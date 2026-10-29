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


# A CircularBuffer handler to speed up the coefficient buffer, and not have to shift the whole buffer each calculation
class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = np.zeros(size) # Fill the buffer with zeros first
        self.oldest_index = 0 
        self.fill_count = 0

    def append(self, item):
        """
        Uses the internal variables to correctly loop through the buffer
        """

        # Assign the new value, "item", into the correct position using the counter modulo'd with the total size
        self.buffer[(self.oldest_index + self.fill_count) % self.size] = item 

        # The main looping logic
        if self.fill_count == self.size:
            # If the buffer is full, "count == size", then use the "oldest_index" variable to point to the correct position to be overriden
            self.oldest_index = (self.oldest_index + 1) % self.size  # Overwrite oldest
        else:
            # Else the buffer isn't full yet, so keep increasing "fill_count"
            self.fill_count += 1
    
    def get_item(self, position):
        """
        Calculates the correct index based on the intended position argument
        To return the correct element
        """
        
        # Start at the newest sample, then move backwards by the requested item position
        index = (self.oldest_index + self.fill_count - 1 - position) % self.size

        return self.buffer[index]

def kaiser_variable_helper(A, deltaOmega):
    """
    Calculates the required variables for the Kaiser Window using the formulas in the lectures
    """

    # Implement the empyrical piecewise operation for Beta
    if(A > 50):
        beta = 0.1102 * (A - 8.7)
    elif(A<=50 and A>=21):
        beta = 0.5842 * (A - 21)**0.4 + 0.07886 * (A - 21)
    else:
        beta = 0

    # Cast to integer for later calculations, and add 1 because int() rounds down, and we want an M larger than the "minimum" recommended
    M = int((A - 8) / (2.285 * deltaOmega)) + 1 

    # Ensure the FIR filter has an odd number of taps, so the middle index lays at an integer, and NOT a half
    if M % 2 == 0:
        M += 1

    return M, beta


def kaiser_window_function(h, beta, alpha):
    """
    Ammplies a Kaiser Window Function to the input array "h"
    """

    # Generate sample indices from 0 to N-1
    n = np.arange(len(h))

    # Calculate the Kaiser window from the mathematical formula in the lecture slides
    window = np.i0(beta * np.sqrt(1 - ((n - alpha) / alpha)**2)) / np.i0(beta)

    # Apply the Kaiser window by multiplying h
    h *= window

    return h

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


# ================================
# === FIR Functions and Class ====
# ================================

# ============ ASSIGNMENT PART TWO ====================

def calculate_FIR_coefficients(bandstop_frequency_array, sampling_rate, remove_DC = True, side_lobe_decay_dB=60, transition_width_rad=0.05):
    """
    Calculates the FIR coefficients

    Bandstop_frequency_array should be a two-dimensional array of integer pairs, representing the start and stop frequencies of the stopbands

    Example: 
        stopbands = np.array([
            [45, 55],     # Remove 50 Hz interference
            [55, 65],     # Remove 60 Hz interference (if we want to also remove US mains noise for example)
        ])
    """

    # Calculate M from the Kaiser method. 
    # If A and deltaOmega aren't specified in the function arguments, use the defaults we found most effective
    M, beta = kaiser_variable_helper(side_lobe_decay_dB, transition_width_rad)

    # Also report the resulting delay and resolution
    group_delay = M / (2*sampling_rate)   
    print(f"\nThe Kaiser-calculated tap number, M, is: {M} \n\t resulting in a frequency resolution of: {(sampling_rate / M ):0.3f} Hz \n\t and group delay of: {group_delay} seconds\n")

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
    plot_frequency_domain(final_frequency_window[0 : middle], frequency_axis, sampling_rate, "Desired_FIR_Frequency_Response", normalize=False, y_label="Gain") 

    # Move the window from the frequency domain to the tap domain: X[K] -> x[n] & ensure it is real
    x = inverse_fft(final_frequency_window)

    # prepare the Impulse Response array
    h = np.zeros(M)

    # Into the first half move the second half of the Impulse Response x[n] AND VICE VERSA
    # Use the correct center calculated above as M is always odd
    h[0 : middle] = x[middle + 1: M] 
    h[middle : M] = x[0 : middle + 1]

    # Apply the Kaiser window function for the intended filter response
    h = kaiser_window_function(h, beta, middle)

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

