# Required imports

import numpy as np
import matplotlib.pyplot as plt
import os

# ==============
# Global Defines
# ==============

path_to_files = 'ECG_Data/'
path_to_output = 'Output_Files/'

# For us the ECG was set to 250 Hz 
# For calculations below, the Fs is calculated from the delta Time anyway
sampling_frequency_Hz = 250 

# ============================
# === Essential Functions ====
# ============================

def Load_ECG_Data(name_of_file):

    # Use the global path to files for an organized directory
    global path_to_files

    # first load the data as a text
    # ignore comments and data separators
    data = np.loadtxt(path_to_files + name_of_file, delimiter="\t", comments="#")

    # Extract time and ECG (time is first column, actual data is 12th)
    # Both are one-dimensional arrays
    time = data[:, 0]
    ecg = data[:, 11]

    sampling_frequency_Hz = 1 / (time[1] - time[0]) # Use Fs = 1 / deltaT 

    return time, ecg, sampling_frequency_Hz

def fft(data, samplerate):

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


def apply_hamming_window_function(input_array):
    """
    Generates and Applies a Hamming window function of length N
    """

    N = len(input_array) # Number of samples
    n = np.arange(N) # Array of integers from 0 to N-1

    # This is the Mathematical Definition of the Hamming Window Function
    hamming_window = 0.54 - 0.46 * np.cos(2 * np.pi * n / (N - 1))

    # Multiplication in the time domain is convolution in the frequency domain
    windowed_input_array = input_array * hamming_window

    return windowed_input_array

# A CircularBuffer handler to speed up the coefficient buffer, and not have to shift the whole buffer each calculation
class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = np.zeros(size) # Fill the buffer with zeros first
        self.start = 0 
        self.count = 0

    def append(self, item):
        """
        Uses the internal variables to correctly loop through the buffer
        """

        # Assign the new value, "item", into the correct position using the counter modulo'd with the total size
        self.buffer[(self.start + self.count) % self.size] = item 

        # The main looping logic
        if self.count == self.size:
            # If the buffer is full, "count == size", then use the "start" variable to point to the correct position to be overriden
            self.start = (self.start + 1) % self.size  # Overwrite oldest
        else:
            # Else the buffer isn't full yet, so keep increasing "count"
            self.count += 1
    
    def get_item(self, position):
        """
        Calculates the correct index based on the intended position argument
        To return the correct element
        """
        
        # Need the "-1" to account for the fact "start + count" points to the next item to be overriden, 
        # NOT the most recent addition
        index = (self.start + self.count - 1 - position) % self.size

        return self.buffer[index]


# ===========================
# === Plotting Functions ====
# ===========================

def plot_time_domain(data_array, time_axis, name_of_plot, show_plot=True):
    """ 
    Plots the time domain of a signal using its array
    """

    # Plotting time domain - assume that the ECG data already contains a time axis 
    plt.plot(time_axis, data_array)
    plt.title(f'{name_of_plot}')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '.svg') # Save as an SVG
    if show_plot:
        plt.show()
    plt.close()

def plot_frequency_domain(fft, frequency_axis, samplerate, name_of_plot, show_plot=True, normalize=True):
    """
    Plots the frequency domain of a signal using its array
    """

    # We used this normalization in the audio assignment, keep the option for now
    if normalize:
        fft = fft / len(fft)

    # Convert y-axis to dB scale
    fft_log = 20 * np.log10(np.abs(fft) + 1e-14) # Encountered log of zero so offset slightly by a very small number to avoid 0 division

    # Plotting frequency domain
    plt.plot(frequency_axis, fft_log)
    plt.ylabel('Magnitude (dB)')
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


# ================================
# === FIR Functions and Class ====
# ================================

# ============ ASSIGNMENT PART TWO ====================

def calculate_FIR_coefficients(bandstop_frequency_array, sampling_rate, remove_DC = True, maximum_delay_seconds = 2):
    """
    Calculates the FIR coefficients

    Bandstop_frequency_array should be a two-dimensional array of integer pairs, representing the start and stop frequencies of the stopbands

    Example: 
        stopbands = np.array([
            [45, 55],     # Remove 50 Hz interference
            [55, 65],     # Remove 60 Hz interference (if we want to also remove US mains noise for example)
        ])
    """

    # Calculate M from sampling rate
    # The higher the M, the smaller the frequency resolution (better), but the larger the delay (worse)
    # For ECG readings, a delay of ~1-2 seconds by default is reasonable to allow a doctor to examine the ECG in ~real-time
    # Thus:
    maximum_delay_samples = int(maximum_delay_seconds * sampling_rate)

    # Rearanging Tau = M / 2 samples -> Tau = M / ( 2 * Fs) seconds
    # M will be always odd, so the center is always at an integer index
    M = 2 * maximum_delay_samples + 1
    print(f"\nThe recommended number of taps used for a {sampling_rate} Hz sampling rate and {maximum_delay_seconds}s maximum delay is: {M} taps.")

    # Calculate the middle index (M is always odd) -> cast to integer to round down to the correct index
    middle = int(M / 2)

    # prepare the variable to store all stopbands' frequency representation
    final_frequency_window = np.ones(M)

    for stopband in bandstop_frequency_array:

        # calculate the correct position of the stopband in terms of tap number M
        k1 = int( (stopband[0] / sampling_rate) * M)
        k2 = int( (stopband[1] / sampling_rate) * M)

         # always maintains symmetry around the M/2 point -> linear phase filter to maintain constant group delay!
        final_frequency_window[k1: k2+1] = 0 # zero out stopband in the shared frequency window
        final_frequency_window[M - k2: M - k1+1] = 0 # zero out mirror stopband in the shared frequency window

    if remove_DC:
        final_frequency_window[0] = 0 # zero out first tap -> DC HAS NO MIRROR!

    # Plot the window to check
    frequency_axis = np.arange(middle) * sampling_rate / M # Create frequency axis in Hz (positive frequencies only -> up to "M/2")
    # Don't normalize this, as we want to see the 0 dB for full pass amplitude -> unlike real voltage signals which we normalize for graphing by 1 / N
    plot_frequency_domain(final_frequency_window[0 : middle], frequency_axis, sampling_rate, "Desired_FIR_Frequency_Response", normalize=False) 

    # Move the window from the frequency domain to the tap domain: X[K] -> x[n] & ensure it is real
    x = inverse_fft(final_frequency_window)

    # prepare the Impulse Response array
    h = np.zeros(M)

    # Into the first half move the second half of the Impulse Response x[n] AND VICE VERSA
    # Use the correct center calculated above as M is always odd
    h[0 : middle] = x[middle + 1: M] 
    h[middle : M] = x[0 : middle + 1]

    # Smooth out the edges of the Impulse Response for better filtering
    h = apply_hamming_window_function(h)

    return h

