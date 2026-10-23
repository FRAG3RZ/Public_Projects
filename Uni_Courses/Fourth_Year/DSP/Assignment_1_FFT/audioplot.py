# Required imports

from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import os

# Source file path
path_to_files = ''
path_to_output = 'Output_Files/'

# =================================
# === Essential Math Functions ====
# =================================

def rms(x):
    return np.sqrt(np.mean(x**2))

def extract_audio_from_file(name_of_file):
    """ 
    Extracts audio from a WAV file using "scipy" and returns it as an array
    """

    # Use the "scipy" library to read the audio file
    samplerate, audio_raw = wavfile.read(path_to_files + name_of_file + ".wav")
    audio_array = np.array(audio_raw)
    audio_array = audio_array / 32768.0  # Normalize the audio array to -1/1 (0 dB), use 2^15 = 32768 for 16-bit audio

    return audio_array, samplerate

def create_WAV_file(name_of_file, audio_array, samplerate):
    """
    Creates a WAV file from an audio array and saves it to the output folder
    """

    # Convert [-1, 1] floating-point audio to 16-bit PCM
    audio_array = np.clip(audio_array, -1.0, 1.0)
    audio_int16 = (audio_array * 32767).astype(np.int16)

    # Save the audio array as a WAV file
    wavfile.write(path_to_output + name_of_file + ".wav", samplerate, audio_int16)

def fft_of_audio(audio_array, samplerate):

    audio_fft = np.fft.fft(audio_array)
    N = len(audio_array) 

    # Make empty freq. array of size N
    frequency_axis = np.empty(N)

    # Frequency resolution = Fs / N
    # Frequency = k * resolution

    # fill array with correct frequencies
    for i in range(N):
        frequency_axis[i] = i * (samplerate / N)

    return audio_fft, frequency_axis

def inverse_fft(audio_fft):
    """
    Converts an FFT back to the time domain using IFFT
    """

    # Conver back to time and take only real values, as real sound isn't imaginary :) unlike my best friend :( 
    audio_ifft = np.real(np.fft.ifft(audio_fft))

    return audio_ifft

def apply_hamming_window_function(input_array):
    """
    Generates a Hamming window function of length N
    """

    N = len(input_array) # Number of samples
    np.arange(N) # Array of integers from 0 to N-1

    # This is the Mathematical Definition of the Hamming Window Function
    hamming_window = 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1))

    # Multiplication in the time domain is convolution in the frequency domain
    windowed_input_array = input_array * hamming_window

    return windowed_input_array


# ===========================
# === Plotting Functions ====
# ===========================

def plot_time_domain(audio_array, samplerate, name_of_plot, show_plot=True):
    """ 
    Plots the time domain of an audio signal using an array from "scipy"
    """

    # Calculate the maximum amplitude of the audio signal (normalized to -1/1 but still indicates the loudness for comparison)
    max_amplitude = np.max(np.abs(audio_array))
    print(f"Max amplitude: {max_amplitude}")

    # Remap X-axis into time
    # Start at 0, end at length of audio / samplerate, number of points is audio array length
    time_axis = np.linspace(0, len(audio_array) / samplerate, num=len(audio_array))

    # Plotting time domain
    plt.plot(time_axis, audio_array)
    plt.title(f'{name_of_plot} - Time Domain')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.ylim(-1, 1)
    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '_time_domain.pdf') # [:-4 gets rid of .wav]
    if show_plot:
        plt.show()
    plt.close()

def plot_frequency_domain(audio_fft, frequency_axis, samplerate, name_of_plot, logascale=False, show_plot=True):
    """
    Plots the frequency domain of an audio signal using an array from "scipy"
    """

    # Convert y-axis to dB scale
    audio_fft_log = 20 * np.log10(np.abs(audio_fft / len(audio_fft)) + 0.00000000000001) # Encountered log of zero so offset slightly by a very small number to avoid 0 division

    # Plotting frequency domain
    if logascale:
        plt.plot(frequency_axis, audio_fft_log)
        plt.xscale('log')
        plt.ylabel('Magnitude (dB)')
    else:
        plt.plot(frequency_axis, np.abs(audio_fft))
        plt.ylabel('Amplitude')
    plt.title(f'{name_of_plot} - Frequency Domain')
    plt.xlabel('Frequency (Hz)')

    # Cutt off the mirror frequencies (above Fs / 2)
    plt.xlim(1, samplerate / 2) # Log can't start at 0

    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '_frequency_domain.pdf') # [:-4 gets rid of .wav]
    if show_plot:
        plt.show()
    plt.close()


# ================
# ===== MAIN =====
# ================

def main():

    # Make sure the proper output path is used
    global path_to_output
     
    for current_audio_name in ["original_speech_5cm", "original_speech_1m"]:

        show_plots = True
            
        # Set output folder for the current recording
        path_to_output = f"Output_Files/{current_audio_name}/"
        os.makedirs(path_to_output, exist_ok=True)

        #==================================
        #   ===   PART ONE - PLOTTING   ===
        #==================================

        # Extract the time domain and frequency domain from the WAV
        raw_audio, samplerate = extract_audio_from_file(current_audio_name)

        # Use the window function to smooth the edges before plotting the FFT (shows better frequency domain)
        windowed_audio = apply_hamming_window_function(raw_audio)
        windowed_fft, frequency_axis = fft_of_audio(windowed_audio, samplerate)

        # Original signal plotted for analysis
        plot_time_domain(raw_audio, samplerate, current_audio_name + "_02_original_waveform", show_plot=show_plots)
        plot_frequency_domain(windowed_fft, frequency_axis, samplerate, current_audio_name + "_01_original_spectrum_hamming_windowed", logascale=True, show_plot=show_plots)

if __name__ == "__main__":
    main()