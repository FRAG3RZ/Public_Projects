# Required imports

from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
import os

# Source file path
path_to_files = 'WAV_Files/'
path_to_output = 'Output_Files/'

# =================================
# === Essential Math Functions ====
# =================================

def extract_audio_from_file(name_of_file):
    """ 
    Extracts audio from a WAV file using "soundfile" and returns it as an array
    """

    # Use the "soundfile" library to read the audio file
    samplerate, audio_raw = wavfile.read(path_to_files + name_of_file + ".wav")
    audio_array = np.array(audio_raw)
    audio_array = audio_array / 32768.0  # Normalize the audio array to -1/1 (0 dB)

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

    # Conver back to time and take only real values, as real sound isn't imaginary :) (unlike my best friend :( )
    audio_ifft = np.real(np.fft.ifft(audio_fft))

    return audio_ifft


# ===========================
# === Plotting Functions ====
# ===========================

def plot_time_domain(audio_array, samplerate, name_of_plot, show_plot=True):
    """ 
    Plots the time domain of an audio signal using an array from "soundfile"
    """

    max_amplitude = np.max(np.abs(audio_array))

    # Check maximum amplitude
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
    Plots the frequency domain of an audio signal using an array from "soundfile"
    """

    magnitude = np.abs(audio_fft)
    relative_amplitude = magnitude / np.max(magnitude)  # Normalize the magnitude to 0 dB maximum

    # Convert y-axis to dB scale
    audio_fft_log = 20 * np.log10(np.abs(relative_amplitude) + 0.00000000000001) # Encountered log of zero so offset slightly by a very small number to avoid 0 division

    # Plotting frequency domain
    if logascale:
        plt.plot(frequency_axis, audio_fft_log)
        plt.xscale('log')
        plt.ylabel('Magnitude (dB)')
    else:
        plt.plot(frequency_axis, np.abs(relative_amplitude))
        plt.ylabel('Amplitude')
    plt.title(f'{name_of_plot} - Frequency Domain')
    plt.xlabel('Frequency (Hz)')

    # Cutt off the mirror frequencies (above Fs / 2)
    if logascale:
        plt.xlim(1, samplerate / 2)
    else:
        plt.xlim(0, samplerate / 2)

    plt.grid()
    plt.savefig(path_to_output + name_of_plot + '_frequency_domain.pdf') # [:-4 gets rid of .wav]
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

def bandpass_filter(audio_fft, frequency_axis, samplerate, low_cutoff, high_cutoff):

    # These cover the "actual" data from 0 -> Fs / 2
    positive_band = (
        (frequency_axis >= low_cutoff) &
        (frequency_axis <= high_cutoff)
    )

    # These cover the "mirrored" data from Fs / 2 -> Fs
    mirrored_band = (
        (frequency_axis >= samplerate - high_cutoff) &
        (frequency_axis <= samplerate - low_cutoff)
    )

    # This creates a mask using an "OR" operation and applies it to the whole FFT array
    mask = positive_band | mirrored_band

    return np.where(mask, audio_fft, 0)


def bandstop_filter(audio_fft, frequency_axis, samplerate, low_cutoff, high_cutoff):
    """
    Removes a frequency band and its mirrored FFT band.
    """

    # These cover the "actual" data from 0 -> Fs / 2
    positive_band = (
        (frequency_axis >= low_cutoff) &
        (frequency_axis <= high_cutoff)
    )

    # These cover the "mirrored" data from Fs / 2 -> Fs
    mirrored_band = (
        (frequency_axis >= samplerate - high_cutoff) &
        (frequency_axis <= samplerate - low_cutoff)
    )

    # This creates a mask using an "OR" operation and applies it to the whole FFT array
    stop_band = positive_band | mirrored_band

    return np.where(stop_band, 0, audio_fft)

def band_multiplier(audio_fft, frequency_axis, samplerate, low_cutoff, high_cutoff, multiplier):
    """
    Multiplies a frequency band and its mirrored FFT band.
    """

    # These cover the "actual" data from 0 -> Fs / 2
    positive_band = (
        (frequency_axis >= low_cutoff) &
        (frequency_axis <= high_cutoff)
    )

    # These cover the "mirrored" data from Fs / 2 -> Fs
    mirrored_band = (
        (frequency_axis >= samplerate - high_cutoff) &
        (frequency_axis <= samplerate - low_cutoff)
    )

    # Once again, this creates a "mask" using an OR operation and "ANDs" it with the FFT array
    selected_band = positive_band | mirrored_band

    audio_fft_multiplied = np.where(selected_band,audio_fft * multiplier,audio_fft)

    return audio_fft_multiplied

#===========================
#   === Aural Exciter ===
#===========================

# The function definition is really long to allow for useful tweaking of the aural exciter parameters.

def aural_exciter(
    audio_raw, samplerate, name_of_audio,
    high_fundamental_frequency, low_fundamental_frequency,
    band_gap_low_frequency, band_gap_high_frequency,
    high_harmonic_low_cutoff, high_harmonic_high_cutoff,
    low_harmonic_low_cutoff, low_harmonic_high_cutoff,
    harmonic_gain=10,
    mixer_gain=0.5
):
    """
    Enhances the voice in an audio signal using harmonic addition
    """

    # Make the FFT
    audio_fft, frequency_axis = fft_of_audio(audio_raw, samplerate)

    # ============== APPLYING LOW AND HIGH-PASS FILTERS ============

    # First, isolate the two frequency bands
    high_frequency_band = bandpass_filter(audio_fft, frequency_axis, samplerate, high_fundamental_frequency - band_gap_high_frequency, high_fundamental_frequency + band_gap_high_frequency)
    low_frequency_band = bandpass_filter(audio_fft, frequency_axis, samplerate, low_fundamental_frequency - band_gap_low_frequency, low_fundamental_frequency + band_gap_low_frequency)

    # Then, plot the frequency domain of the two bands
    plot_frequency_domain(high_frequency_band, frequency_axis, samplerate, name_of_audio + "_04_upper_input_band", logascale=True, show_plot=show_plots)
    plot_frequency_domain(low_frequency_band, frequency_axis, samplerate, name_of_audio + "_05_lower_input_band", logascale=True, show_plot=show_plots)

    # Then, convert back to time domain to apply the non-linearity
    high_frequency_band_time = inverse_fft(high_frequency_band)
    low_frequency_band_time = inverse_fft(low_frequency_band)

    # ============ GENERATING EXTRA HARMONICS ===============
    # HYPERBOLIC TANGENT
    
    # Then, use a non-linear function to create harmonics in the time domain
    high_frequency_band_time_harmonics = np.tanh(harmonic_gain * high_frequency_band_time)
    low_frequency_band_time_harmonics = np.tanh(harmonic_gain * low_frequency_band_time)

    # ================= FILTERING THE EXTRA HARMONICS =================

    # Then, convert back to frequency domain to filter the harmonics
    high_fft, frequency_axis = fft_of_audio(high_frequency_band_time_harmonics, samplerate)
    low_fft, frequency_axis = fft_of_audio(low_frequency_band_time_harmonics, samplerate)

    # Select useful harmonic regions
    high_fft = bandpass_filter(high_fft, frequency_axis, samplerate, high_harmonic_low_cutoff, high_harmonic_high_cutoff)
    low_fft = bandpass_filter(low_fft, frequency_axis, samplerate, low_harmonic_low_cutoff, low_harmonic_high_cutoff)

    # Check that harmonics are present
    plot_frequency_domain(high_fft, frequency_axis, samplerate, name_of_audio + "_06_upper_band_after_tanh", logascale=True, show_plot=show_plots)
    plot_frequency_domain(low_fft, frequency_axis, samplerate, name_of_audio + "_07_lower_band_after_tanh", logascale=True, show_plot=show_plots)

    # ========== FUSED AUDIO ============

    # Return to time domain
    high_frequency_band_time_harmonics = inverse_fft(high_fft)
    low_frequency_band_time_harmonics = inverse_fft(low_fft)

    # Now, fuse all three together
    fused_audio = audio_raw + mixer_gain * high_frequency_band_time_harmonics + mixer_gain * low_frequency_band_time_harmonics  # Average the three signals together

    fused_audio_fft, frequency_axis = fft_of_audio(fused_audio, samplerate)
    plot_frequency_domain(fused_audio_fft, frequency_axis, samplerate, name_of_audio + "_08_final_aural_excited_spectrum", logascale=True, show_plot=show_plots)

    return fused_audio

#===========================
#   === Main Program  ===
#===========================

for current_audio_name in ["Daniel_5cm", "Daniel_1m"]:

    # Show the plots in Python
    show_plots = False

    # Set output folder for the current recording
    path_to_output = f"Output_Files/{current_audio_name}/"
    os.makedirs(path_to_output, exist_ok=True)

    #==================================
    #   ===   PART ONE - PLOTTING   ===
    #==================================

    # Extract the time domain and frequency domain from the WAV
    raw_audio, samplerate = extract_audio_from_file(current_audio_name)
    fft_audio, frequency_axis = fft_of_audio(raw_audio, samplerate)

    # Use the window function to smooth the edges before plotting the FFT (shows better frequency domain)
    windowed_audio = apply_hamming_window_function(raw_audio)
    windowed_fft, frequency_axis = fft_of_audio(windowed_audio, samplerate)

    # Original signal plotted for analysis
    plot_frequency_domain(windowed_fft, frequency_axis, samplerate, current_audio_name + "_01_original_spectrum_hamming_windowed", logascale=True, show_plot=show_plots)
    plot_time_domain(raw_audio, samplerate, current_audio_name + "_02_original_waveform", show_plot=show_plots)

    #=========================================
    #   ===   PART TWO  - LINEAR FILTERING ===
    #=========================================

    # Enhance the harmonics of Daniel's voice
    for i in range(3):

        fundamental_freq = 100  # Fundamental frequency of Daniel's voice in Hz

        harmonic_freq = fundamental_freq * (i + 1) 
        fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, harmonic_freq - 10, harmonic_freq + 10, 1.5) # Enhance the harmonic frequency by 2x

    filtered_fft = bandpass_filter(fft_audio, frequency_axis, samplerate, 20, 20000) # Humans only hear from 20 - 20,000 Hz
    filtered_fft = bandstop_filter(filtered_fft, frequency_axis, samplerate, 48, 52) # Remove main noise 

    # === Plot the filtered frequency domain ===
    plot_frequency_domain(filtered_fft, frequency_axis, samplerate, current_audio_name + "_03_linear_filtered_spectrum", logascale=True, show_plot=show_plots)

    # ==== Export to WAV again to hear it ====
    inverse_filtered_audio = inverse_fft(filtered_fft)
    create_WAV_file(current_audio_name + "_inverse_filtered", inverse_filtered_audio, samplerate)

    #=========================================
    #   ===   PART THREE - AURAL EXCITER   ===
    #=========================================

    excited_audio = aural_exciter(
        raw_audio,
        samplerate,
        current_audio_name,

        # Input frequency bands - band_gap is the range around the frequency that is kept and "harmonicized"
        high_fundamental_frequency=2250,
        low_fundamental_frequency=100,
        band_gap_low_frequency=30, 
        band_gap_high_frequency=750, 

        # Output harmonic frequency bands - select only the useful harmonics to be reintroduced 
        high_harmonic_low_cutoff=3500,
        high_harmonic_high_cutoff=8000,
        low_harmonic_low_cutoff=200,
        low_harmonic_high_cutoff=1500,

        # Gain of the harmonics and the gain of the mixer responsible for reintroducing the harmonics
        harmonic_gain=10,
        mixer_gain=0.05
)
    create_WAV_file(current_audio_name + "_aurally_excited", excited_audio, samplerate)

