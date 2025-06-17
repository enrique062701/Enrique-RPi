#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 13 14:08:22 2025
This file is to try and reconstruct the field strenght from scratch without using Gettysburg code (Nate)
@author: Enrique
"""
import numpy as np
import h5py
import os
import matplotlib.pyplot as plt
import lmfit
import pandas as pd
from io import StringIO
from scipy.integrate import cumulative_trapezoid

calibration_data = '1INCAP_2.TXT'
#Now importing the HDF5 data
filename = 'magnet-calibration-pat-ground-2025-05-27.h5'
data = h5py.File(filename, 'r')

IN_voltage = np.array(data['MSO24:Ch4:Trace'])#Bdot Voltage
MSO_time = np.array(data['MSO24:Time']) #Time for the MSO
#---------------------------------------------------------------------------------------------------------------------------------------

def data_clean(data_path):
    '''
    Parameters
    ----------
    Input TXT file recieved from network analyzer from calibrating Bdot.

    Returns
    -------
    BP_ : Pandas Data Type
    Returns a clean pandas dataframe by removing all the junk in the header.
    '''
    with open(data_path, 'r') as f:
        lines = f.readlines()

    data_start = next(i for i, line in enumerate(lines) if line.strip().startswith('1.'))
    data_lines = lines[data_start:]
    data_str = "".join(data_lines)
    BP_ = pd.read_csv(StringIO(data_str), sep='\t', header = None, names=["Frequency", "Gain", "Phase"])
    BP_.head(15)
    return BP_

#Now inputting the Calibration parameters
def predict_re_im(data, a, tau, tau_s):
    '''
    Input the TXT calibration file to convert to real and imaginary parts
    '''
    clean = data_clean(data)
    w = 2 * np.pi * clean["Frequency"]
    gain = clean["Gain"]

    real = clean['Gain'] * ((a * (w ** 2) * (tau_s - tau)) / (1 + (tau_s * w) ** 2))
    imaginary = clean['Gain'] * ((a * tau * tau_s * (w**3) + a * w) / (1 + (tau_s * w) ** 2))
    
    return real, imaginary, clean
#------------------------------------------------------------------------------------------------------------------------------------------------------------------    

def objective_function(params, data):
    a = params['a']
    tau = params['tau']
    tau_s = params['tau_s']

    clean = data_clean(data)
    w = 2 *np.pi * clean['Frequency']
    gain = clean['Gain']
    phase_deg = clean["Phase"]
    phase_rad = np.radians(phase_deg)

    real_measured = gain * np.cos(phase_rad)
    imaginary_measured = gain * np.sin(phase_rad)

    real_pred, im_pred = predict_re_im(data, a, tau, tau_s)

    resid_re = real_pred - real_measured
    resid_imag = im_pred - imaginary_measured

    return np.concatenate((resid_re, resid_imag))

#------------------------------------------------------------------------------------------------------------------------------------------------------------------    

def calibrate(data):
    params = lmfit.Parameters()
    params.add_many(
        ('a', 0.00064516, True, 1e-6, 1e-1),
        ('tau', 3e-8, True, 1e-9, 1e-6),
        ('tau_s', 3e-8, True, 1e-9, 1e-6)
    )
    result = lmfit.minimize(objective_function, params, args = (data,))
    a, tau, tau_s = result.params.valuesdict().values()
    
    return a, tau, tau_s

#------------------------------------------------------------------------------------------------------------------------------------------------------------------    

def reconstruct(voltages, times, gain, b_0, correct_drift: bool = False):
    '''
    a: It is the area of the probe. It is attained from the calibration function
    N is the number of turns in the probe
    '''
    #a, tau, tau_s = calibrate(data)
    a = 4.9199e-05
    tau = -1.999e-08
    tau_s = -1.9618e-08
    N = 1

    if correct_drift:
        num_timestamps = times.shape[0]
        voltages -= np.average(voltages[:int(num_timestamps * 0.04)])

    field = np.zeros_like(voltages)
    field[0] = b_0

    const1 = 1 / (a * N * gain)
    const2 = field[0] - tau

    voltages_integrated = cumulative_trapezoid(voltages, x=times, initial=0)
    print(len(voltages_integrated), 'Voltages integrated')
    print(len(voltages), 'Voltage')
    print(voltages[0].size)
    for i in range(len(voltages_integrated)):
        field[i+1] = const1 * (voltages_integrated[i] + (tau_s * voltages[i])) + const2

    return field
#------------------------------------------------------------------------------------------------------------------------------------------------------------------

def reconstruc2(voltages, times, gain, b_0):
    a = 4.9199e-05
    tau = -1.999e-08
    tau_s = -1.9618e-08
    N = 1

    const1 = 1 / (a * N * gain)
    const2 = b_0 - tau
    #field = np.zeros_like(voltages)
    average_volts = np.average(voltages, axis = 0)
    time_average = np.average(times, axis = 0)

    voltages_integrated = cumulative_trapezoid(average_volts, x = time_average, initial=0)

    field = const1 * (voltages_integrated + (tau_s * average_volts)) + const2
    return field
#------------------------------------------------------------------------------------------------------------------------------------------------------------------

def reconstruct_array(data, volts_arr, times_arr, gain, b_0: float =0, **kwargs):
    num_rows = volts_arr.shape[0]
    if type(b_0) is int:
        b_0 = np.full(num_rows, b_0)

    field_arr = []
    for i, row in enumerate(volts_arr):
        field_row = reconstruct(data, row, times_arr[i], gain, b_0[i], kwargs)
        field_arr.append(field_row)
    return np.array(field_arr)
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
def magnetic_field(volts_arr, times_arr, gain, b_0):
    pass
#------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    calibration_data = '1INCAP_2.TXT'
    filename = 'magnet-calibration-pat-ground-2025-05-27.h5'
    data = h5py.File(filename, 'r')

    voltages = data['MSO24:Ch4:Trace']
    times = data['MSO24:Time']
    gain = 10
    b_0 = 0
    real, imaginary, clean_data = predict_re_im(calibration_data, 4.9199e-05, -1.99e-08, -1.9618e-08)


    a, tau, tau_s = calibrate(calibration_data)
    print(a,tau,tau_s)







    #The first step is to find the calibration parameters of the file.
    #clean = data_clean(calibration_data)
    
    #real, imaginary, clean = predict_re_im(calibration_data, 4.9199e-05, -1.99e-08, -1.9618e-08)
    #w = 2 *np.pi * clean['Frequency']
    #a_, tau, tau_s = calibrate(calibration_data)
    #print(a_)


    field = reconstruc2(voltages, times, gain, b_0)
    #re_array = reconstruct_array()
    print(field)
    plt.plot(field)
    plt.title('Reconstructed array averaged - Enrique')
    plt.show()