#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file is to automatically get and plot all the timestamps for any given actionlist run
"""
import numpy as np
import matplotlib.pyplot as plt
import h5py


def all_timestamps(data):
    '''
    Function creates a dictionary where you can index it based on the PV. Returns a numpy array for the data. 
    First section acquires all the timestamps in the timestamps folder. The second will acquire the timestamps from the 
    Pi-Max Imagae folder into a new list.
    '''
    file = h5py.File(data, 'r')
    length = np.array(file.get('timestamps'))
    time_dict = {}

    for pv in length:
        time_dict[pv] = np.array(file.get(f'timestamps/{pv}'))

    Image_timestamps = []
    PI_cam = np.array(file.get("13PICAM2:Pva1:Image"))
    for i in range(len(PI_cam)):
        loop = file.get(f'13PICAM2:Pva1:Image/image {i}')
        image_time= loop.attrs["timestamp"]
        Image_timestamps.append(image_time)

    #Now to add the image timestamps at the very end
    time_dict['13PICAM2:Pva1:Image'] = np.array(Image_timestamps)
    return time_dict

def difference(timestamps):
    '''
    Function returns the difference between each timestamp value. Example on how it can be indexed:
    Vacuum:Gas:SetFlowRateSLPM.timestamp - Vacuum:Gas:Pressure.timestamps = (....) The difference between the arrays
    '''
    #Will only compare the timestamps for the most important values. Comparing each one to each other will give 
    #500+ arrays. 
    difference = {}
    #plt.figure(figsize = (15,7))
    for base_key, base_array in timestamps.items():
        print(f'\n All PVs in the file "{base_key}"')
        for compare_key, compare_array in timestamps.items():
            if base_key != compare_key:
                key_name = f"{base_key} - {compare_key}"
                difference[key_name] = base_array - compare_array
    return difference

def plot_function(data, **kwargs):
    '''
    Function will plot all the difference unless stated. Can enter: plot = [...], which will only plot the PV that are listed.
    Only need to mention the suffix as the prefix is the same as all.
    '''
    plt.figure(figsize = (19,10))
    prefix = "13PICAM2:Pva1:Image"
    suffix = kwargs.get('plot')
    if kwargs.get('plot'):
        plotting_data = {key:value for key, value in data.items() if key.startswith(prefix) and key.endswith(suffix)}
        for key, array in plotting_data.items():
            size = len(array)
            plt.plot(np.array(array), label = key)
        
    else:
        plotting_data ={key: value for key, value in data.items() if key.startswith(prefix)}   
        for key, array in plotting_data.items():
            size = len(array)
            plt.plot(np.array(array), label = key)
    
    #size = len(plotting_data['13PICAM2:Pva1:Image - Motor10:PositionRead.timestamp'])
    print(size)
    plt.legend()
    plt.xlabel('Shot #')
    plt.ylabel('Time difference')
    plt.title(f'{prefix} - devices; gain{size}')
    plt.show()                
    return plotting_data
            

#---------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    gain10 = "Enrique_gain1_10-2025-03-19.h5"
    gain15 = "Enrique_gain1_15-2025-03-19.h5"
    gain20 = "Enrique_gain1_20-2025-03-19.h5"
    gain25 = "Enrique_gain1_25-2025-03-19.h5"
    gain30 = "Enrique_gain1_30-2025-03-19.h5"
    gain35 = "Enrique_gain1_35-2025-03-19.h5"
    gain40 = "Enrique_gain1_40-2025-03-19.h5"
    gain45 = "Enrique_gain1_45-2025-03-19.h5"
    gain50 = "Enrique_gain1_50-2025-03-19.h5"
    
    gain10_timestamps = all_timestamps(gain10)
    gain15_timestamps = all_timestamps(gain15)
    gain20_timestamps = all_timestamps(gain20)
    gain25_timestamps = all_timestamps(gain25)
    gain30_timestamps = all_timestamps(gain30)
    gain35_timestamps = all_timestamps(gain35)
    gain40_timestamps = all_timestamps(gain40)
    gain45_timestamps = all_timestamps(gain45)
    gain50_timestamps = all_timestamps(gain50)
    
    gain10_difference = difference(gain10_timestamps)
    gain15_difference = difference(gain15_timestamps)
    gain20_difference = difference(gain20_timestamps)
    gain25_difference = difference(gain25_timestamps)
    gain30_difference = difference(gain30_timestamps)
    gain35_difference = difference(gain35_timestamps)
    gain40_difference = difference(gain40_timestamps)
    gain45_difference = difference(gain45_timestamps)
    gain50_difference = difference(gain50_timestamps)


    plot_test = plot_function(gain10_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp', 
                                                         'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain15_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp',
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain20_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp', 
                                                        'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain25_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp',
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain30_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp',
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain35_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp', 
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain40_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp',
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain45_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp',
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))
    plot_test = plot_function(gain50_difference, plot = ('13PICAM2:cam1:IntensifierGain_RBV.timestamp',
                                                     'LeCroy:Ch1:Trace.timestamp', 'LeCroy:Ch3:Trace.timestamp','LeCroy:Time.timestamp', 'MSO24:Ch1:Trace.timestamp'))










