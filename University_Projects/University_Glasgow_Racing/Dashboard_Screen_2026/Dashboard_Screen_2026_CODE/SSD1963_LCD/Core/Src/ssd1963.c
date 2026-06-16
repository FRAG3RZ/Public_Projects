#include "ssd1963.h"
#include "main.h"
#include "gpio.h"
#include "fmc.h"
#include "tim.h"
#include "stm32f7xx_hal.h"
#include "definables.h"

// -----------------------------
// FMC address mapping
// -----------------------------
// Bank1/NE1 base is 0x6000_0000.
// With LCD_RS connected to FMC_A16, the "data" address is typically base + 0x20000 on a 16-bit bus.
//
// If you ever suspect RS is inverted, swap CMD/DATA addresses below.
#define LCD_FMC_BASE   (0x60000000UL)
#define LCD_CMD_ADDR   (LCD_FMC_BASE)
#define LCD_DATA_ADDR  (LCD_FMC_BASE + 0x00020000UL)

static inline void lcd_cmd(uint16_t c)  { *(__IO uint16_t*)LCD_CMD_ADDR  = c; }
static inline void lcd_dat(uint16_t d)  { *(__IO uint16_t*)LCD_DATA_ADDR = d; }

// -----------------------------
// Panel timing constants (from vendor example)
// -----------------------------
#define SSD_HOR_RESOLUTION      800
#define SSD_VER_RESOLUTION      480

#define SSD_HOR_PULSE_WIDTH     1
#define SSD_HOR_BACK_PORCH      46
#define SSD_HOR_FRONT_PORCH     210

#define SSD_VER_PULSE_WIDTH     1
#define SSD_VER_BACK_PORCH      23
#define SSD_VER_FRONT_PORCH     22

#define SSD_HT  (SSD_HOR_RESOLUTION + SSD_HOR_BACK_PORCH + SSD_HOR_FRONT_PORCH) // 1056
#define SSD_HPS (SSD_HOR_BACK_PORCH)                                            // 46
#define SSD_VT  (SSD_VER_RESOLUTION + SSD_VER_BACK_PORCH + SSD_VER_FRONT_PORCH) // 525
#define SSD_VPS (SSD_VER_BACK_PORCH)                                            // 23

// Orientation: vendor example uses MADCTL (0x36). Many panels differ on BGR.
// Start with BGR=0; if colors are swapped (red/blue), set BGR=1.
#define SSD1963_BGR 0

static void ssd_write_reg8(uint16_t reg, uint8_t val)
{
    lcd_cmd(reg);
    lcd_dat(val);
}

static void ssd_write_reg(uint16_t reg, const uint8_t* data, uint32_t n)
{
    lcd_cmd(reg);
    for (uint32_t i = 0; i < n; i++) lcd_dat(data[i]);
}

static void ssd_soft_reset(void)
{
    lcd_cmd(0x01);
    HAL_Delay(10);
}

// Set column/page address + memory write
void SSD1963_SetWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    // 0x2A: column address set
    lcd_cmd(0x2A);
    lcd_dat((x0 >> 8) & 0xFF);
    lcd_dat(x0 & 0xFF);
    lcd_dat((x1 >> 8) & 0xFF);
    lcd_dat(x1 & 0xFF);

    // 0x2B: page address set
    lcd_cmd(0x2B);
    lcd_dat((y0 >> 8) & 0xFF);
    lcd_dat(y0 & 0xFF);
    lcd_dat((y1 >> 8) & 0xFF);
    lcd_dat(y1 & 0xFF);

    // 0x2C: memory write
    lcd_cmd(0x2C);
}

void SSD1963_Fill(uint16_t rgb565)
{
    SSD1963_SetWindow(0, 0, SSD_HOR_RESOLUTION - 1, SSD_VER_RESOLUTION - 1);

    const uint32_t pixels = (uint32_t)SSD_HOR_RESOLUTION * (uint32_t)SSD_VER_RESOLUTION;
    for (uint32_t i = 0; i < pixels; i++)
    {
        // 16-bit 565 on 16-bit parallel bus
        *(__IO uint16_t*)LCD_DATA_ADDR = rgb565;
    }
}

