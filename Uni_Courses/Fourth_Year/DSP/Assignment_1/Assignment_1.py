# Required imports

import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

# Source file path
path_to_files = 'WAV_Files/'
path_to_output = 'Output_Files/'


def extract_audio_from_file(name_of_file):
    """ 
    Extracts audio from a WAV file using "soundfile" and returns it as an array
    """

    # Use the "soundfile" library to read the audio file
    audio_raw, samplerate = sf.read(path_to_files + name_of_file)
    audio_array = np.array(audio_raw)

    return audio_array, samplerate


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

def plot_frequency_domain(audio_raw, samplerate, name_of_plot, logascale=False, show_plot=True):
    """
    Plots the frequency domain of an audio signal using an array from "soundfile"
    """

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

def filter_frequencies_from_file(name_of_file, low_cutoff, high_cutoff, show_plot=True):
    """
    Filters frequencies from an audio file using FFT and IFFT
    """

    audio_raw, samplerate = sf.read(path_to_files + name_of_file)
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

    # === THIS IS THE FILTERING STEP ===
    # Leave only the frequencies between low_cutoff and high_cutoff, set the rest to 0
    audio_fft_filtered = np.where((frequency_axis >= low_cutoff) & (frequency_axis <= high_cutoff), audio_fft, 0)

    # Convert back to time domain using inverse FFT
    # Make sure the result is real only, as real sound isn't imaginary :)
    audio_filtered = np.real(np.fft.ifft(audio_fft_filtered))

    return audio_filtered, audio_fft_filtered, samplerate

def create_WAV_file(name_of_file, audio_array, samplerate):
    """
    Creates a WAV file from an audio array and saves it to the output folder
    """

    # Save the audio array as a WAV file
    sf.write(path_to_output + name_of_file, audio_array, samplerate)


#===========================
#   === Main Program ===
#===========================

# Raw Time and Frequency Plots

raw_audio, samplerate = extract_audio_from_file('Daniel_5cm.wav')

plot_time_domain(raw_audio, samplerate, 'Daniel_5cm.wav', show_plot=True)
plot_frequency_domain(raw_audio, samplerate, 'Daniel_5cm.wav', logascale=True, show_plot=True)

# Filter Select Frequencies

filtered_audio, filtered_fft, samplerate = filter_frequencies_from_file('Daniel_5cm.wav', 250, 350)

plot_time_domain(filtered_audio, samplerate, 'Daniel_5cm_filtered', show_plot=True)
plot_frequency_domain(filtered_audio, samplerate, 'Daniel_5cm_filtered', logascale=True, show_plot=True)

create_WAV_file('Daniel_5cm_filtered.wav', filtered_audio, samplerate)