class FIRfilter:

    def __init__(self,_coefficients):
        self.tap_number = len(_coefficients) # Initialize M to the size of the coefficient array
        self.FIR_coefficients = _coefficients # Initialize the coefficients to the ones passed to the contructor
        self.data_buffer = CircularBuffer(self.tap_number) # prepare the Impulse Response CircularBuffer class of length M -> it starts empty by default

    # Take in the latest value and output the filter result
    def doFilter(self, latest_data):
        """
        In the bandstop filter implementation, 
        The delay buffer stores the signal and uses pre-taught coefficients to remove unwanted noise
        """

        # Append the latest value to the circular buffer
        # The class internally keeps track of the pointer position and overides the correct value
        self.data_buffer.append(latest_data)

        # Prepare the sum -> scalar value (the filter output)
        sum = 0

        # Multiply, and sum, the corresponding data and n-delay pairs
        for i in range(self.tap_number):
            sum += self.data_buffer.get_item(i) * self.FIR_coefficients[i]

        return sum 

    # Filter while changing the FIR coefficients using the "least mean square" error^2 minimization approach
    def doFilterAdaptive(self, signal, noise, learningRate = 0.001):
        """
        In the LMS filter implementation, 
        The delay buffer stores the noise and slowly teaches itself how to remove it from the signal by updating the FIR coefficients
        """

        # Filter the reference noise to estimate interference
        # Starts at 0 and slowly builds to the actual interefence
        estimated_noise = self.doFilter(noise)

        # Calculate the error (cleaned ECG)
        # Starts equal to original ECG and evolves into original ECG - noise
        error = signal - estimated_noise

        # Then, update all FIR coefficients
        for i in range (self.tap_number):
            # implement deltaH = mu * error * x(n - M)
            self.FIR_coefficients[i] += learningRate * error * self.data_buffer.get_item(i)

        return error


def main():

    # Make sure the proper output path is used
    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    #for file_name in ["daniel_1.tsv", "daniel_2.tsv", "haider_1.tsv", "haider_2.tsv"]:
    for file_name in ["daniel_1.tsv"]:

        # =============== DATA PREPARATION ================

        print("\n===============\n")

        time, ecg, Fs = Load_ECG_Data(file_name)
        print("File: ", file_name)
        print("Sampling Frequency", Fs)
        print("Duration:", time[-1], "seconds")

        # =============== PART 1 - PLOTTING ================


        plot_name = file_name[:-4] # Remove the .tsv for plot naming

        # Plot the ECG in time domain
        plot_time_domain(ecg, time, plot_name + "_Unfiltered_ECG - Time Domain")

        # Plot the ECG in the frequency domain
        ecg_fft, frequency_axis = fft(ecg, Fs)
        plot_frequency_domain(ecg_fft, frequency_axis, Fs, plot_name + "_Unfiltered_ECG - Frequency Domain")


        # =============== PART 2 - FIR COEFFICIENT CREATION ================


        # Prepare the stopbands -> remove DC and remove mains noise
        stopbands = np.array([
                    [45, 55],     # Remove 50 Hz interference
                    [0.1, 0.5]    # Remove DC wander and other factors like breathing
                ])

        FIR_coefficients = calculate_FIR_coefficients(stopbands, Fs, maximum_delay_seconds=1)


        # =============== PART 3 - FIR CLASS USAGE ================

        # Create a bandstop filter instance and empty output array
        Bandstop_Filter = FIRfilter(FIR_coefficients)
        filter_output = np.zeros(len(ecg))

        # Simulate FIR filtering by passing datapoints one by one and store them in filter_output
        for i in range(len(ecg)):
            filter_output[i] = Bandstop_Filter.doFilter(ecg[i])

        plot_time_domain(filter_output, time, plot_name + "_Bandstop_filtered_ECG_using - Time Domain")

        # =============== PART 4 - Least Mean Squared error ================
        
        # Create an LMS filter instance and empty output array
        LMS_Filter = FIRfilter(np.zeros(500))
        lms_filter_output = np.zeros(len(ecg))

        # Simulate Adaptive FIR filtering by passing datapoints one by one and storing them in lms_filter_output
        for i in range(len(ecg)):
            # Introduce a perfect 50 Hz sine as the training noise
            mains_noise = np.sin(2.0 * np.pi * 50 / Fs * i)

            lms_filter_output[i] = LMS_Filter.doFilterAdaptive(ecg[i], mains_noise, learningRate=0.001)

        plot_time_domain(lms_filter_output, time, plot_name + "_LMS_filtered_ECG_using - Time Domain")

        # =============== PART 5 - Matched Filter ================


        print("===============\n")

if __name__ == "__main__":
    main()