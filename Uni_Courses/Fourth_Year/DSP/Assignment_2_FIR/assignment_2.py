# Required imports

import numpy as np
import matplotlib.pyplot as plt
import os

# ==============
# Global Defines
# ==============

path_to_files = 'ECG_Data/'
path_to_output = 'Output_Files/'

sampling_frequency_Hz = 250 # For us the ECG was set to 250 Hz

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


def main():

    # Make sure the proper output path is used
    global path_to_output
    os.makedirs(path_to_output, exist_ok=True)

    for file_name in ["daniel_1.tsv", "daniel_2.tsv", "haider_1.tsv", "haider_2.tsv"]:

        time, ecg, Fs = Load_ECG_Data(file_name)
        print("ECG shape:", ecg.shape)
        print("Sampling Frequency", Fs)
        print("Duration:", time[-1], "seconds")

        # Plot the ECG
        plt.figure(figsize=(12, 4))
        plt.plot(time, ecg)
        plt.xlabel("Time (s)")
        plt.ylabel("ECG amplitude")
        plt.title("ECG Recording")
        plt.grid(True)
        plt.show()
    

if __name__ == "__main__":
    main()