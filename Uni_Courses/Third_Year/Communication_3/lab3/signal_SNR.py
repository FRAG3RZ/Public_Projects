import numpy as np
import pandas as pd

def generate_signal_csv(filename="signal.csv", n_points=300, snr_db=None, signal_rms=0.144):

    # Generate random binary base signal
    base_base_signal = np.random.randint(0, 2, size=n_points)

    # Expand each sample into 10 repeated samples
    base_signal_repeat = np.repeat(base_base_signal, 10)

    base_signal = base_signal_repeat - 0.5

    #PAM

    PAM4_signal = np.random.randint(0, 4, size=n_points) / 3

    PAM4_repeat = np.repeat(PAM4_signal, 10)

    PAM4_signal_mean_zero = PAM4_repeat - 0.5

    # If no SNR specified → save pure (expanded) binary signal
    if snr_db is None:
        df = pd.DataFrame({'value': base_base_signal})
        df.to_csv(filename, index=False, header = False)
        print(f"Saved pure binary signal → {filename}")

        dg = pd.DataFrame({'value': PAM4_repeat})
        dg.to_csv(f"PAM4_{filename}", index=False, header = False)
        return

    snr_db = snr_db + 3

    # Correct noise RMS formula
    noise_rms = signal_rms / (10 ** (snr_db / 20))

    print(f"Noise RMS for {snr_db} SNR is: {noise_rms}")

    # Add Gaussian noise
    noise = np.random.normal(0, noise_rms, len(base_signal))

    noisy_signal = base_signal * signal_rms + noise
    noisy_signal_offset_bleh = noisy_signal + (signal_rms / 2)

    noisy_signal_PAM = PAM4_signal_mean_zero * signal_rms + noise
    noisy_signal_PAM_offset_bleh = noisy_signal_PAM + (signal_rms / 2)

    noisy_signal_offset = (noisy_signal_offset_bleh - noisy_signal_offset_bleh.max()) / (noisy_signal_offset_bleh.max() - noisy_signal_offset_bleh.min())

    noise_signal_PWM_offset = (noisy_signal_PAM_offset_bleh - noisy_signal_PAM_offset_bleh.max()) / (noisy_signal_PAM_offset_bleh.max() - noisy_signal_PAM_offset_bleh.min())

    # Save to CSV
    df = pd.DataFrame({'value': noisy_signal_offset})
    df.to_csv(filename, index=False, header=False)

    df = pd.DataFrame({'value': noise_signal_PWM_offset})
    df.to_csv(f"PAM4_{filename}", index=False, header=False)

    print(f"Saved noisy signal with SNR = {snr_db} dB → {filename}")

#WE NEED TO FIRST SHIFT THE SIGNAL TO MAKE IT BETWEEN - 0.144/2 AND 0.144/2, BECAUSE THE NOISE = NP.RANDOM.NORMAL IS ONLY VALID FOR STANDARD DEVIATION OF NOISE RMS WHEN THE MEAN IS ZERO

# === Example usage ===
# Just random 0/1 signal
generate_signal_csv("pure_binary.csv")

# Add noise for 24 dB SNR
generate_signal_csv("noisy_signal_24dB.csv", snr_db=24)

# Add noise for 24 dB SNR
generate_signal_csv("noisy_signal_18dB.csv", snr_db=18)

# Add noise for 12 dB SNR
generate_signal_csv("noisy_signal_12dB.csv", snr_db=12)

# Add noise for 12 dB SNR
generate_signal_csv("noisy_signal_9dB.csv", snr_db=9)

generate_signal_csv("noisy_signal_6dB.csv", snr_db=6)
