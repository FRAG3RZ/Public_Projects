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
    plt.savefig(path_to_output + name_of_plot + '_frequency_domain.svg') # [:-4 gets rid of .wav]
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
    upper_band_harmonic_gain=10, lower_band_harmonic_gain=10,
    lower_band_mixer_gain=0.5, upper_band_mixer_gain=0.5,
    show_plots = True
):
    """
    Enhances the voice in an audio signal using harmonic addition
    """

    # Check the RMS of the original audio and the two bands
    original_rms = rms(audio_raw)
    print("Original RMS before exciter:", original_rms)

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

    # Non-linear fuctions, including a gain parameter, are used to generate extra harmonics from the isolated bands

    # OPTION 1
    # HYPERBOLIC TANGENT
    
    high_frequency_band_time_harmonics = np.tanh(upper_band_harmonic_gain * high_frequency_band_time)
    low_frequency_band_time_harmonics = np.tanh(lower_band_harmonic_gain * low_frequency_band_time)
    
    # OPTION 2
    # CUBE FUNCTION
    """
    high_frequency_band_time_harmonics = np.power(upper_band_harmonic_gain * high_frequency_band_time, 3)
    low_frequency_band_time_harmonics = np.power(lower_band_harmonic_gain * low_frequency_band_time, 3)
    """
    # ================= FILTERING THE EXTRA HARMONICS =================
    
    # Then, convert back to frequency domain to filter the harmonics
    high_fft, frequency_axis = fft_of_audio(high_frequency_band_time_harmonics, samplerate)
    low_fft, frequency_axis = fft_of_audio(low_frequency_band_time_harmonics, samplerate)
    
    # Select useful harmonic regions
    high_fft = bandpass_filter(high_fft, frequency_axis, samplerate, high_harmonic_low_cutoff, high_harmonic_high_cutoff)
    low_fft = bandpass_filter(low_fft, frequency_axis, samplerate, low_harmonic_low_cutoff, low_harmonic_high_cutoff)

    # Check that harmonics are created and filtered
    plot_frequency_domain(high_fft, frequency_axis, samplerate, "_06_higher_band_harmonics", logascale=True, show_plot=show_plots)
    plot_frequency_domain(low_fft, frequency_axis, samplerate, "_07_lower_band_harmonics", logascale=True, show_plot=show_plots)
    
    # Return to time domain
    high_frequency_band_time_harmonics = inverse_fft(high_fft)
    low_frequency_band_time_harmonics = inverse_fft(low_fft)

    # Check the RMS of generated, and filtered, harmonics
    print("Upper harmonic RMS:", rms(high_frequency_band_time_harmonics))
    print("Lower harmonic RMS:", rms(low_frequency_band_time_harmonics))
    
    # ========== FUSED AUDIO & RMS NORMALIZATION ============

    # Remove the unwanted frequencies from the original audio
    audio_fft = bandpass_filter(audio_fft, frequency_axis, samplerate, 20, 20000) # Humans only hear from 20 - 20,000 Hz
    audio_fft = bandstop_filter(audio_fft, frequency_axis, samplerate, 0, 60, sigma=10) # Remove the "hum" of the environment (lower sigma to not eat away at the bass of the voice)
    filtered_audio = inverse_fft(audio_fft)

    # ===== Now, fuse all three together in the mixer =====
    fused_audio = filtered_audio + upper_band_mixer_gain * high_frequency_band_time_harmonics + lower_band_mixer_gain * low_frequency_band_time_harmonics 

    # RMS of the fused audio
    fused_rms = rms(fused_audio)
    print("Fused audio RMS:", rms(fused_audio))

    # Normalize the fused audio to the original RMS to retain - > WHISPERS = WHISPERS & YELLS = YELLS
    fused_audio = fused_audio * (original_rms / fused_rms)

    # ============== PLOTTING THE FINAL AUDIO ==============

    # Apply Hamming window FOR PLOTTING ONLY -> this does not affect the actualy audio
    windowed_fused_audio = apply_hamming_window_function(fused_audio)
    fused_audio_fft, frequency_axis = fft_of_audio(windowed_fused_audio, samplerate)

    plot_frequency_domain(fused_audio_fft, frequency_axis, samplerate, name_of_audio + "_08_final_aural_excited_spectrum", logascale=True, show_plot=show_plots)

    return fused_audio


# ================
# ===== MAIN =====
# ================

def main():

    show_plots = True
    global path_to_output

    # ============================================
    # ========= 5cm audio enhancement =============
    # ============================================
        
    current_audio_name = "original_speech_5cm"

    path_to_output = f"Output_Files/{current_audio_name}/"
    os.makedirs(path_to_output, exist_ok=True)

    # Extract the time domain and frequency domain from the WAV
    raw_audio, samplerate = extract_audio_from_file(current_audio_name)

    excited_audio = aural_exciter(
        raw_audio,
        samplerate,
        current_audio_name,

        # Input frequency bands
        high_fundamental_frequency=2300,
        low_fundamental_frequency=120,
        band_gap_low_frequency=40,
        band_gap_high_frequency=50,

        # Output harmonic frequency bands
        high_harmonic_low_cutoff=6000,
        high_harmonic_high_cutoff=8000,
        low_harmonic_low_cutoff=250,
        low_harmonic_high_cutoff=850,

        # Harmonic generation and mixing
        upper_band_harmonic_gain=5,
        lower_band_harmonic_gain=6,
        lower_band_mixer_gain=0.6,
        upper_band_mixer_gain=0.5,

        show_plots=show_plots
    )
    create_WAV_file("exciter_speech", excited_audio, samplerate)

if __name__ == "__main__":
    main()