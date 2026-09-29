# --- CONFIG -------------------------------------------------------------------
MODE = "time"   # choose "time" or "fft"
CSV_FILE = "../lab3/CSV/scope_7.csv"
# ------------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.ticker import AutoMinorLocator
import numpy as np
import scipy

# optional SciPy peak finding
try:
    from scipy.signal import find_peaks
    SCIPY = True
except ImportError:
    SCIPY = False

# === 1. Load CSV ===
df = pd.read_csv(CSV_FILE)
import matplotlib.ticker as mticker
from matplotlib.ticker import AutoMinorLocator
import numpy as np
import scipy

# optional SciPy peak finding
try:
    from scipy.signal import find_peaks
    SCIPY = True
except ImportError:
    SCIPY = False

# === 1. Load CSV ===
df = pd.read_csv(CSV_FILE)

# === 2. Select columns ===
x_col = df.columns[0]
y_col = df.columns[1]

# Convert to numeric and drop NaNs
x = pd.to_numeric(df[x_col], errors="coerce")
y = pd.to_numeric(df[y_col], errors="coerce")
mask = x.notna() & y.notna()
x, y = x[mask], y[mask]

# === 3. Mode-specific setup ===
if MODE.lower() == "time":
    y_plot = y * 1000.0
    title = "Signal"
    x_label = "Time [Seconds]"
    y_label = "Amplitude [mV]"
    plot_label = "200 Hz; 200mV"
    x_lim = (x.min(), x.max())
    y_lim = (y_plot.min(), y_plot.max())

elif MODE.lower() == "fft":
    y_plot = y  # no scaling
    title = "FFT Spectrum - 1 kHz Carrier"
    x_label = "Frequency [Hz]"
    y_label = "Amplitude [dBV]"
    plot_label = "Fc - 1kHz"
    x_lim = (0, 2000)          # limit 0–2 kHz
    y_lim = (y_plot.min(), -15)  # bottom auto, top limited to -24 dBV
else:
    raise ValueError("MODE must be either 'time' or 'fft'")

# === 4. Plot ===
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y_plot, linewidth=1, label=plot_label)

# === 5. FFT peak annotation ===
if MODE.lower() == "fft":
    # Only search within the visible range
    mask = (x >= x_lim[0]) & (x <= x_lim[1])
    x_vis = np.array(x[mask])
    y_vis = np.array(y_plot[mask])

    if SCIPY:
        peaks, props = find_peaks(y_vis, prominence=2.0, distance=20)
    else:
        # Fallback: simple peak detection
        peaks = np.where((y_vis[1:-1] > y_vis[:-2]) & (y_vis[1:-1] > y_vis[2:]))[0] + 1

    # Sort by amplitude and keep top 6
    top_peaks = sorted(peaks, key=lambda i: y_vis[i], reverse=True)[:9]

    for i in top_peaks:
        fx, fy = x_vis[i], y_vis[i]
        ax.plot(fx, fy, "o", color="red", markersize=5)
        ax.annotate(
            f"{fx:.0f} Hz\n{fy:.1f} dBV",
            xy=(fx, fy),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.7),
        )

# === 6. Apply limits ===
ax.set_xlim(*x_lim)
ax.set_ylim(*y_lim)

# === 7. Clean tick density ===
ax.xaxis.set_major_locator(mticker.MaxNLocator(nbins=8))
ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=6))
ax.xaxis.set_minor_locator(AutoMinorLocator(2))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))

# === 8. Labels & styling ===
ax.set_title(title)
ax.set_xlabel(x_label)
ax.set_ylabel(y_label)
ax.grid(True, which="both", linestyle="--", alpha=0.4)
ax.legend()
fig.tight_layout()

plt.show()