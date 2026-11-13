from SamplingFuncs.Daq6421 import Daq6421
from SamplingFuncs.CalibrationFunctions import generate_waveform
import numpy as np
import matplotlib.pyplot as plt


# Parameters
sample_rate = 20000     # Hz
sample_time = 2         # s
t = np.arange(0, sample_time + 1/sample_rate, 1/sample_rate)
fake_output = 0*t

# Connect to the DAQ and get data with the above wave form
my_daq = Daq6421()
my_daq.setup()

data = my_daq.read_write_AiAo(sample_rate,fake_output,{0},{0},(0,5),False)

# Plot data
t = np.arange(0, sample_time + 1/sample_rate, 1/sample_rate)
plt.plot(t, data)
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.show()

