# Required imports

import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import os

# Source file path
path_to_files = 'WAV_Files/'
path_to_output = 'Output_Files/'

def extract_audio_from_file(name_of_file):
    """ 
    Extracts audio from a WAV file using "soundfile" and returns it as an array
    """

    # Use the "soundfile" library to read the audio file
    audio_raw, samplerate = sf.read(path_to_files + name_of_file+ ".wav")
    audio_array = np.array(audio_raw)

    return audio_array, samplerate

def fft_of_audio(audio_raw, samplerate):

    audio_array = np.array(audio_raw)
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

    # Conver back to time and take only real values, as real sound isn't imaginary :) (unlike my best friend :( )
    audio_ifft = np.real(np.fft.ifft(audio_fft))

    return audio_ifft


# ===========================
# === Plotting Functions ====
# ===========================

def plot_time_domain(audio_raw, samplerate, name_of_plot, show_plot=True):
    """ 
    Plots the time domain of an audio signal using an array from "soundfile"
    """

    audio_array = np.array(audio_raw)
    max_amplitude = np.max(np.abs(audio_array))

    # Check maximum amplitude
    print(f"Max amplitude: {max_amplitude}")

    # Normalize Y-axis
    audio_array = audio_array / max_amplitude

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
    plt.savefig(path_to_output + name_of_plot + '_time_domain.pdf', dpi=600) # [:-4 gets rid of .wav]
    if show_plot:
        plt.show()
    plt.close()

def plot_frequency_domain(audio_fft, frequency_axis, samplerate, name_of_plot, logascale=False, show_plot=True):
    """
    Plots the frequency domain of an audio signal using an array from "soundfile"
    """

    # Convert y-axisto dB scale
    audio_fft_log = 20 * np.log10(np.abs(audio_fft) + 0.00000001) # Encountered log of zero so offset slightly

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

    # Cutt off the mirror frequencies (Fs / 2)
    plt.xlim(0, samplerate / 2)

    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '_frequency_domain.pdf', dpi=600) # [:-4 gets rid of .wav]
    if show_plot:
        plt.show()
    plt.close()


#===========================
#=== Filtering Functions ===
#===========================

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

def bandpass_filter(audio_fft, frequency_axis, low_cutoff, high_cutoff):
    """
    Filters frequencies using FFT and IFFT
    """

    # === THIS IS THE FILTERING STEP ===
    # Leave only the frequencies between low_cutoff and high_cutoff, set the rest to 0
    audio_fft_filtered = np.where((frequency_axis >= low_cutoff) & (frequency_axis <= high_cutoff), audio_fft, 0)

    return audio_fft_filtered


def bandstop_filter(audio_fft, frequency_axis, low_cutoff, high_cutoff):
    """
    Filters frequencies using FFT and IFFT
    """

    # Leave only the frequencies between low_cutoff and high_cutoff, set the rest to 0
    audio_fft_filtered = np.where((frequency_axis < low_cutoff) | (frequency_axis > high_cutoff), audio_fft, 0)

    return audio_fft_filtered

def band_multiplier(audio_fft, frequency_axis, low_cutoff, high_cutoff, multiplier):
    """
    Multiplies frequencies using FFT and IFFT
    """

    # Take the specified band, and multiply it by the multiplier, leave the rest unchanged
    audio_fft_multiplied = np.where((frequency_axis >= low_cutoff) & (frequency_axis <= high_cutoff), audio_fft * multiplier, audio_fft)

    return audio_fft_multiplied

def audio_normalizer(audio_array):
    """
    Normalizes an audio array to the range of -1 to 1
    """

    # Find the max amplitude of the whole speech
    max_amplitude = np.max(np.abs(audio_array))

    # Divide all the values by the maximum to normalize
    normalized_audio_array = audio_array / max_amplitude

    return normalized_audio_array