// -----------------------------
// Tiny "gfx" helpers (RGB565)
// -----------------------------

void SSD1963_DrawPixel(uint16_t x, uint16_t y, uint16_t rgb565)
{
    if (x >= SSD_HOR_RESOLUTION || y >= SSD_VER_RESOLUTION) return;
    SSD1963_SetWindow(x, y, x, y);
    *(__IO uint16_t*)LCD_DATA_ADDR = rgb565;
}

void SSD1963_DrawHLine(uint16_t x, uint16_t y, uint16_t w, uint16_t rgb565)
{
    if (y >= SSD_VER_RESOLUTION || x >= SSD_HOR_RESOLUTION) return;
    if (x + w > SSD_HOR_RESOLUTION) w = (uint16_t)(SSD_HOR_RESOLUTION - x);
    if (w == 0) return;
    SSD1963_SetWindow(x, y, (uint16_t)(x + w - 1), y);
    for (uint32_t i = 0; i < w; i++) *(__IO uint16_t*)LCD_DATA_ADDR = rgb565;
}

void SSD1963_DrawVLine(uint16_t x, uint16_t y, uint16_t h, uint16_t rgb565)
{
    if (x >= SSD_HOR_RESOLUTION || y >= SSD_VER_RESOLUTION) return;
    if (y + h > SSD_VER_RESOLUTION) h = (uint16_t)(SSD_VER_RESOLUTION - y);
    if (h == 0) return;
    SSD1963_SetWindow(x, y, x, (uint16_t)(y + h - 1));
    for (uint32_t i = 0; i < h; i++) *(__IO uint16_t*)LCD_DATA_ADDR = rgb565;
}

void SSD1963_FillRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t rgb565)
{
    if (x >= SSD_HOR_RESOLUTION || y >= SSD_VER_RESOLUTION) return;
    if (x + w > SSD_HOR_RESOLUTION) w = (uint16_t)(SSD_HOR_RESOLUTION - x);
    if (y + h > SSD_VER_RESOLUTION) h = (uint16_t)(SSD_VER_RESOLUTION - y);
    if (w == 0 || h == 0) return;

    SSD1963_SetWindow(x, y, (uint16_t)(x + w - 1), (uint16_t)(y + h - 1));
    const uint32_t pixels = (uint32_t)w * (uint32_t)h;
    for (uint32_t i = 0; i < pixels; i++) *(__IO uint16_t*)LCD_DATA_ADDR = rgb565;
}

void SSD1963_WritePixels(const uint16_t *px, uint32_t count)
{
    volatile uint16_t *dst = (volatile uint16_t*)LCD_DATA_ADDR;
    for (uint32_t i = 0; i < count; i++) {
        *dst = px[i];
    }
}

void SSD1963_TestColorBars(void)
{
    // 8 vertical bars (classic)
    const uint16_t colors[8] = {
        RGB565(255,255,255), // white
        RGB565(255,255,0),   // yellow
        RGB565(0,255,255),   // cyan
        RGB565(0,255,0),     // green
        RGB565(255,0,255),   // magenta
        RGB565(255,0,0),     // red
        RGB565(0,0,255),     // blue
        RGB565(0,0,0)        // black
    };

    const uint16_t bar_w = (uint16_t)(SSD_HOR_RESOLUTION / 8);
    for (uint16_t i = 0; i < 8; i++) {
        const uint16_t x = (uint16_t)(i * bar_w);
        const uint16_t w = (i == 7) ? (uint16_t)(SSD_HOR_RESOLUTION - x) : bar_w;
        SSD1963_FillRect(x, 0, w, SSD_VER_RESOLUTION, colors[i]);
    }
}

