"""
This file shows examples on how to use the Bdot_reconstruct Python script in order to better analyze the 
data without having to do so much code. Simplifies and streamlines data reading for Bdots.
"""

import numpy as np
from Bdot_reconstruct import Data_cleaner, Bdot_actions, Plotting_Functions
import matplotlib.pyplot as plt

#This is how you call the data

calibration_data = "1INCAP_2.TXT"
run_data = "magnet-calibration-pat-ground-2025-05-27.h5"

Bdot = Bdot_actions(calibration_data, run_data) # This will intialize the class and place the data as objects
Bdot.oscilloscope_data() # This will allow you to access all the files in the HDF5 file, not just the oscilloscope

#This is how you get the effective_area
effective_area = Bdot.B_dot_calibration(imaginary = False) #Set imaginary True if the .TXT files are in real and imaginary format instead of phase and frequency
print(f'The effective area is: {effective_area}')

#If you want to get the reconstructed field. The effective area and other factors are taken into account after calculating effective area
MSO24_Ch4 = Bdot.MSO24_Ch4_Trace
MSO24_time = Bdot.MSO24_Time

field = Bdot.B_field_reconstruct(MSO24_Ch4, MSO24_time)
print(f'The reconstructed field is: {field[0]}')
plt.plot(field)
plt.show()
