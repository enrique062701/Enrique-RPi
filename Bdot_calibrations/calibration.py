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
def B_field_reconstruct(voltage, time, a, g, N, tau_s, average):
    '''
    Function integrates Erics everson equation 10 to get the reconstructed field. Averages the first 10-100 points
    and subtracts it from CH4 to rid of the noise before integrating. If average is false, it will calculate it for just one
    data trace.
    '''
    #Will implement the average here so that it spits out the average field for the entire run.
    if average == True:

        voltage_average = np.average(voltage, axis = 0)
        time_average = np.average(time, axis = 0)
        print(voltage_average.shape)
        #Finding the initial condition
        noise = np.average(voltage_average[:20])
        voltage_average = voltage_average - noise

        A = a * N * g 
        initial_conditon = 0 - tau_s * (1/A) * voltage_average[0] #0 is equal to 0 because initial field is 0
        fields = []
        voltage_integrated = cumulative_trapezoid(voltage_average, x = time_average, initial = 0)

        for i in range(len(voltage_average)):
            field = 1/A * (voltage_integrated[i] + tau_s * voltage_average[i]) + initial_conditon
            fields.append(field)

        return fields
    else:
        A2 = a * N * g 
        initial_conditon2 = 0 - tau_s * (1/A2) * voltage[0] #0 is equal to 0 because initial field is 0
        fields2 = []
        voltage_integrated2 = cumulative_trapezoid(voltage, x = time, initial = 0)

        for i in range(len(voltage)):
            field2 = 1/A2 * (voltage_integrated2[i] + tau_s * voltage[i]) + initial_conditon2
            fields2.append(field2)
        return fields2

if __name__ == "__main__":

    OneInchCalibration = '1INCAP_2.TXT'

    #filename = 'magnet-calibration-pat-ground-2025-05-27.h5'
    filename = 'magnetZscan-9cm-2025-06-16.h5'
    Data_file = h5py.File(filename, 'r')

    MSO_voltage = np.array(Data_file['MSO24:Ch4:Trace'][2])
    MSO_time = np.array(Data_file['MSO24:Time'][2])

    print(MSO_voltage.shape, 'Voltage')
    print(MSO_time.shape, 'Time')
    #For this one, use the parameters in the prob_0.json file
    field = B_field_reconstruct(np.array(Data_file["MSO24:Ch4:Trace"]), np.array(Data_file["MSO24:Time"]), -0.000447134918, 1, 1, -3.1174319180e-08, average = True)
    plt.plot(np.array(Data_file["MSO24:Time"][2]), field, label = 'Field vs time')
    plt.title('Time vs Field')
    plt.xlabel('Time (s)')
    plt.ylabel('Field (T)')
    plt.legend()
    plt.show()

    #This uses the calibration parameters using my own calibration method
    field2 = B_field_reconstruct(np.array(Data_file["MSO24:Ch4:Trace"]), np.array(Data_file["MSO24:Time"]), -7.919e-05, 1, 1, -1.9618e-08, average = True)
    #print(field2.shape, 'Field 2')
    plt.plot(MSO_time, field2, label = "Field vs time 2")
    plt.legend()
    plt.show()
    print('Test 3')


    #Will now plot the position vs voltage plot for 100V
    file_path = '/mnt/shared/'
    positions = np.arange(0,22, 1)
    voltage_list = []
    time_list = []
    field_list = []
    field_max = []
    for i in range(22):
        filename = f'{file_path}/magnetZscan-{i}cm-2025-06-16.h5'
        Data_file = h5py.File(filename, 'r')
        voltage = np.array(Data_file['MSO24:Ch4:Trace'])
        time = np.array(Data_file['MSO24:Time'])
        field = B_field_reconstruct(voltage, time, -0.000447134918, 1, 1, -3.1174319180e-08, average = True)
        max_ = np.max(field)
        field_max.append(max_)
        field_list.append(field)
        voltage_list.append(voltage)
        time_list.append(time)

    plt.plot(positions, field_max, label = 'field strength')
    plt.legend()
    plt.title('Position vs Field - 100V')
    plt.xlabel('Positions (cm)')
    plt.ylabel('Field (T)')
    plt.show()


    voltage_list2 = []
    time_list2 = []
    field_list2 = []
    field_max2 = []
    for i in range(22):
        filename = f'{file_path}/magnetZscan-1coil-100V-{i}cm-2025-06-16.h5'
        Data_file = h5py.File(filename, 'r')
        voltage = np.array(Data_file['MSO24:Ch4:Trace'])
        time = np.array(Data_file['MSO24:Time'])
        field = B_field_reconstruct(voltage, time, -0.000447134918, 1, 1, -3.1174319180e-08, average = True)
        max_ = np.max(field)
        field_max2.append(max_)
        field_list2.append(field)
        voltage_list2.append(voltage)
        time_list2.append(time)
    plt.plot(positions, field_max2, label = 'field strength')
    plt.legend()
    plt.title('Position vs Field - 1 coil: 100V')
    plt.xlabel('Positions (cm)')
    plt.ylabel('Field (T)')
    plt.show()



    ##Doing the 600V
    filename = f'{file_path}/magnetZscan-10cm_Vscan-2025-06-16.h5'
    Data_file = h5py.File(filename, 'r')

    MSO_voltage = np.array(Data_file['MSO24:Ch4:Trace'])
    MSO_time = np.array(Data_file['MSO24:Time'])
    print(MSO_voltage[50:60])
    print(MSO_time.shape)
    voltage_600V = MSO_voltage[50:60]
    time_600V = MSO_time[50:60]
    

    field_600 = B_field_reconstruct(voltage_600V, time_600V, -0.000447134918, 1, 1, -3.1174319180e-08, average = True)
    print(voltage_600V.shape)
    print(time_600V.shape)
    plt.plot(time_600V[0], field_600, label = 'Magnetic field')
    plt.legend()
    plt.title('Magnetic field - 600V')
    plt.xlabel('Time (s)')
    plt.ylabel('Field (T)')
    plt.show()
    print(np.max(field_600))