void SSD1963_TestCheckerboard(uint16_t tile)
{
    if (tile == 0) tile = 16;
    for (uint16_t y = 0; y < SSD_VER_RESOLUTION; y += tile) {
        for (uint16_t x = 0; x < SSD_HOR_RESOLUTION; x += tile) {
            const uint16_t w = (x + tile > SSD_HOR_RESOLUTION) ? (uint16_t)(SSD_HOR_RESOLUTION - x) : tile;
            const uint16_t h = (y + tile > SSD_VER_RESOLUTION) ? (uint16_t)(SSD_VER_RESOLUTION - y) : tile;
            const uint16_t c = (((x / tile) ^ (y / tile)) & 1) ? RGB565(30,30,30) : RGB565(220,220,220);
            SSD1963_FillRect(x, y, w, h, c);
        }
    }
}

static void ssd_set_madctl_landscape(void)
{
    // Vendor example maps "USE_HORIZONTAL=1" to MADCTL value 0x00 (with their setup).
    // We add optional BGR bit (bit3).
    uint8_t madctl = 0x00;
    if (SSD1963_BGR) madctl |= (1u << 3);
    ssd_write_reg8(0x36, madctl);
}

void SSD1963_Init(void)
{
    /*
     * Full init with hardware reset.
     * Use this only when you want SSD1963_Init() to own the reset.
     */
    HAL_GPIO_WritePin(LCD_RESET_GPIO_Port, LCD_RESET_Pin, GPIO_PIN_RESET);
    HAL_Delay(100);

    HAL_GPIO_WritePin(LCD_RESET_GPIO_Port, LCD_RESET_Pin, GPIO_PIN_SET);
    HAL_Delay(300);

    SSD1963_InitNoReset();
}

void SSD1963_InitNoReset(void)
{
    /*
     * SSD1963 command init only.
     * Do NOT toggle LCD_RESET in this function.
     */

    /*
     * 0xE2: PLL configuration.
     * Use 0x54, not 0x04, for the third byte.
     */
    {
        const uint8_t pll[] = {
            0x1D,
            0x02,
            0x54
        };
        ssd_write_reg(0xE2, pll, sizeof(pll));
    }

    HAL_Delay(5);

    /*
     * 0xE0: start PLL, then lock/use PLL.
     */
    ssd_write_reg8(0xE0, 0x01);
    HAL_Delay(10);

    ssd_write_reg8(0xE0, 0x03);
    HAL_Delay(20);

    ssd_soft_reset();
    HAL_Delay(20);

    /*
     * 0xE6: pixel clock.
     */
    {
        const uint8_t pclk[] = { 0x03, 0xFF, 0xFF };
        ssd_write_reg(0xE6, pclk, sizeof(pclk));
    }

    /*
     * 0xB0: LCD mode.
     */
    {
        uint8_t b0[] = {
            0x20,
            0x00,
            (uint8_t)((SSD_HOR_RESOLUTION - 1) >> 8),
            (uint8_t)((SSD_HOR_RESOLUTION - 1) & 0xFF),
            (uint8_t)((SSD_VER_RESOLUTION - 1) >> 8),
            (uint8_t)((SSD_VER_RESOLUTION - 1) & 0xFF),
            0x00
        };
        ssd_write_reg(0xB0, b0, sizeof(b0));
    }

    /*
     * 0xB4: horizontal period.
     */
    {
        uint8_t b4[] = {
            (uint8_t)((SSD_HT - 1) >> 8),
            (uint8_t)((SSD_HT - 1) & 0xFF),
            (uint8_t)(SSD_HPS >> 8),
            (uint8_t)(SSD_HPS & 0xFF),
            (uint8_t)(SSD_HOR_PULSE_WIDTH - 1),
            0x00,
            0x00,
            0x00
        };
        ssd_write_reg(0xB4, b4, sizeof(b4));
    }

    /*
     * 0xB6: vertical period.
     * Fifth byte is pulse width - 1.
     */
    {
        uint8_t b6[] = {
            (uint8_t)((SSD_VT - 1) >> 8),
            (uint8_t)((SSD_VT - 1) & 0xFF),
            (uint8_t)(SSD_VPS >> 8),
            (uint8_t)(SSD_VPS & 0xFF),
            (uint8_t)(SSD_VER_PULSE_WIDTH - 1),
            0x00,
            0x00
        };
        ssd_write_reg(0xB6, b6, sizeof(b6));
    }

    /*
     * 0xF0: set host pixel interface to 16-bit RGB565.
     */
    ssd_write_reg8(0xF0, 0x03);

    /*
     * MADCTL orientation.
     */
    ssd_set_madctl_landscape();

    /*
     * Disable DBC.
     */
    ssd_write_reg8(0xD0, 0x00);

    /*
     * SSD1963 GPIO config.
     */
    {
        uint8_t b8[] = { 0x03, 0x01 };
        ssd_write_reg(0xB8, b8, sizeof(b8));
    }

    ssd_write_reg8(0xBA, 0x01);

    /*
     * Display ON last.
     */
    lcd_cmd(0x29);
    HAL_Delay(10);

    __DSB();
    __ISB();
}

