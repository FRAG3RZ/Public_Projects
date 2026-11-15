import numpy as np
import scipy.signal as signal
import time
import os

# This is for Arduino Control
import pyfirmata2

# Import for Watchdog and Hyperthreading
import threading
from watchdog import Watchdog

# Import for game control
import pyautogui

from IIR_filter import DirectFormII, IIRFilter

# ====================== IMPORTANT DEFINES =======================

arduino_Fs = 1000  # Sampling frequency of the Arduino
sampling_interval = 1 / arduino_Fs

arduino_IIR_Filter = IIRFilter(filters=[])

# Create an instance of the Arduino
PORT =  pyfirmata2.Arduino.AUTODETECT
board = pyfirmata2.Arduino(PORT)


def main():

    # ======= STEP 1: Generate IIR Coefficients =======

    # Generate the SOS coefficients for 50 Hz removal
    # Make sure to convert the frequency to Nyquist normalization
    sos = signal.butter(2, [45 / arduino_Fs * 2, 55 / arduino_Fs * 2], btype='bandstop', output='sos')

    # ======= STEP 2: Create Master IIR Filter to Hold the SOS chain =======
    
    global arduino_IIR_Filter  # Already use the global instance

    # ======= STEP 3: Fill the Main Filters with Individual 2nd order Filter Instances =======

    # 2.2 Direct Form II Filter in Python
    for second_order_filter in sos:
        b = second_order_filter[:3]  # FIR coefficients are the first three
        a = second_order_filter[3:]  # IIR coefficients are the last three

        # Create an instance of the DirectFormII filter
        df2_filter = DirectFormII(b, a)

        # Add the filter instance to the master IIR filter
        arduino_IIR_Filter.filters.append(df2_filter)


    # ======= STEP 4: Sample the Arduino Signal and Apply the Filter =======

    # Setup the Arduino Pins
    analog_in_0 = board.get_pin('a:0:i')
    analog_in_0.register_callback(Arduino_Data_Ready)
    

    # ======= Start the Watchdog =======

    global watchdog
    watchdog = Watchdog(samples_per_second=arduino_Fs, time_individual_callback=False)

    # Start watchdog monitoring on a separate thread -> makes sure watchdog is fully separate from main
    watchdog_thread = threading.Thread(
        target=watchdog.monitor_watchdog, # This is the function which runs on the separate thread
        daemon=True # Set this to be a background process, aka a Daemon
    )
    watchdog_thread.start()

    # Interval in miliseconds
    analog_in_0.enable_reporting()
    board.samplingOn(sampling_interval * 1000)


    # Make the main run only if the watchdog allows it
    # If watchdog flags an error, exit the program
    try:
        while True:
            if watchdog.expired.is_set():
                raise TimeoutError("Watchdog expired!")

            time.sleep(0.01)

    finally:
        board.exit()

        
def Arduino_Data_Ready(voltage):

    # Pet the watchdog
    watchdog.pet_watchdog_on_callback_start()

    # First sample the Arduino
    arduino_raw_voltage = voltage

    # Filtered voltage from arduino
    filtered_voltage = arduino_IIR_Filter.dofilter(arduino_raw_voltage)


    # ==== Update the real-time plotting ====


    # ====== Control the game ======

    """
    # =============== Game Control ================
    # Map 10–50 cm onto screen width
    fraction = max(0, min(1, (distance_cm - 10) / 40))
    x = int(fraction * (pyautogui.size().width - 1))

    pyautogui.moveTo(x, 700)
    """

    # End of Callback
    watchdog.end_of_callback()



if __name__ == "__main__":
    main()