"""
This file shows examples on how to use the Bdot_reconstruct Python script in order to better analyze the 
data without having to do so much code. Simplifies and streamlines data reading for Bdots.
"""

import numpy as np
from Bdot_reconstruct import Data_cleaner, Bdot_actions, Plotting_Functions
import matplotlib.pyplot as plt


calibration_data = "1INCAP_2.TXT"
run_data = "magnet-calibration-pat-ground-2025-05-27.h5"
#This is how you call the data
Run1_data = Data_cleaner(calibration_data, run_data)
Run1_data.oscilloscope_data()
MSO24_Ch4 = Run1_data.MSO24_Ch4_Trace
MSO24_time = Run1_data.MSO24_Time
print(type(MSO24_Ch4), 'Type for Ch4')
Bdot = Bdot_actions(Run1_data)

field = Bdot_actions.B_field_reconstruct(MSO24_Ch4, MSO24_time)
print(field, 'This is the field')

plot = Plotting_Functions(Run1_data)
max_b_field = plot.max_b_field(Channels = ['LeCroy:Ch1:Trace', 'LeCroy:Ch2:Trace'])
print(max_b_field)

