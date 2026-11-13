import numpy as np
import pandas as pd
import nidaqmx
from nidaqmx.stream_readers import AnalogSingleChannelReader

# Parameters
input_pin = 0           # analog in for reading HY810H output
trigger_pin = 8         # digital pin for ADMET trigger
input_bounds = (0,5)    # analog input expected range in V
sample_rate = 2         # Hz
sample_time = 30*60     # s
sample_count = sample_rate*sample_time


# Setup
local_system = nidaqmx.system.System.local()
device_names = [device.name for device in local_system.devices]
device_name = device_names[0]

# Task configurations
input_channel = f"{device_name}/ai{input_pin},"
terminal_config = nidaqmx.constants.TerminalConfiguration.RSE



with nidaqmx.Task() as read_task:
    # Configure input channel
    read_task.ai_channels.add_ai_voltage_chan(input_channel,
                                            min_val=input_bounds[0], max_val=input_bounds[1],
                                            terminal_config=terminal_config)

    read_task.timing.cfg_samp_clk_timing(rate=sample_rate,
                                        sample_mode=nidaqmx.constants.AcquisitionType.FINITE,           # we know the number of samples to collect
                                        samps_per_chan=sample_count)
                                                                        
    
    
    # Set the combined task start trigger if given one
    read_task.triggers.start_trigger.cfg_dig_edge_start_trig(f"/{device_name}/PFI{trigger_pin}",trigger_edge=nidaqmx.constants.Edge.FALLING)

    # Read data
    reader = AnalogSingleChannelReader(read_task.in_stream) 
    data = np.zeros(sample_count)
    reader.read_many_sample(data,number_of_samples_per_channel=sample_count,timeout=nidaqmx.constants.WAIT_INFINITELY)

# Save to CSV
time = np.arange(len(data)) / sample_rate
df = pd.DataFrame({
    'Time': time,
    'HY810H Signal (V)': data
})

df.to_csv('30MinTestNIDAQ.csv', index=False)