void SSD1963_Force16BitPixelInterface(void)
{
    /*
     * SSD1963 0xF0:
     * 0x03 = 16-bit RGB565 host pixel interface.
     */
    lcd_cmd(0xF0);
    lcd_dat(0x03);

    __DSB();
    __ISB();

    HAL_Delay(2);
}

static uint16_t lcd_read16_raw(void)
{
    uint16_t v;

    __DSB();
    v = *(__IO uint16_t *)LCD_DATA_ADDR;
    __DSB();

    return v;
}

typedef enum
{
    LCD_READ_LANE_LOW = 0,
    LCD_READ_LANE_HIGH = 1
} LCD_ReadLane;

static LCD_ReadLane lcd_read_lane = LCD_READ_LANE_LOW;

static uint8_t lcd_extract8(uint16_t raw)
{
    if (lcd_read_lane == LCD_READ_LANE_HIGH)
        return (uint8_t)(raw >> 8);

    return (uint8_t)(raw & 0xFF);
}

static uint8_t SSD1963_ReadDDB(uint8_t ddb[5])
{
    uint16_t raw[6];

    lcd_cmd(0xA1);
    __DSB();

    for (uint32_t i = 0; i < 5; i++)
        raw[i] = lcd_read16_raw();

    if (((raw[0] & 0xFF) == 0x01) &&
        ((raw[1] & 0xFF) == 0x57) &&
        ((raw[2] & 0xFF) == 0x61))
    {
        lcd_read_lane = LCD_READ_LANE_LOW;

        for (uint32_t i = 0; i < 5; i++)
            ddb[i] = (uint8_t)(raw[i] & 0xFF);

        return 1;
    }

    if (((raw[0] >> 8) == 0x01) &&
        ((raw[1] >> 8) == 0x57) &&
        ((raw[2] >> 8) == 0x61))
    {
        lcd_read_lane = LCD_READ_LANE_HIGH;

        for (uint32_t i = 0; i < 5; i++)
            ddb[i] = (uint8_t)(raw[i] >> 8);

        return 1;
    }

    /*
     * Retry with one dummy read.
     */
    lcd_cmd(0xA1);
    __DSB();

    (void)lcd_read16_raw();

    for (uint32_t i = 0; i < 5; i++)
        raw[i] = lcd_read16_raw();

    if (((raw[0] & 0xFF) == 0x01) &&
        ((raw[1] & 0xFF) == 0x57) &&
        ((raw[2] & 0xFF) == 0x61))
    {
        lcd_read_lane = LCD_READ_LANE_LOW;

        for (uint32_t i = 0; i < 5; i++)
            ddb[i] = (uint8_t)(raw[i] & 0xFF);

        return 1;
    }

    if (((raw[0] >> 8) == 0x01) &&
        ((raw[1] >> 8) == 0x57) &&
        ((raw[2] >> 8) == 0x61))
    {
        lcd_read_lane = LCD_READ_LANE_HIGH;

        for (uint32_t i = 0; i < 5; i++)
            ddb[i] = (uint8_t)(raw[i] >> 8);

        return 1;
    }

    return 0;
}

