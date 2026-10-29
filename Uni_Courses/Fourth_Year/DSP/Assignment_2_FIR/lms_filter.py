from fir_filter import *

path_to_output = 'Output_Files/'

def main():

    # Make sure the proper output path is used
    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    # =============== DATA PREPARATION ================

    print("\n===============\n")
    print("Running: Realtime LMS FIR Filter Simulation\n")

    file_name = "ecg_1.tsv"

    plot_name = file_name[:-4] # Remove the .tsv for plot naming

    time, ecg, Fs = Load_ECG_Data(file_name)
    print("File: ", file_name)
    print("Sampling Frequency", Fs)
    print("Duration:", time[-1], "seconds")

    # =============== Least Mean Squared Error Filter ================

    # Create an LMS filter instance and empty output array
    LMS_Filter = FIRfilter(np.zeros(500))
    lms_filter_output = np.zeros(len(ecg))

    # Simulate Adaptive FIR filtering by passing datapoints one by one and storing them in lms_filter_output
    for i in range(len(ecg)):
        # Introduce a perfect 50 Hz sine as the training noise
        mains_noise = np.sin(2.0 * np.pi * 50 / Fs * i) + 0.2

        lms_filter_output[i] = LMS_Filter.doFilterAdaptive(ecg[i], mains_noise, learningRate=0.0005)

    plot_time_domain(lms_filter_output, time, plot_name + "_LMS_filtered_ECG_using - Time Domain")

    print("\n===============\n")

if __name__ == "__main__":
    main()