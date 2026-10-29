# Required imports

import numpy as np
import matplotlib.pyplot as plt
import os

# ==============
# Global Defines
# ==============

path_to_files = ''
path_to_output = 'Output_Files/'

# For us the ECG was set to 250 Hz 
# For calculations below, the Fs is calculated from the delta Time anyway
sampling_frequency_Hz = 250 

# ============================
# === Essential Functions ====
# ============================

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

def fft(data, samplerate):
    """
    Converts a time domain signal into its frequency domain representation
    """

    # ONLY 1 OF 2 NUMPY HIGH-LEVEL FUNCTIONS
    fft_data = np.fft.fft(data)
    N = len(data) 

    # Make empty freq. array of size N
    frequency_axis = np.empty(N)

    # Frequency resolution = Fs / N
    # Frequency = k * resolution

    # fill array with correct frequencies
    for i in range(N):
        frequency_axis[i] = i * (samplerate / N)

    return fft_data, frequency_axis

def inverse_fft(fft_data):
    """
    Converts an FFT back to the time domain using IFFT
    """
    # SECOND OF THE TWO NUMPY HIGH-LEVEL FUNCTIONS
    # Convert back to time and take only real values, as real sound isn't imaginary :) unlike my best friend :( 
    ifft_data = np.real(np.fft.ifft(fft_data))

    return ifft_data

# ===========================
# === Plotting Functions ====
# ===========================

def plot_time_domain(data_array, time_axis, name_of_plot, show_plot=True, y_label='Voltage (mV)'):
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

def plot_frequency_domain(fft, frequency_axis, samplerate, name_of_plot, show_plot=True, normalize=True, y_label='Voltage (mV)'):
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
    plt.xlim(0, samplerate / 2) # If using Log on the x-axis, Log can't start at 0 so use 1

    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '.svg') # Save as an SVG
    if show_plot:
        plt.show()
    plt.close()


def main():

    # Make sure the proper output path is used
    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    # =============== DATA PREPARATION ================

    print("\n===============\n")
    print("Running: ECG_Plot\n")

    file_name = "ecg_1.tsv" # Used for Steps 1 - 4

    plot_name = file_name[:-4] # Remove the .tsv for plot naming

    time, ecg, Fs = Load_ECG_Data(file_name)
    print("File: ", file_name)
    print("Sampling Frequency", Fs)
    print("Duration:", time[-1], "seconds")

    # =============== PART 1 - PLOTTING ================


    # Plot the ECG in time domain
    plot_time_domain(ecg, time, plot_name + "_Unfiltered_ECG - Time Domain")

    # Plot the ECG in the frequency domain
    ecg_fft, frequency_axis = fft(ecg, Fs)
    plot_frequency_domain(ecg_fft, frequency_axis, Fs, plot_name + "_Unfiltered_ECG - Frequency Domain")

    print("\n===============\n")


if __name__ == "__main__":
    main()