static uint8_t SSD1963_ReadReg8(uint16_t cmd)
{
    lcd_cmd(cmd);
    __DSB();

    return lcd_extract8(lcd_read16_raw());
}

static uint16_t SSD1963_ReadReg16(uint16_t cmd)
{
    uint8_t hi;
    uint8_t lo;

    lcd_cmd(cmd);
    __DSB();

    hi = lcd_extract8(lcd_read16_raw());
    lo = lcd_extract8(lcd_read16_raw());

    return ((uint16_t)hi << 8) | lo;
}

void SSD1963_DisplayOn(void)
{
    lcd_cmd(0x29);
    __DSB();
    __ISB();
    HAL_Delay(20);
}

uint8_t SSD1963_VerifyBasic(void)
{
    uint8_t ddb[5] = {0};
    uint8_t power_mode;
    uint8_t pll_status;
    uint8_t pixel_if;
    uint16_t scan1;
    uint16_t scan2;

    /*
     * First prove that reads actually work.
     * Expected: 01 57 61 xx FF
     */
    if (!SSD1963_ReadDDB(ddb))
    {
        return 0;
    }

    /*
     * GET_POWER_MODE.
     * We want sleep off, normal display mode, display on.
     */
    power_mode = SSD1963_ReadReg8(0x0A);

    if ((power_mode & 0x1C) != 0x1C)
    {
        return 0;
    }

    /*
     * GET_PLL_STATUS.
     * Common SSD1963 code checks bit 2 for PLL lock.
     */
    pll_status = SSD1963_ReadReg8(0xE4);

    if ((pll_status & 0x04) == 0)
    {
        return 0;
    }

    /*
     * GET_PIXEL_DATA_INTERFACE.
     * 0x03 = 16-bit 565 host interface.
     */
    pixel_if = SSD1963_ReadReg8(0xF1);

    if ((pixel_if & 0x07) != 0x03)
    {
        return 0;
    }

    /*
     * GET_SCANLINE.
     * If scanline changes, display timing is probably running.
     */
    scan1 = SSD1963_ReadReg16(0x45);
    HAL_Delay(20);
    scan2 = SSD1963_ReadReg16(0x45);

    if (scan1 == scan2)
    {
        return 0;
    }

    return 1;
}

void LCD_ControllerRebootAtStartup(void)
{
    LCD_SetBrightness(0);

    /*
     * FMC is configured before this function is called.
     * Reset the LCD controller, then send one clean SSD1963 init sequence.
     */
    HAL_GPIO_WritePin(LCD_RESET_GPIO_Port, LCD_RESET_Pin, GPIO_PIN_RESET);
    HAL_Delay(1000);

    HAL_GPIO_WritePin(LCD_RESET_GPIO_Port, LCD_RESET_Pin, GPIO_PIN_SET);
    HAL_Delay(1200);

    SSD1963_InitNoReset();
    SSD1963_Force16BitPixelInterface();

    SSD1963_DisplayOn();
    SSD1963_Fill(0x0000);

    __DSB();
    __ISB();

    LCD_SetBrightness(LCD_BRIGHTNESS);
}

