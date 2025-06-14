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
def convert_to_real_im(data):
    '''
    Input the TXT calibration file to convert to real and imaginary parts
    '''
    w = float
    a = float
    tau = float
    tau_s = float
    clean = data_clean(data)
    
    real = clean['Gain'] * ((a * (w ** 2) * (tau_s - tau)) / (1 + (tau_s * w) ** 2))
    imaginary = clean['Gain'] * ((a * tau * tau_s * (w**3) + a * w) / (1 + (tau_s * w) ** 2))
    
    return real, imaginary
#------------------------------------------------------------------------------------------------------------------------------------------------------------------    

def calibrate(data):
    params = lmfit.Parameters()
    
    a = params['a']
    tau = params['tau']
    tau_s = params['tau_s']
    
    real, imaginary = np.array(convert_to_real_im(data))
    
    re_pred = 
    im_pred = 
    
    params.add_many(('a',  0.00064516), ('tau', 3e-8), ('tau_s', 3e-8))
    








