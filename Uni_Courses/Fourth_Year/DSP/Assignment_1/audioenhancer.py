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
    Extracts audio from a WAV file using "soundfile" and returns it as an array
    """

    # Use the "soundfile" library to read the audio file
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
    Plots the time domain of an audio signal using an array from "soundfile"
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
    Plots the frequency domain of an audio signal using an array from "soundfile"
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


#===========================
#=== Filtering Functions ===
#===========================


def bandpass_filter(audio_fft, frequency_axis, samplerate,
                    low_cutoff, high_cutoff, sigma=20):

    # Convert mirrored FFT frequencies into their positive equivalents for the gaussian attenutation to pass over them correctly
    frequency = np.where(
        frequency_axis <= samplerate / 2,
        frequency_axis,
        samplerate - frequency_axis
    )

    # Distance from the passband (zero for frequencies inside)
    distance = np.maximum(low_cutoff - frequency, 0) + np.maximum(frequency - high_cutoff, 0)

    # Gaussian roll-off outside the passband
    mask = np.exp(-0.5 * (distance / sigma)**2)

    # Apply the smooth frequency mask
    return audio_fft * mask


# Same as band pass, but the guassian mask is inverted instead
def bandstop_filter(audio_fft, frequency_axis, samplerate,
                    low_cutoff, high_cutoff, sigma=20):

    # Convert mirrored FFT frequencies into their positive equivalents for the gaussian attenutation to pass over them correctly
    frequency = np.where(
        frequency_axis <= samplerate / 2,
        frequency_axis,
        samplerate - frequency_axis
    )

    # Distance from the stopband (zero for frequencies inside)
    distance = np.maximum(low_cutoff - frequency, 0) + np.maximum(frequency - high_cutoff, 0)

    # Gaussian attenuation around the stopband
    mask = np.exp(-0.5 * (distance / sigma)**2)

    # Invert the mask to reject rather than pass the selected frequencies
    return audio_fft * (1 - mask)



def band_multiplier(audio_fft, frequency_axis, samplerate,
                    low_cutoff, high_cutoff, dB_gain, sigma=20):
    """
    Smoothly boosts or attenuates a frequency band and its mirrored FFT band.
    Low sigma means sharper transitions
    """

    # Convert dB gain to linear multiplication
    multiplier = 10 ** (dB_gain / 20)

    # Generate Gaussian mask using the existing bandpass filter
    mask = bandpass_filter(
        np.ones_like(frequency_axis),
        frequency_axis,
        samplerate,
        low_cutoff,
        high_cutoff,
        sigma # Low sigma means sharper transitions and vice versa
    )

    # Smoothly apply the gain according to the Gaussian mask
    audio_fft_multiplied = audio_fft * (1 + (multiplier - 1) * mask)

    return audio_fft_multiplied

# ================
# ===== MAIN =====
# ================

def main():

    show_plots = False

    # Make sure the proper output path is used
    global path_to_output

    # ========= ====================================
    # ========== 5cm audio enhancement =============
    # ========= ====================================
    
    current_audio_name = "original_speech_5cm"

    # Set output folder for the current recording
    path_to_output = f"Output_Files/{current_audio_name}/"
    os.makedirs(path_to_output, exist_ok=True)

    # Extract the time domain and frequency domain from the WAV
    raw_audio, samplerate = extract_audio_from_file(current_audio_name)
    fft_audio, frequency_axis = fft_of_audio(raw_audio, samplerate)

    # ====== Settings found from the Mixer in the DSP Rankine Lab =======

    # Low-frequency bass
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 100, 200, dB_gain=3.5, sigma=20)
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 280, 380, dB_gain=3.5, sigma=40)

    # Reduce boxiness without removing too much -> high attenuation leads to "dull" voice
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 600, 1000, dB_gain=-4, sigma=120)

    # High-frequency presence boost -> resonanted quite well with Daniel's voice
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 7500, 8500, dB_gain=5, sigma=250)

    # ====== Settings mirrored from the SM58 microphone =======

    # High-frequency roll-off -> higher sigma to be smoother
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 11000, 13000, dB_gain=-4, sigma=500)
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 13500, 20000, dB_gain=-5, sigma=1000)

    # Noise filtering
    filtered_fft = bandpass_filter(fft_audio, frequency_axis, samplerate, 20, 20000, sigma=20) # Inaudible to humans anyway
    filtered_fft = bandstop_filter(filtered_fft, frequency_axis, samplerate, 0, 65, sigma=10) # Removes most background "hum", human voice isn't present there anyway

    # Inverse FFT & Export
    inverse_filtered_audio = inverse_fft(filtered_fft)
    create_WAV_file("enhanced_speech_5cm", inverse_filtered_audio, samplerate)

    # =========== Plotting ============

    # Apply Hamming window FOR PLOTTING ONLY -> this does not affect the actualy audio 
    windowed_filtered_audio = apply_hamming_window_function(inverse_filtered_audio)
    windowed_filtered_fft, frequency_axis = fft_of_audio(windowed_filtered_audio, samplerate)

    # Plot the windowed spectrum
    plot_frequency_domain(windowed_filtered_fft, frequency_axis, samplerate, "_enhanced_speech_5cm_linear_filtered_spectrum", logascale=True, show_plot=show_plots)


    # ============================================================================================================================================================


    # ============================================
    # ========= 1m audio enhancement =============
    # ============================================
    
    current_audio_name = "original_speech_1m"

    # Set output folder for the current recording
    path_to_output = f"Output_Files/{current_audio_name}/"
    os.makedirs(path_to_output, exist_ok=True)

    # Extract the time domain and frequency domain from the WAV
    raw_audio, samplerate = extract_audio_from_file(current_audio_name)
    fft_audio, frequency_axis = fft_of_audio(raw_audio, samplerate)

    # ====== Settings found from the Mixer in the DSP Rankine Lab =======

    # Low-frequency bass
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 100, 200, dB_gain=6, sigma=40)
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 280, 380, dB_gain=6, sigma=50)

    # Reduce boxiness without removing too much -> high attenuation leads to "dull" voice
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 600, 1000, dB_gain=-3, sigma=120)

    # High-frequency presence boost -> resonanted quite well with Daniel's voice
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 7500, 8500, dB_gain=5, sigma=500)

    # ====== Settings mirrored from the SM58 microphone =======

    # High-frequency roll-off -> higher sigma to be smoother
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 11000, 13000, dB_gain=-2, sigma=500)
    fft_audio = band_multiplier(fft_audio, frequency_axis, samplerate, 13500, 20000, dB_gain=-5, sigma=500)

    # Noise filtering
    filtered_fft = bandpass_filter(fft_audio, frequency_axis, samplerate, 20, 20000, sigma=20) # Inaudible to humans anyway
    filtered_fft = bandstop_filter(filtered_fft, frequency_axis, samplerate, 0, 65, sigma=10) # Removes most background "hum", human voice isn't present there anyway

    # Inverse FFT & Export
    inverse_filtered_audio = inverse_fft(filtered_fft)
    create_WAV_file(current_audio_name + "enhanced_speech_1m", inverse_filtered_audio, samplerate)

    # =========== Plotting ============

    # Apply Hamming window FOR PLOTTING ONLY -> this does not affect the actualy audio 
    windowed_filtered_audio = apply_hamming_window_function(inverse_filtered_audio)
    windowed_filtered_fft, frequency_axis = fft_of_audio(windowed_filtered_audio, samplerate)

    # Plot the windowed spectrum
    plot_frequency_domain(windowed_filtered_fft, frequency_axis, samplerate, "_enhanced_speech_1m_linear_filtered_spectrum", logascale=True, show_plot=show_plots)
    

if __name__ == "__main__":
    main()