void LCD_EarlyPinHold_NoHAL(void)
{
    /*
     * This function intentionally does not use HAL.
     * It is safe to call before HAL_Init().
     *
     * Goal:
     * - Assert LCD_RESET low as early as possible after MCU NRST.
     * - Hold LCD_RD, LCD_WR, LCD_CS inactive high.
     * - Bias RS/DC and data bus while FMC is not configured.
     *
     * Pins:
     * PC5  = LCD_RESET
     * PD4  = LCD_RD / FMC_NOE
     * PD5  = LCD_WR / FMC_NWE
     * PD7  = LCD_CS / FMC_NE1
     * PD11 = LCD_RS / FMC_A16
     */

    /* Enable GPIOC, GPIOD, GPIOE clocks */
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN |
                    RCC_AHB1ENR_GPIODEN |
                    RCC_AHB1ENR_GPIOEEN;
    __DSB();

    /*
     * PC5 = LCD_RESET.
     * Set output latch low first, then make it output.
     */
    GPIOC->BSRR = ((uint32_t)GPIO_PIN_5 << 16U);   // PC5 low

    GPIOC->MODER &= ~(3UL << (5U * 2U));
    GPIOC->MODER |=  (1UL << (5U * 2U));           // output

    GPIOC->OTYPER &= ~GPIO_PIN_5;                  // push-pull

    GPIOC->OSPEEDR &= ~(3UL << (5U * 2U));         // low speed

    GPIOC->PUPDR &= ~(3UL << (5U * 2U));
    GPIOC->PUPDR |=  (2UL << (5U * 2U));           // pulldown


    /*
     * PD4/PD5/PD7 = RD/WR/CS.
     * Drive inactive high immediately.
     */

    GPIOD->BSRR = GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_7;

    /* Clear mode bits */
    GPIOD->MODER &= ~((3UL << (4U * 2U)) |
                      (3UL << (5U * 2U)) |
                      (3UL << (7U * 2U)));

    /* Set output mode */
    GPIOD->MODER |=  ((1UL << (4U * 2U)) |
                      (1UL << (5U * 2U)) |
                      (1UL << (7U * 2U)));

    /* Push-pull */
    GPIOD->OTYPER &= ~(GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_7);

    /* Low speed */
    GPIOD->OSPEEDR &= ~((3UL << (4U * 2U)) |
                        (3UL << (5U * 2U)) |
                        (3UL << (7U * 2U)));

    /* Pull-up */
    GPIOD->PUPDR &= ~((3UL << (4U * 2U)) |
                      (3UL << (5U * 2U)) |
                      (3UL << (7U * 2U)));

    GPIOD->PUPDR |=  ((1UL << (4U * 2U)) |
                      (1UL << (5U * 2U)) |
                      (1UL << (7U * 2U)));


    /*
     * PD11 = RS/DC.
     * Input pulldown until FMC owns it.
     */
    GPIOD->MODER &= ~(3UL << (11U * 2U));          // input

    GPIOD->PUPDR &= ~(3UL << (11U * 2U));
    GPIOD->PUPDR |=  (2UL << (11U * 2U));          // pulldown


    /*
     * Optional: weakly bias LCD data bus low before FMC owns it.
     *
     * GPIOD:
     * PD0, PD1, PD8, PD9, PD10, PD14, PD15
     */
    const uint32_t pd_data =
        GPIO_PIN_0 | GPIO_PIN_1 |
        GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 |
        GPIO_PIN_14 | GPIO_PIN_15;

    for (uint32_t pin = 0; pin < 16; pin++)
    {
        uint32_t mask = (1UL << pin);

        if (pd_data & mask)
        {
            GPIOD->MODER &= ~(3UL << (pin * 2U));  // input

            GPIOD->PUPDR &= ~(3UL << (pin * 2U));
            GPIOD->PUPDR |=  (2UL << (pin * 2U));  // pulldown
        }
    }

    /*
     * GPIOE data:
     * PE7..PE15
     */
    for (uint32_t pin = 7; pin <= 15; pin++)
    {
        GPIOE->MODER &= ~(3UL << (pin * 2U));      // input

        GPIOE->PUPDR &= ~(3UL << (pin * 2U));
        GPIOE->PUPDR |=  (2UL << (pin * 2U));      // pulldown
    }

    __DSB();
    __ISB();
}
