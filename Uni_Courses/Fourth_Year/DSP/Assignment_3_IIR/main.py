import numpy as np
import scipy.signal as signal
import time
import os

# Import for game control
import pyautogui

from IIR_filter import DirectFormII, IIRFilter

Fs = 1000  # Sampling frequency of the Arduino
max_iteration_time = 1 / Fs  # Maximum allowed time per iteration



def main():

    # ======= STEP 1: Generate IIR Coefficients =======

    # Generate the SOS coefficients for 50 Hz removal
    # Make sure to convert the frequency to Nyquist normalization
    sos = signal.butter(2, [45 / Fs * 2, 55 / Fs * 2], btype='bandstop', fs=Fs, output='sos')

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

    while True:



        #distance_cm = read_distance_from_arduino()  # Replace with your actual function to read from Arduino

        # =============== Game Control ================
        # Map 10–50 cm onto screen width
        fraction = max(0, min(1, (distance_cm - 10) / 40))
        x = int(fraction * (pyautogui.size().width - 1))

        pyautogui.moveTo(x, 700)



if __name__ == "__main__":
    main()