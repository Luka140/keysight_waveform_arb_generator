import scipy.signal.windows as windows
import numpy as np
import matplotlib.pyplot as plt
import pathlib 
from datetime import datetime

import os

_current_time = str(datetime.now().time()).replace(".", "-").replace(":", "_") # No periods in filename


# ----------- SETTINGS -------------------------------------------------------
frequency               = 50e3               # Hz
nr_cycles               = 3 
sample_rate             = 250 * 10**6  
peak_to_peak_voltage    = 6                  # Volts

filename                = f"waveform{int(frequency)}Hz_{int(nr_cycles)}cycles_{int(peak_to_peak_voltage)}Vpp_{_current_time}.arb"
filepath                = pathlib.Path.cwd() / "signals" 
# ----------------------------------------------------------------------------
if not filepath.exists():
    os.mkdir(filepath)

t_end = nr_cycles / frequency
time = np.linspace(0, t_end, int(t_end * sample_rate))
unit_voltage = np.sin(2 * np.pi * frequency * time)


hann_window = windows.hann(len(time))

unit_windowed_signal = unit_voltage * hann_window 

# Set voltage to peak to peak
windowed_signal = unit_windowed_signal * ( 1 / np.max(np.abs(unit_windowed_signal))) * peak_to_peak_voltage / 2 
print(f"Maximum amplitude: {np.max(np.abs(windowed_signal))} v")

# Plot to check
plt.plot(time, windowed_signal)
plt.title(f"Hann windowed {nr_cycles} cycle sine wave ({frequency}) Hz")
plt.ylabel("Voltage")
plt.xlabel("Time (s)")
plt.show()


# ----- Format: 
#File Format:1.10
#Channel Count:1
#Sample Rate:250000000
#High Level:3
#Low Level:-3
#Filter:"NORMAL"
#Data Points:15000
#Data:
#0
#41
#82
#124

max_val_16bit_int   = 32767
scaled_voltage_float = max_val_16bit_int * unit_windowed_signal / (np.max(np.abs(unit_windowed_signal)))
scaled_voltage_float[scaled_voltage_float >= 0] = np.floor(scaled_voltage_float[scaled_voltage_float >= 0])
scaled_voltage_float[scaled_voltage_float < 0] = np.ceil(scaled_voltage_float[scaled_voltage_float < 0])
scaled_voltage = scaled_voltage_float.astype(int)

# Save to csv:
path = filepath / filename
path.touch()

with open(path, 'w') as f:
    f.write("File Format:1.10\n")
    f.write("Channel Count:1\n")
    f.write(f"Sample Rate:{sample_rate}\n")
    f.write(f"High Level:{peak_to_peak_voltage/2}\n")
    f.write(f"Low Level:-{peak_to_peak_voltage/2}\n")
    f.write(f'Filter:"NORMAL"\n')
    f.write(f'Data Points:{scaled_voltage.size}\n')
    f.write("Data:\n")

    for val in scaled_voltage:
        f.write(f"{val}\n")
    
print(f"Waveform saved at: {path}")