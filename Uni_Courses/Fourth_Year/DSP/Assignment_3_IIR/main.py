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

arduino_Fs = 1000  # Sampling frequency of the Arduino
sampling_interval = 1 / arduino_Fs  # Maximum allowed time per iteration

# Create an instance of the Arduino
PORT =  pyfirmata2.Arduino.AUTODETECT
board = pyfirmata2.Arduino(PORT)

# Setup the Arduino Pins for the Ultrasonic
trigger_pin = board.get_pin('d:9:o')
echo_pin = board.get_pin('d:10:i')

echo_pin.register_callback(myCallback)
echo_pin.enable_reporting()

# Interval in miliseconds
board.samplingOn(sampling_interval * 1000)

def read_voltage_from_arduino():

    voltage = 0
    return voltage

def main():

    # ======= STEP 1: Generate IIR Coefficients =======

    # Generate the SOS coefficients for 50 Hz removal
    # Make sure to convert the frequency to Nyquist normalization
    sos = signal.butter(2, [45 / arduino_Fs * 2, 55 / arduino_Fs * 2], btype='bandstop', output='sos')

    # ======= STEP 2: Create Master IIR Filter to Hold the SOS chain =======
    
    arduino_IIR_Filter = IIRFilter(filters=[])  # Create an instance of the master IIR filter

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

    # ============= Setup the Watchdog ================   

    watchdog = Watchdog(watchdog_maximum_time_s=max_sec_per_iteration)

    # Start watchdog monitoring on a separate thread -> makes sure watchdog is fully separate from main
    watchdog_thread = threading.Thread(
        target=watchdog.monitor_watchdog, # This is the function which runs on the separate thread
        daemon=True # Set this to be a background process, aka a Daemon
    )
    watchdog_thread.start()

    while True:

        # First sample the Arduino
        arduino_raw_voltage = read_voltage_from_arduino() 

        # Filtered voltage from arduino
        filtered_voltage = arduino_IIR_Filter.dofilter(arduino_raw_voltage)

        """
        # =============== Game Control ================
        # Map 10–50 cm onto screen width
        fraction = max(0, min(1, (distance_cm - 10) / 40))
        x = int(fraction * (pyautogui.size().width - 1))

        pyautogui.moveTo(x, 700)
        """

        # At the end of each iteration, "pet" the watchdog :D
        watchdog.pet_the_watchdog()



if __name__ == "__main__":
    main()