def detect_R_peaks(filter_output_sample, min_sample_spacing, was_previous_max, samples_to_prev_detection, max, Fs):
    """
    Causal R peak detection
    Takes in a sample and then compares with the heuristic and previous nmax to detect peaks
    """

    # Assume no detection by default
    r_detected = 0

    # Slowly decay the max value by 0.5% for each sample
    # Expected level before next heartbeat is about 50% (about 136 samples for 110 BPM at 250 Hz Fs)
    # High enough to miss noise, low enough so smaller Matched Filter detections still get detected
    # Decays more slowly with a lower value
    max = max - 0.005 * max

    # If there is a new maximum value keep track
    if filter_output_sample > max:
        max = filter_output_sample
        was_previous_max = True

    # If the value keeps increasing, keep updating the max, but if it starts falling, detect the falling edge
    if filter_output_sample < max and was_previous_max:
        # Apply the heuristic
        if( samples_to_prev_detection >= min_sample_spacing):
            r_detected = 1 # New R detection

        # Detect each falling edge only once
        was_previous_max = False

    return r_detected, max, was_previous_max


def main():

    # Make sure the proper output path is used
    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    # =============== DATA PREPARATION ================

    print("\n===============\n")

    file_name = "haider_2.tsv" # Used for Steps 1 - 4
    template_file_name = "daniel_1.tsv" # Template used for Matching in Step 5

    plot_name = file_name[:-4] # Remove the .tsv for plot naming
    template_name = template_file_name[:-4] # Remove the .tsv for plot naming

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


    # =============== PART 2 - FIR COEFFICIENT CREATION ================


    # Prepare the stopbands -> remove DC and remove mains noise
    stopbands = np.array([
                [45, 55],     # Remove 50 Hz interference
                [0.1, 0.6]      # Remove DC wander and other factors like breathing (works really well!)
            ])

    # For the Kaiser Variables, use reasonable values
    FIR_coefficients = calculate_FIR_coefficients(stopbands, Fs, side_lobe_decay_dB=60, transition_width_rad= 2 * np.pi * 2 / Fs)


    # =============== PART 3 - FIR CLASS USAGE ================


    # Create a bandstop filter instance and empty output array
    Bandstop_Filter = FIRfilter(FIR_coefficients)
    Bandstop_filter_output = np.zeros(len(ecg))

    # Simulate FIR filtering by passing datapoints one by one and store them in filter_output
    for i in range(len(ecg)):
        Bandstop_filter_output[i] = Bandstop_Filter.doFilter(ecg[i])

    plot_time_domain(Bandstop_filter_output, time, plot_name + "_Bandstop_filtered_ECG_using - Time Domain")


    # =============== PART 4 - Least Mean Squared error ================
    

    # Create an LMS filter instance and empty output array
    LMS_Filter = FIRfilter(np.zeros(500))
    lms_filter_output = np.zeros(len(ecg))

    # Simulate Adaptive FIR filtering by passing datapoints one by one and storing them in lms_filter_output
    for i in range(len(ecg)):
        # Introduce a perfect 50 Hz sine as the training noise
        mains_noise = np.sin(2.0 * np.pi * 50 / Fs * i) + 0.2

        lms_filter_output[i] = LMS_Filter.doFilterAdaptive(ecg[i], mains_noise, learningRate=0.0005)

    plot_time_domain(lms_filter_output, time, plot_name + "_LMS_filtered_ECG_using - Time Domain")


    # =============== PART 5 - Matched Filter ================

    # =====Step 1 - filter the signal(use other lab partner) =====

    template_time, template_ecg, template_Fs = Load_ECG_Data(template_file_name)
    print("Template File: ", template_file_name)

    # Use the same coefficients as PART 3 to remove mains and DC wander
    Template_Filter = FIRfilter(FIR_coefficients) 
    Template_Filter_Output = np.zeros(len(template_ecg))
    
    # Simulate FIR filtering by passing datapoints one by one and store them in filter_output
    for i in range(len(template_ecg)):
        Template_Filter_Output[i] = Template_Filter.doFilter(template_ecg[i])

    # ===== Step 2 = create template from filtered data =====     
     
    # Use daniel_1: 2.9s - 3.7s, convert to samples using sample_rate
    template = Template_Filter_Output[int(2.9 * template_Fs) : int(3.7 * template_Fs)]

    # ===== Step 3, time reverse the template to get the Impulse Response =====
    Matched_FIR_coefficients = template[::-1]

    # ===== Step 4, filter the ORIGINAL ECG with the time-reversed template =====

    # Prepare the Matched Filter instance as well as a bandstop filter instance to feed it filtered data
    Matched_FIR_Filter = FIRfilter(Matched_FIR_coefficients)
    Input_Bandstop_Filter = FIRfilter(FIR_coefficients)

    # Prepare all output arrays
    Matched_FIR_Filter_Output = np.zeros(len(ecg))
    Input_Bandstop_Filter_Output = np.zeros(len(ecg))
    detected_R_peaks = np.zeros(len(ecg))
    momentary_heart_rate = np.zeros(len(ecg))

    # Create static variables
    local_maximum_nmax = 0
    samples_to_prev_detection = 0
    was_previous_max = False
    R_detected_once = False

    # Heuristic array -> only accept detections matching valid bpm
    # As the R_peak detection is causal, we can't really ignore peaks which fall into a smaller bpm
    # Once the bpm would be lower than 40 bpm, then no more values would ever be taken
    # Therefore, APPLY ONLY MAXIMUM BPM HERE
    Maximum_Heuristic_BPM = 150

    # Convert BPM thresholds to an accepted min spacing:
    min_sample_spacing = 1 / (Maximum_Heuristic_BPM / 60) * Fs

    for i in range(len(ecg)):

        # Keep track of previous detections
        samples_to_prev_detection += 1

        # First filter the original ECG using a normal bandpass
        Input_Bandstop_Filter_Output[i] = Input_Bandstop_Filter.doFilter(ecg[i])

        # Use the filtered ECG output as the input to the Matched filter
        Matched_FIR_Filter_Output[i] = Matched_FIR_Filter.doFilter(Input_Bandstop_Filter_Output[i])

        # ===== Step 5, square the output to improve SNR =====
        # ===== Step 6, detect the R peaks and apply a heuristic to filter incorrect peaks ===== 
        detected_R_peaks[i], local_maximum_nmax, was_previous_max = detect_R_peaks(Matched_FIR_Filter_Output[i] ** 2, min_sample_spacing, was_previous_max, samples_to_prev_detection, local_maximum_nmax, Fs)

        # If new peak is detected, update heart rate
        if(detected_R_peaks[i]):
            # Only update the BPM once two R_peak readings are done
            if R_detected_once:
                momentary_heart_rate[i] =  60 * Fs / samples_to_prev_detection
            R_detected_once = True
            samples_to_prev_detection = 0
        else:
            if i > 0:
                momentary_heart_rate[i] = momentary_heart_rate[i-1]


    # Plot the Heart Rate vs. Time graph
    plot_time_domain(momentary_heart_rate, time, plot_name + "_Momentary_Heart_Rate", y_label="Heart Rate (BPM)")

    # ===== Step 7 - Plot the detected R-peaks against the ECG =====

    plt.figure()

    # Plot the original ECG
    plt.plot(time, Input_Bandstop_Filter_Output, label="Bandstop Filtered ECG")

    # Accept only indexes where R is detected
    peak_indexes = np.flatnonzero(detected_R_peaks) 

    # Also need to offset the indexes by the R peak of the template itself (just find it's maximum value)
    R_peak_of_template = np.argmax(template)
    peak_offset = len(template) - 1 - R_peak_of_template
    peak_indexes -= peak_offset
    
    # Mark the detected R-peaks with red crosses
    plt.plot(time[peak_indexes], Input_Bandstop_Filter_Output[peak_indexes],'rx', label="Detected Falling Edge of R-peaks")
    plt.title("Bandstop Filtered ECG with Detected R-peaks")
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (mV)")
    plt.legend()
    plt.grid()

    # Save as SVG for the report
    plt.savefig(path_to_output + plot_name + "_Original_ECG_With_Detected_R_Peaks.svg")
    plt.show()
    plt.close()

    print("\n===============\n")

if __name__ == "__main__":
    main()