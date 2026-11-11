import sys
import platform
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt
import time
import os
import statistics

# This will be used to run a "watchdog" in a separate thread
import threading

# Our own filters
from IIR_filter import DirectFormI, DirectFormII, IIRFilter

Arduiono_Fs = 1000  # Sampling frequency of the Arduino
max_iteration_time = 1 / Arduiono_Fs  # Maximum allowed time per iteration

# Make sure the proper output path is used
path_to_files = ""
path_to_output = "Output_Files/"

def Load_ECG_Data(name_of_file):
    """
    Use NumPy to read the ECG .tsv files and output an array
    """

    # Use the global path to files for an organized directory
    global path_to_files

    # first load the data as a text
    # ignore comments and data separators
    data = np.loadtxt(path_to_files + name_of_file, delimiter="\t", comments="#")

    # Extract time and ECG (time is first column, Channel 2 data is 8th)
    # Both are one-dimensional arrays
    time = data[:, 0]
    ecg = data[:, 8]

    # Convert to miliVolts
    ecg *= 1000

    sampling_frequency_Hz = 1 / (time[1] - time[0]) # Use Fs = 1 / deltaT 

    return time, ecg, sampling_frequency_Hz

# ===========================
# === Plotting Functions ====
# ===========================

def plot_time_domain(data_array, time_axis, name_of_plot, show_plot=True, y_label='Voltage (mV)', path_to_output=path_to_output):
    """ 
    Plots the time domain of a signal using its array
    """
    
    # Plotting time domain - assume that the ECG data already contains a time axis 
    plt.plot(time_axis, data_array)
    plt.title(f'{name_of_plot}')
    plt.xlabel('Time (s)')
    plt.ylabel(y_label)
    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '.svg') # Save as an SVG
    if show_plot:
        plt.show()
    plt.close()

def plot_frequency_domain(fft, frequency_axis, samplerate, name_of_plot, show_plot=True, normalize=True, y_label='Voltage (mV)', path_to_output=path_to_output):
    """
    Plots the frequency domain of a signal using its array
    """

    # We used this normalization in the audio assignment, keep the option for now
    if normalize:
        fft = fft / len(fft)

    # FFT is done in voltage
    fft_voltage = np.abs(fft)
    
    # Plotting frequency domain
    plt.plot(frequency_axis, fft_voltage)
    plt.ylabel(y_label)
    plt.title(f'{name_of_plot}')
    plt.xlabel('Frequency (Hz)')

    # plt.xscale('log') Optionally could log scale X-axis, but the x range isn't large for ECG data

    # Cutt off the mirror frequencies (above Fs / 2)
    # Use plot negative frequencies so the DC bin is visible
    plt.xlim(-3, samplerate / 2) # If using Log on the x-axis, Log can't start at 0 so use 1

    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '.svg') # Save as an SVG
    if show_plot:
        plt.show()
    plt.close()


def benchmark(filter_instance, ecg, Signal_bits = None, repetitions=100):
    execution_times = []

    for _ in range(repetitions):

        start = time.perf_counter()

        if Signal_bits is None:
            for sample in ecg:
                filter_instance.dofilter(sample)
        else:
            for sample in ecg:
                filter_instance.dofilter(sample) / (2**Signal_bits)  # Don't forget to scale back down

        elapsed = time.perf_counter() - start
        execution_times.append(elapsed)

    return statistics.median(execution_times)


