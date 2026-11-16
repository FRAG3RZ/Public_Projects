import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import time
import os

# This is for Arduino Control
import pyfirmata2

# Import our own Watchdog class and the threading for starting the Watchdog in its own thread
import threading
from watchdog import Watchdog

# Import for game control
import pyautogui

# Import our own IIR Filter classes
from IIR_filter import DirectFormII, IIRFilter

# Reuse our CircularBuffer class from Assignment 2 to use as the buffer for incomming data
from CircularBuffer import CircularBuffer


# ====================== IMPORTANT DEFINES =======================

arduino_Fs = 1000  # Sampling frequency of the Arduino
sampling_interval = 1 / arduino_Fs

# Create an instance of the Arduino
PORT =  pyfirmata2.Arduino.AUTODETECT
board = pyfirmata2.Arduino(PORT)

# ========================= DATA STORAGE =============================

# Use a dictionary to store the arduino filters
# Instead of filters[0] we can call filters["x"], which makes it more clear
arduino_IIR_Filters = {
    "x": IIRFilter(filters=[]),
    "y": IIRFilter(filters=[]),
    "z": IIRFilter(filters=[])
}

axes_names = ["x", "y", "z"]

# Store the most recent x samples of each signal
# At 1000 Hz, 5000 samples correspond to approximately 5 seconds
recent_sample_count = 5000

# Use our own CircularBuffer class to keep only the latest samples!
# Good use of pre-written and proofed code! :D
raw_data = {axis: CircularBuffer(recent_sample_count) for axis in axes_names}
filtered_data = {axis: CircularBuffer(recent_sample_count) for axis in axes_names}
time_data = {axis: CircularBuffer(recent_sample_count) for axis in axes_names}

# Prevent plotting and Arduino callbacks from accessing buffers simultaneously
# When data is being updated, don't use it for plotting!
# When plotting the data, don't update it!
# This is a shared "flag" of sorts between the main thread and the callback
data_lock = threading.Lock()

# =================== PLOTTING PREPARATION ===================

# Create one window with 3 rows and 2 columns of graphs
# Left column: raw X, Y, Z
# Right column: filtered X, Y, Z
fig, axes = plt.subplots(3, 2, figsize=(12, 8))

# Store the lines so we can update their data later
raw_lines = {}
filtered_lines = {}

# Create one empty raw and filtered graph for each IMU axis
# Label the graphs and enable grid
# Enumerate gives back for the axes_names as well as their index "i"
for i, axis in enumerate(axes_names):

    # Create an empty line on each graph
    raw_lines[axis], = axes[i, 0].plot([])
    filtered_lines[axis], = axes[i, 1].plot([])

    # Add graph titles
    axes[i, 0].set_title(f"{axis.upper()} - Raw")
    axes[i, 1].set_title(f"{axis.upper()} - Filtered")

    # Y-axis is voltage -> callback scales the normalized ADC output into voltage using VREF = 5.0V
    axes[i, 0].set_ylabel("Voltage (V)")
    axes[i, 1].set_ylabel("Voltage (V)")

    # X axis will be converted to time in update_plots instead of samples
    axes[i, 0].set_xlabel("Time (s)")
    axes[i, 1].set_xlabel("Time (s)")

    # Show a grid on both graphs
    axes[i, 0].grid()
    axes[i, 1].grid()

plt.tight_layout()

# Create a function which we can continuously call to update the graphs
def update_plots():

    # Update the raw and filtered graphs for each IMU axis
    for i, axis in enumerate(axes_names):

        # Retrieve the samples in chronological order from our circular buffers
        # Prevent the Arduino callback from modifying the buffers while we read them
        with data_lock:
            raw = raw_data[axis].get_samples()
            filtered = filtered_data[axis].get_samples()
            timestamps = time_data[axis].get_samples()

        # Avoid running this when there are no samples yet
        if len(timestamps) == 0:
            continue

        # Convert timestamps to seconds relative to the current time
        current_time = time.perf_counter()
        time_axis = [t - current_time for t in timestamps]

        # Update the raw and filtered plot lines
        raw_lines[axis].set_data(time_axis, raw)
        filtered_lines[axis].set_data(time_axis, filtered)

        # Display the last 5 seconds, with 0 representing the current time
        # Makes the plot visibility nicer
        axes[i, 0].set_xlim(-5, 0)
        axes[i, 1].set_xlim(-5, 0)

        # Adjust the vertical axes to fit the latest readings
        axes[i, 0].relim()
        axes[i, 0].autoscale_view(scalex=False)

        axes[i, 1].relim()
        axes[i, 1].autoscale_view(scalex=False)


