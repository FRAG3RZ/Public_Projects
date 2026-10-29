# Required imports

from ecg_plot import *

# ============ ASSIGNMENT PART TWO ====================

def kaiser_variable_helper(A, deltaOmega):
    """
    Calculates the required variables for the Kaiser Window using the formulas in the lectures
    """

    # Implement the empyrical piecewise operation for Beta
    if(A > 50):
        beta = 0.1102 * (A - 8.7)
    elif(A<=50 and A>=21):
        beta = 0.5842 * (A - 21)**0.4 + 0.07886 * (A - 21)
    else:
        beta = 0

    # Cast to integer for later calculations, and add 1 because int() rounds down, and we want an M larger than the "minimum" recommended
    M = int((A - 8) / (2.285 * deltaOmega)) + 1 

    # Ensure the FIR filter has an odd number of taps, so the middle index lays at an integer, and NOT a half
    if M % 2 == 0:
        M += 1

    return M, beta


def kaiser_window_function(h, beta, alpha):
    """
    Ammplies a Kaiser Window Function to the input array "h"
    """

    # Generate sample indices from 0 to N-1
    n = np.arange(len(h))

    # Calculate the Kaiser window from the mathematical formula in the lecture slides
    window = np.i0(beta * np.sqrt(1 - ((n - alpha) / alpha)**2)) / np.i0(beta)

    # Apply the Kaiser window by multiplying h
    h *= window

    return h

def calculate_FIR_coefficients(bandstop_frequency_array, sampling_rate, remove_DC = True, side_lobe_decay_dB=60, transition_width_rad=0.05):
    """
    Calculates the FIR coefficients

    Bandstop_frequency_array should be a two-dimensional array of integer pairs, representing the start and stop frequencies of the stopbands

    Example: 
        stopbands = np.array([
            [45, 55],     # Remove 50 Hz interference
            [55, 65],     # Remove 60 Hz interference (if we want to also remove US mains noise for example)
        ])
    """

    # Calculate M from the Kaiser method. 
    # If A and deltaOmega aren't specified in the function arguments, use the defaults we found most effective
    M, beta = kaiser_variable_helper(side_lobe_decay_dB, transition_width_rad)

    # Also report the resulting delay and resolution
    group_delay = M / (2*sampling_rate)   
    print(f"\nThe Kaiser-calculated tap number, M, is: {M} \n\t resulting in a frequency resolution of: {(sampling_rate / M ):0.3f} Hz \n\t and group delay of: {group_delay} seconds\n")

    # Calculate the middle index (M is always odd) -> cast to integer to round down to the correct index
    middle = int(M / 2)

    # prepare the variable to store all stopbands' frequency representation
    final_frequency_window = np.ones(M)

    for stopband in bandstop_frequency_array:

        # calculate the correct position of the stopband in terms of tap number M
        k1 = int( (stopband[0] / sampling_rate) * M)
        k2 = int( (stopband[1] / sampling_rate) * M)

         # always maintains symmetry around the M/2 point -> linear phase filter to maintain constant group delay!
        final_frequency_window[k1: k2+1] = 0 # zero out stopband in the shared frequency window
        final_frequency_window[M - k2: M - k1+1] = 0 # zero out mirror stopband in the shared frequency window

    if remove_DC:
        final_frequency_window[0] = 0 # zero out first tap -> DC HAS NO MIRROR!

    # Plot the window to check
    frequency_axis = np.arange(middle) * sampling_rate / M # Create frequency axis in Hz (positive frequencies only -> up to "M/2")
    # Don't normalize this, as we want to see the 0 dB for full pass amplitude -> unlike real voltage signals which we normalize for graphing by 1 / N
    plot_frequency_domain(final_frequency_window[0 : middle], frequency_axis, sampling_rate, "Desired_FIR_Frequency_Response", normalize=False, y_label="Gain") 

    # Move the window from the frequency domain to the tap domain: X[K] -> x[n] & ensure it is real
    x = inverse_fft(final_frequency_window)

    # prepare the Impulse Response array
    h = np.zeros(M)

    # Into the first half move the second half of the Impulse Response x[n] AND VICE VERSA
    # Use the correct center calculated above as M is always odd
    h[0 : middle] = x[middle + 1: M] 
    h[middle : M] = x[0 : middle + 1]

    # Apply the Kaiser window function for the intended filter response
    h = kaiser_window_function(h, beta, middle)

    return h