def main():

    # Check the stuff
    print("\nProcessor architecture:", platform.machine())
    print("Python version:", sys.version)
    print("Python executable:", sys.executable)
    print("NumPy version:", np.__version__)

    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    # ======= STEP 1: Generate IIR Coefficients =======

    # Generate the SOS coefficients for 50 Hz removal
    # Make sure to convert the frequency to Nyquist normalization
    sos_bandstop = signal.butter(2, [45 / 250 * 2, 55 / 250 * 2], btype='bandstop', output='sos')

    # remove DC offset with a high-pass filter at 0.5 Hz
    sos_highpass = signal.butter(2, 0.5 / 250 * 2, btype='highpass', output='sos')

    # Combine the coefficients into one SOS array
    sos = np.vstack((sos_highpass, sos_bandstop))

    # ======= STEP 2: Create Master IIR Filter to Hold the SOS chain =======
    
    Direct_Form_I_Integer_Filter = IIRFilter(filters=[])  
    Direct_Form_I_Float_Filter = IIRFilter(filters=[])
    Direct_Form_II_Filter = IIRFilter(filters=[])

    # ======= STEP 3: Fill the Main Filters with Individual Filter Instances =======

    # 2.1 Direct Form I Filter in Python
    for second_order_filter in sos:
        b = second_order_filter[:3]  # FIR coefficients are the first three
        a = second_order_filter[3:]  # IIR coefficients are the last three
        Q_bits = 14  # No scaling for floating-point implementation  # Calculate the scaling factor

        # The coefficients can fit into a "short" (16-bit) integer
        b_scaled = np.round(b * 2**Q_bits).astype(np.int16)
        a_scaled = np.round(a * 2**Q_bits).astype(np.int16)

        # Create an instance of the DirectFormI filter
        df1_filter = DirectFormI(b_scaled, a_scaled, Q_bits)

        # Add the filter instance to the master IIR filter
        Direct_Form_I_Integer_Filter.filters.append(df1_filter)

    # 2.2 Direct Form I Filter in Python (Floating-Point)
    for second_order_filter in sos:
        b = second_order_filter[:3]  # FIR coefficients are the first three
        a = second_order_filter[3:]  # IIR coefficients are the last three

        # Create an instance of the DirectFormI filter
        df1_filter = DirectFormI(b, a)

        # Add the filter instance to the master IIR filter
        Direct_Form_I_Float_Filter.filters.append(df1_filter)

    # 2.2 Direct Form II Filter in Python
    for second_order_filter in sos:
        b = second_order_filter[:3]  # FIR coefficients are the first three
        a = second_order_filter[3:]  # IIR coefficients are the last three

        # Create an instance of the DirectFormII filter
        df2_filter = DirectFormII(b, a)

        # Add the filter instance to the master IIR filter
        Direct_Form_II_Filter.filters.append(df2_filter)
    

    # ======= STEP 4: Sample the Arduino Signal and Apply the Filter =======

    # =============== DATA PREPARATION ================

    print("\n===============\n")
    print("Running: Realtime FIR Simulation\n")

    file_name = "ecg1.tsv"
    plot_name = "Haider's ECG"

    ecg_time, ecg, ecg_Fs = Load_ECG_Data(file_name)
    print("File: ", file_name)
    print("Sampling Frequency", ecg_Fs)
    print("Duration:", ecg_time[-1], "seconds")

    # =============== FILTERING ================

    # =======================================================
    # ======= Python Implementation of 2nd Order Filters ====
    # =======================================================

    # ============== Direct Form I Filtering ================
    # Check that the result is correct before the benchmarking, and plot the filtered output

    ECG_Filtered_output = np.zeros(len(ecg))
    ecg_fixed_point = np.round(np.array(ecg) * 2**Q_bits).astype(np.int32)  # Convert to fixed-point representation
    start_time = time.time()  # Start the timer for performance measurement

    # Simulate FIR filtering by passing datapoints one by one and store them in filter_output
    for i in range(len(ecg)):
        ECG_Filtered_output[i] = ( Direct_Form_I_Integer_Filter.dofilter(ecg_fixed_point[i]) / (2**Q_bits)  ) # Don't forget to scale back down 
    end_time = time.time()  # End the timer for performance measurement

    # Calculate the elapsed time for filtering
    elapsed_time = end_time - start_time

    plot_time_domain(ECG_Filtered_output, ecg_time, plot_name + "_IIR_filtered_ECG_Direct_Form_I_Python", path_to_output=path_to_output)
    print("\n===============\n")
    print(f"Elapsed time for IIR filtering (Direct Form I): {elapsed_time:.4f} seconds")

    # ============== Direct Form II Filtering ================
    # Check that the result is correct before the benchmarking, and plot the filtered output

    ECG_Filtered_output_II = np.zeros(len(ecg))
    start_time_II = time.time()  # Start the timer for performance measurement

    # Simulate FIR filtering by passing datapoints one by one and store them in filter_output
    for i in range(len(ecg)):
        ECG_Filtered_output_II[i] = Direct_Form_II_Filter.dofilter(ecg[i])
    end_time_II = time.time()  # End the timer for performance measurement

    # Calculate the elapsed time for filtering
    elapsed_time_II = end_time_II - start_time_II

    plot_time_domain(ECG_Filtered_output_II, ecg_time, plot_name + "_IIR_filtered_ECG_Direct_Form_II_Python", path_to_output=path_to_output)
    print("\n===============\n")
    print(f"Elapsed time for IIR filtering (Direct Form II): {elapsed_time_II:.4f} seconds")


    # =======================================================================
    # ======= Benchmarking Python Implementation of 2nd Order Filters =======
    # =======================================================================

    print("\n===============\n")
    print("Benchmarking Direct Form I Fixed-Point Filter...")

    benchmark_results_I = (Direct_Form_I_Integer_Filter, ecg_fixed_point, Q_bits, 1000)

    elapsed_I = benchmark(*benchmark_results_I)

    print(f"\nMedian execution time for Direct Form I Filter: {elapsed_I:.6f} seconds")
    print(f"The per-sample execution time is: {elapsed_I * 1_000_000 / len(ecg_fixed_point):.6f} microseconds")

    print("\n===============\n")
    print("Benchmarking Direct Form I Floating-Point Filter...")

    benchmark_results_I = (Direct_Form_I_Float_Filter, ecg, None, 1000)

    elapsed_I_float = benchmark(*benchmark_results_I)

    print(f"\nMedian execution time for Direct Form I Filter: {elapsed_I_float:.6f} seconds")
    print(f"The per-sample execution time is: {elapsed_I_float * 1_000_000 / len(ecg):.6f} microseconds")
    

    print("\n===============\n")
    print("Benchmarking Direct Form II Filter...")

    benchmark_results_II = (Direct_Form_II_Filter, ecg, None, 1000)

    elapsed_II = benchmark(*benchmark_results_II)

    print(f"\nMedian execution time for Direct Form II Filter: {elapsed_II:.6f} seconds")
    print(f"The per-sample execution time is: {elapsed_II * 1_000_000 / len(ecg):.6f} microseconds\n")
    


if __name__ == "__main__":
    main()