# ============================== MAIN ================================

def main():

    # ======= STEP 1: Generate IIR Coefficients =======

    # Generate the SOS coefficients for 50 Hz removal
    # Make sure to convert the frequency to Nyquist normalization
    sos_50Hz = signal.butter(2, [45 / arduino_Fs * 2, 55 / arduino_Fs * 2], btype='bandstop', output='sos')

    # Remove DC for matched filter usage -> use a highpass
    sos_DC = signal.butter(2, (0.5 / arduino_Fs * 2), btype='highpass', output='sos')

    # Combine the different filters into one SOS matrix
    # Combine the matrices vertically using np.vertical stack
    sos = np.vstack((sos_DC, sos_50Hz))

    # ======= STEP 2: Create Master IIR Filter to Hold the SOS chain =======
    
    # Already use the global instances
    # Need three filters for X,Y and Z axis
    global arduino_IIR_Filters  

    # ======= STEP 3: Fill the Main Filters with Individual 2nd order Filter Instances =======

    # 2.2 Direct Form II Filter in Python 
    for axis in arduino_IIR_Filters:
        for second_order_filter in sos:
            b = second_order_filter[:3] # FIR coefficients are the first three
            a = second_order_filter[3:] # IIR coefficients are the last three

            # Create an instance of the DirectFormII filter
            df2_filter = DirectFormII(b, a)

            # Add the filter instance to the master IIR filter
            arduino_IIR_Filters[axis].filters.append(df2_filter)

    # ======= STEP 4: Sample the Arduino Signal and Apply the Filter =======

    # Setup the Arduino Pins
    IMU_pins = {
        "x": board.get_pin('a:0:i'),
        "y": board.get_pin('a:1:i'),
        "z": board.get_pin('a:2:i')
    }

    # ======= Start the Watchdog =======
    
    global watchdog
    watchdog = Watchdog(samples_per_second=arduino_Fs * 3, # Multiplied by three because we're expecting three callbacks from X, Y and Z 
                        time_individual_callback=False)

    # Start watchdog monitoring on a separate thread -> makes sure watchdog is fully separate from main
    watchdog_thread = threading.Thread(
        target=watchdog.monitor_watchdog, # This is the function which runs on the separate thread
        daemon=True # Set this to be a background process, aka a Daemon
    )
    watchdog_thread.start()

    # Register the callbacks -> Need three ways to call our one universal ccallback
    # Need to use .items() for Python to return BOTH the keys and the associated values
    for axis, pin in IMU_pins.items():

        # Register the correct callback based on the axis
        pin.register_callback(
            # Use a lambda function here to create an arbitrary function which just calls the callback function with our parameters
            lambda voltage, axis=axis: Arduino_Data_Ready(voltage, axis)
        )
        pin.enable_reporting()

    # Interval in miliseconds
    board.samplingOn(sampling_interval * 1000)

    # Enables interactive plotting
    plt.ion() 

    # Open the graph window without stopping the Python program
    plt.show(block=False)
    
    try:
        # Keep updating until the user closes the graph window
        # Main running WHILE loop!
        while plt.fignum_exists(fig.number):

            # Stop the program if the watchdog detects a problem
            if watchdog.expired.is_set():
                raise TimeoutError("Watchdog expired!")

            # Update the six graphs with the latest Arduino samples
            update_plots()

            # Allow Matplotlib to redraw and process window events
            plt.pause(0.05)

    finally:
        # Close the Arduino connection when the program finishes
        board.exit()

        
def Arduino_Data_Ready(voltage, axis):

    # Start the callback watchdog 
    watchdog.pet_watchdog_on_callback_start()

    # Read and store the raw voltage
    # Arduino returns a normalized ADC reading between 0 - 1, need to scale to VREF = 5V
    arduino_raw_voltage = voltage * 5.0 

    # Calculate and store the right voltage as per X, Y or Z
    filtered_voltage = arduino_IIR_Filters[axis].dofilter(arduino_raw_voltage)

    # ==== Update the real-time plotting ====

    # Write the raw, filtered and timestamp values together
    # ---> use the data_lock to make sure that the plotting in the Main thread doesn't read the data during writting
    # useful from the "threading" library!
    with data_lock:
        raw_data[axis].append(arduino_raw_voltage)
        filtered_data[axis].append(filtered_voltage)
        time_data[axis].append(time.perf_counter())

    # Apply the matched filter here: 

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