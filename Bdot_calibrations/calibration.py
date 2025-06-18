'''
This python file will calibrate the bdot data and will also reconstruct the B-field. It will manually
integrate the B-field to rebuild the magnetic field using Eric's paper.
'''
import numpy as np
import matplotlib.pyplot as plt
import os
import h5py
from scipy.integrate import cumulative_trapezoid

#Implementing the data clean function to clean the calibration data
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

#Next is to code the equation that integrates the signal to get the field
def B_field_reconstruct(voltage, time, a, g, N, tau_s):
    '''
    Function integrates Erics everson equation 10 to get the reconstructed field.
    '''
    A = a * N * g 
    initial_conditon = 0 - tau_s * (1/A) * voltage[0]
    fields = []
    voltage_integrated = cumulative_trapezoid(voltage, x = time, initial = 0)
    for i in range(len(voltage)):
        
        field = 1/A * (voltage_integrated[i] + tau_s * voltage[i]) + initial_conditon
        fields.append(field)

    return fields

if __name__ == "__main__":

    OneInchCalibration = '1INCAP_2.TXT'

    filename = 'magnet-calibration-pat-ground-2025-05-27.h5'
    Data_file = h5py.File(filename, 'r')

    MSO_voltage = Data_file['MSO24:Ch4:Trace'][2]
    MSO_time = Data_file['MSO24:Time'][2]

    field = B_field_reconstruct(np.array(Data_file["MSO24:Ch4:Trace"][20]), np.array(Data_file["MSO24:Time"][20]), -0.000447134918, 1, 1, -3.1174319180e-08)
    print(len(field))
    plt.plot(np.array(Data_file["MSO24:Time"][20]), field, label = 'Field vs time')
    plt.title('Time vs Field')
    plt.xlabel('Time (s)')
    plt.ylabel('Field (T)')
    plt.legend()
    plt.show()

    field2 = B_field_reconstruct(MSO_voltage, MSO_time, -0.063062, 1, 1, -5.952166e-06)
    plt.plot(field2)
    plt.show()

