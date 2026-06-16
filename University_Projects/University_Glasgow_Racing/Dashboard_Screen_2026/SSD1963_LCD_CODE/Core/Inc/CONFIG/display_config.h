/*
=============
DEFINABLES:
=============
*/
#pragma once 

//forward declarations
enum Screen_State; 
enum TouchMode;

//TESTING OR RELEASE IMPORTANT DEFINES!
#define SCREEN_TEST_MODE 1 //Set to 1 to have the screen keep incrementing all values to test -? SET TO ZERO FOR THE REAL THING
#define CAN_TEST_MODE 0 //set to one to test the CAN callback

#define SEND_SDC_STATE 0 //set to 1 to send the SDC state over CAN
#define USE_ADC_FOR_SCREEN_STATE 0 //set to 1 to use the ADC for screen state, 0 to use the read pin
#define DRAW_LOGO_FROM_SD 0 //set to 1 to draw the big logo from SD card

//starting screen (LOGO, ENDURANCE, PEDAL)
#define STARTING_SCREEN LOGO

#define AUTOMATIC_TRANSITION_FROM_STARTING_SCREEN 1 //set to 1 to automatically transition from logo to endurance to pedal after startup after a short delay, 0 to stay on logo until touch
#define AUTOMATIC_SECOND_SCREEN PEDAL //second screen (LOGO, ENDURANCE, PEDAL)

//TouchMode
#define TOUCH_MODE POLLING
#define GT911_I2C_TIMEOUT_MS  50

//TOUCHSCREEN COOLDOWN BEFORE READINGS ARE ACCEPTED AGAIN
#define TOUCH_COOLDOWN_MS 250

//BRIGHTNESS
#define LCD_BRIGHTNESS 10 // adjust as needed (0-100%)

//ADC VOLTAGE DIVIDERS:
#define ADC_MAX_COUNTS          4095U   // 12-bit ADC

// Adjust these thresholds to match your resistor divider / expected voltages
// Example values for 3.3V ADC:
// 1.0V -> about 1241 counts
// 2.0V -> about 2482 counts
#define STATE_RD_TH_LOW         1241U
#define STATE_RD_TH_HIGH        2482U

// CAN message for SDC / state report
#define CAN_ID_SDC_STATE        0x101
#define CAN_SDC_STATE_DLC       4 //DATA LENGTH CODE


//BROKEN STARTUP TESTING (turned out to be too fast FMC lol)
#define LCD_BOOT_MAX_ATTEMPTS       5
#define LCD_BOOT_RETRY_DELAY_MS     250
#define LCD_FAIL_RETRY_DELAY_MS     3000
#define LCD_USE_READBACK 1 //set 1 to verify LCD is on using the read pin


/*
==============
ENUM CLASSES
=============
*/

//SCREEN STATEs
enum Screen_State {
    ENDURANCE,
    PEDAL,
    LOGO
};

enum TouchMode {
    DISABLED,
    POLLING,
    INTERRUPT
};

//READING STATE ADC
typedef enum
{
    STATE_RD_LEVEL_0 = 0,
    STATE_RD_LEVEL_1 = 1,
    STATE_RD_LEVEL_2 = 2
} StateRdLevel;

//USB REQUESTS
typedef enum {
    SCREEN_REQ_NONE = 0,
    SCREEN_REQ_LOGO,
    SCREEN_REQ_ENDURANCE,
    SCREEN_REQ_PEDAL
} ScreenRequest;