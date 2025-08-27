"""
This file shows examples on how to use the Bdot_reconstruct Python script in order to better analyze the 
data without having to do so much code. Simplifies and streamlines data reading for Bdots.
"""

import numpy as np
from Bdot_reconstruct import Data_cleaner, Bdot_actions, Plotting_Functions
import matplotlib.pyplot as plt

'''

#This is how you call the data
Run1_data = Data_cleaner(calibration_data, run_data)
Run1_data.oscilloscope_data()
MSO24_Ch4 = Run1_data.MSO24_Ch4_Trace
MSO24_time = Run1_data.MSO24_Time
print(type(MSO24_Ch4), 'Type for Ch4')

Bdot = Bdot_actions(calibration_data, run_data) # This will intialize the class and place the data as objects
Bdot.oscilloscope() # This will allow you to access all the files in the HDF5 file, not just the oscilloscope
effective_area = Bdot.B_dot_calibration(imaginary = False)
print(f'The effective area is: {effective_area}')
'''

calibration_data = "1INCAP_2.TXT"
run_data = "magnet-calibration-pat-ground-2025-05-27.h5"

Bdot = Bdot_actions(calibration_data, run_data) # This will intialize the class and place the data as objects
Bdot.oscilloscope_data() # This will allow you to access all the files in the HDF5 file, not just the oscilloscope
effective_area = Bdot.B_dot_calibration(imaginary = False)
print(f'The effective area is: {effective_area}')

#If you want to get the reconstructed field
MSO24_Ch4 = Bdot.MSO24_Ch4_Trace
MSO24_time = Bdot.MSO24_Time

field = Bdot.B_field_reconstruct(MSO24_Ch4, MSO24_time)
print(f'The reconstructed field is: {field[0]}')
plt.plot(field)
#plt.show()
