import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO
import h5py
from scipy.integrate import cumulative_trapezoid

'''
This file calibrates and reconstructs the bdot and bfield. Object oriented programming because it will be used
for future calibrations. Inspired by Nathan Bowers from Gettysburg. Modified and reconstructed the calibration to be 
better suited for Phoenix Laser Lab and easier to understand
Author: Enrique
'''

class Data_cleaner:
    """
    This class calls all the calibration functions. So far it is only for the 1axis Bdot because it is essential
    to calibrate the magnetic field. Will add more in the future. Must pass both together
    """
    def __init__(self, calibration_data, HDF5_data_):
        self.calibration_data = calibration_data
        self.HDF5_data = h5py.File(HDF5_data_, 'r')
        

    def clean_data_cal(self):
        """
        This method loads the calibration data for the bdot. This is the .TXT file that is attained from the
        network analyzer. Cleans the data and returns a pandas dataframe. Will be used to calibrate it once ready.
        """
        with open(self.calibration_data, 'r') as f:
            lines = f.readlines()
        data_start = next(i for i, line in enumerate(lines) if line.strip().startswith('1.'))
        data_lines = lines[data_start:]
        data_str = "".join(data_lines)
        BP_ = pd.read_csv(StringIO(data_str), sep= '\t', header = None, names = ["Frequency", "Gain", "Phase"])
        return BP_

    def oscilloscope_data(self):
        """
        This method loads the HDF5 file and splits it into corresponding variables for important traces. This will get all the 
        oscilloscope channels to their own numpy arrays. Need to pass different.
        Assigning each classs to an attribute so that I do not have to return each channel. Example code usage:
            position10_100V = Data_cleaner(myfile.hdf5)
            position10_100V.oscilloscope_data()
            position10_100V.LeCroy_Ch1 --> Or any channel. Can call any channel like this
        Can also assign each channel to its own variable so that you do not have to type the whole thing:
            MSO24_Ch1 = position10_100V.MSO24_Ch1
        
        Add error handling. If one of the scopes isnt active then make sure it does not crash

        """
        
            
        self.LeCroy_Ch1 = np.array(self.HDF5_data['LeCroy:Ch1:Trace'])
        self.LeCroy_Ch2 = np.array(self.HDF5_data['LeCroy:Ch2:Trace'])
        self.LeCroy_Ch3 = np.array(self.HDF5_data['LeCroy:Ch3:Trace'])
        self.LeCroy_Ch4 = np.array(self.HDF5_data['LeCroy:Ch4:Trace'])
        self.LeCroy_time = np.array(self.HDF5_data['LeCroy:Time'])

        self.MSO24_Ch1 = np.array(self.HDF5_data['MSO24:Ch1:Trace'])
        self.MSO24_Ch2 = np.array(self.HDF5_data['MSO24:Ch2:Trace'])
        self.MSO24_Ch3 = np.array(self.HDF5_data['MSO24:Ch3:Trace'])
        self.MSO24_Ch4 = np.array(self.HDF5_data['MSO24:Ch4:Trace'])
        self.MSO24_time = np.array(self.HDF5_data['MSO24:Time'])

        #self.MDO30_Ch1 = np.array(self.HDF5_data['MDO30:Ch1:Trace'])
        #self.MDO30_Ch2 = np.array(self.HDF5_data['MDO30:Ch2:Trace'])
        #self.MDO30_Ch3 = np.array(self.HDF5_data['MDO30:Ch3:Trace'])
        ##self.MDO30_time = np.array(self.HDF5_data['MDO30:Time'])



class Bdot_actions(Data_cleaner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def B_field_reconstruct(voltage, time, **kwargs):
        """
        Function takes in the voltage and time and then averages it to find the average field for the run
        Params:
            voltage: The voltage that the Bdot reads
            time: The time axis of the scope the Bdot is in
            a: area of calibrated Bdot
            g: gain on scope --> set to 1
            N: number of turns on the Bdot
            tau_s: attained from calibration

        Returns:
            field: The reconstructed B-field. Uses equation 10 from Eric Everson's Bdot paper.
        """
        defaults = {
            'a': -0.000447134918,
            'g': 1,
            'N': 1,
            'tau_s': -3.1174319180e-08,
        }
        params = {key:kwargs.get(key, default) for key, default in defaults.items()}
        
        a = params['a']
        g = params['g']
        N = params['N']
        tau_s = params['tau_s']

        voltage_average = np.average(voltage, axis = 0)
        time_average = np.average(time, axis = 0)

        noise = np.average(voltage_average[:20])
        voltage_average = voltage_average - noise

        fields = []
        A = a * N * g
        for trace in range(len(voltage)):
            noise = np.average(voltage[trace][:20])
            voltage_clean = voltage[trace] - noise

            initial_conditon = - tau_s * (1/A) * voltage_clean
            voltage_integrated = cumulative_trapezoid(voltage_clean, time[trace], initial = 0)

            field = 1/A * (voltage_integrated + tau_s * voltage_clean) + initial_conditon
            fields.append(field)
        field_average = np.average(fields, axis = 0)

        return field_average



        

        

class Plotting_Functions(Data_cleaner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)