def create_WAV_file(name_of_file, audio_array, samplerate):
    """
    Creates a WAV file from an audio array and saves it to the output folder
    """

    # Save the audio array as a WAV file
    sf.write(path_to_output + name_of_file + ".wav", audio_array, samplerate)

#===========================
#   === Aural Exciter ===
#===========================

def aural_exciter(audio_raw, samplerate, high_fundamental_frequency, low_fundamental_frequency, band_gap):
    """
    Enhances the voice in an audio signal using harmonic addition
    """

    # Make the FFT
    audio_fft, frequency_axis = fft_of_audio(audio_raw, samplerate)

    # First, isolate the two frequency bands
    high_frequency_band = bandpass_filter(audio_fft, frequency_axis, high_fundamental_frequency - band_gap, high_fundamental_frequency + band_gap)
    low_frequency_band = bandpass_filter(audio_fft, frequency_axis, low_fundamental_frequency - band_gap, low_fundamental_frequency + band_gap)

    # Then, convert back to time domain and normalize
    high_frequency_band_time = inverse_fft(high_frequency_band)
    low_frequency_band_time = inverse_fft(low_frequency_band)

    # Then, use a non-linear function to create harmonics in the time domain
    high_frequency_band_time_harmonics = np.tanh(high_frequency_band_time)
    low_frequency_band_time_harmonics = np.tanh(low_frequency_band_time)

    # Now, fuse all three together
    fused_audio = audio_raw + high_frequency_band_time_harmonics + low_frequency_band_time_harmonics

    return fused_audio


#===========================
#   === Main Program ===
#===========================

# ==== Raw Time and Frequency Plots ====

current_audio_name = 'Daniel_Vowels'

raw_audio, samplerate = extract_audio_from_file(current_audio_name)
fft_audio, frequency_axis = fft_of_audio(raw_audio, samplerate)

plot_time_domain(raw_audio, samplerate, current_audio_name + "_raw", show_plot=True)

# Use the window function to smooth the edges before plotting
windowed_audio = apply_hamming_window_function(raw_audio)
windowed_fft_audio, windowed_frequency_axis = fft_of_audio(windowed_audio, samplerate)
plot_frequency_domain(windowed_fft_audio, windowed_frequency_axis, samplerate, current_audio_name + "_windowed", logascale=True, show_plot=True)

# ==== Filtering Step ====

# ==== STEP 2 ====

# Enhance the harmonics of Daniel's voice
for i in range(4):

    fundamental_freq = 100  # Fundamental frequency of Daniel's voice in Hz
    # MY VOWEL A IS 100 HZ????????

    harmonic_freq = fundamental_freq * (i + 1) 
    fft_audio = band_multiplier(fft_audio, frequency_axis, harmonic_freq - 10, harmonic_freq + 10, 0) # Enhance the harmonic frequency by 2x
    fft_audio = band_multiplier(fft_audio, frequency_axis, harmonic_freq + (fundamental_freq*0.2), harmonic_freq + (fundamental_freq*0.8), 1) # Enhance the harmonic frequency by 2x

filtered_fft = bandpass_filter(fft_audio, frequency_axis, 20, 20000) # Humans only hear from 20 - 20,000 Hz
filtered_fft = bandstop_filter(filtered_fft, frequency_axis, 48, 52) # Remove main noise 

# === Plot the filtered frequency domain ===

plot_frequency_domain(filtered_fft, frequency_axis, samplerate, current_audio_name + "_filtered", logascale=True, show_plot=True)

# == AURAL EXCITER ===

excited_audio = aural_exciter(raw_audio, samplerate, 1000, 120, 10)
create_WAV_file(current_audio_name + "_aurally_excited", excited_audio, samplerate)

# ==== Export to WAV again to hear it!!!! ====

inverse_filtered_audio = inverse_fft(filtered_fft)
inverse_filtered_audio = audio_normalizer(inverse_filtered_audio)
create_WAV_file(current_audio_name + "_inverse_filtered", inverse_filtered_audio, samplerate)


