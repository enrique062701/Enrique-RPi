"""
This file shows examples on how to use the Bdot_reconstruct Python script in order to better analyze the 
data without having to do so much code. Simplifies and streamlines data reading for Bdots.
"""

import numpy as np
from Bdot_reconstruct import Data_cleaner, Bdot_actions
import matplotlib.pyplot as plt


calibration_data = "1INCAP_2.TXT"
run_data = "magnet-calibration-pat-ground-2025-05-27.h5"
#This is how you call the data
Run1_data = Data_cleaner(calibration_data, run_data)
Run1_data.oscilloscope_data()
MSO24_Ch4 = Run1_data.MSO24_Ch4
MSO24_time = Run1_data.MSO24_time
print(type(MSO24_Ch4), 'Type for Ch4')

field = Bdot_actions.B_field_reconstruct(MSO24_Ch4, MSO24_time)
print(field)

plt.plot(field)
plt.show()

volts = []
time = []
field = []
field_max = []
field_list = []
file_path = '/home/phoenix/Enrique-RPi/Bdot_calibrations/magnet_data'
positions = np.arange(0,22,1)
for i in range(22):
    filename = f'{file_path}/magnetZscan-{i}cm-2025-06-16.h5'
    data = Data_cleaner(calibration_data, filename)
    data.oscilloscope_data()

    voltage = data.MSO24_Ch1
    time = data.MSO24_time
    field = Bdot_actions.B_field_reconstruct(voltage, time)
    max_ = np.max(field)
    print(max_, 'This is the max for this case')
    field_max.append(max_)
    field_list.append(field)
    volts.append(voltage)
    time.append(time)

plt.plot(positions, field_max, label = 'Field strength')
plt.legend()
plt.show()


