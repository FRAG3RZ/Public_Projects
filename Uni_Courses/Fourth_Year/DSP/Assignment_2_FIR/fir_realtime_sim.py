from fir_filter import *
from fir_design import *

path_to_output = 'Output_Files/'

def main():

    # Make sure the proper output path is used
    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    # =============== DATA PREPARATION ================

    print("\n===============\n")
    print("Running: Realtime FIR Simulation\n")

    file_name = "ecg_1.tsv"

    plot_name = file_name[:-4] # Remove the .tsv for plot naming

    time, ecg, Fs = Load_ECG_Data(file_name)
    print("File: ", file_name)
    print("Sampling Frequency", Fs)
    print("Duration:", time[-1], "seconds")

    # =============== FIR COEFFICIENT CREATION ================


    # Prepare the stopbands -> remove DC and remove mains noise
    stopbands = np.array([
                [45, 55],     # Remove 50 Hz interference
                [0.1, 0.6]    # Remove DC wander and other factors like breathing (works really well!) -> careful not to remove the T-part of the PQRST
            ])

    # For the Kaiser Variables, use reasonable values
    FIR_coefficients = calculate_FIR_coefficients(stopbands, Fs, side_lobe_decay_dB=60, transition_width_rad= 2 * np.pi * 2 / Fs)

    # =============== FIR CLASS USAGE ================

    # Create a bandstop filter instance and empty output array
    Bandstop_Filter = FIRfilter(FIR_coefficients)
    Bandstop_filter_output = np.zeros(len(ecg))

    # Simulate FIR filtering by passing datapoints one by one and store them in filter_output
    for i in range(len(ecg)):
        Bandstop_filter_output[i] = Bandstop_Filter.doFilter(ecg[i])

    plot_time_domain(Bandstop_filter_output, time, plot_name + "_Bandstop_filtered_ECG_using - Time Domain")

    print("\n===============\n")


if __name__ == "__main__":
    main()