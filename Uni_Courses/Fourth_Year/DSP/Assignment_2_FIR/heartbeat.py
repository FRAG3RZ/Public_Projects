from fir_filter import *
from fir_design import *

path_to_output = 'Output_Files/'

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
    print("Running: Realtime Bandstop FIR Filter + Heart Beat Detection Simulation\n")

    file_name = "ecg_1.tsv" # Used for Steps 1 - 4
    
    plot_name = file_name[:-4] # Remove the .tsv for plot naming
    time, ecg, Fs = Load_ECG_Data(file_name)
    print("File: ", file_name)
    print("Sampling Frequency", Fs)
    print("Duration:", time[-1], "seconds")

    template_file_name = "ecg_2.tsv" # Template used for Matching in Step 5
    template_name = template_file_name[:-4] # Remove the .tsv for plot naming
    template_time, template_ecg, template_Fs = Load_ECG_Data(template_file_name)

    # =============== FIR COEFFICIENT CREATION ================
    
    # Prepare the stopbands -> remove DC and remove mains noise
    stopbands = np.array([
                [45, 55],     # Remove 50 Hz interference
                [0.1, 0.6]      # Remove DC wander and other factors like breathing (works really well!)
            ])

    # For the Kaiser Variables, use reasonable values
    FIR_coefficients = calculate_FIR_coefficients(stopbands, Fs, side_lobe_decay_dB=60, transition_width_rad= 2 * np.pi * 2 / Fs)

    # =============== Matched Filter ================

    # ===== Step 1 - filter the signal(use other lab partner) =====
    
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