import numpy as np
import matplotlib.pyplot as plt
import h5py
from scipy.integrate import cumulative_trapezoid


def B_field_reconstruct(voltage, time, a, g, N, tau_s):
    '''
    Function integrates Erics everson equation 10 to get the reconstructed field. Averages the first 10-100 points
    and subtracts it from CH4 to rid of the noise before integrating. If average is false, it will calculate it for just one
    data trace.
    Use Bdot calibration attained from Nathan from Gettysburg.
    --Edit: Instead of averaging first, it will integrate first and then average.
    '''
    #Will first integrate over each data point and then average it out to get std and plot error bar
    fields = []
    max_field = []
    A = a * N * g 
    for trace in range(len(voltage)):
        noise = np.average(voltage[trace][:20])
        voltage_clean = voltage[trace] - noise #Subtract the noise

        initial_conditon = -tau_s * (1/A) * voltage_clean[0] #This will get the first value of each trace
        voltage_integrated = cumulative_trapezoid(voltage_clean, time[trace], initial = 0)

        field = 1/A * (voltage_integrated + tau_s * voltage_clean) + initial_conditon
        max_ = np.max(field)
        max_field.append(max_)
        fields.append(field)

    field_average = np.average(fields, axis = 0)
    average_max = np.average(max_field)
    field_std = np.std(fields, axis = 0)


    return field_average, average_max
#-------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    file_path = "/home/phoenix/Enrique-RPi/Bdot_calibrations/magnet_data"
    positions = np.arange(0,22, 1)

    magnet_current = []
    voltage_list = []
    time_list = []
    field_list = []
    field_max = []
    max_test = []
    for i in range(22):
        filename = f'{file_path}/magnetZscan-1coil-100V-{i}cm-2025-06-16.h5'
        Data_file = h5py.File(filename, 'r')
        voltage = np.array(Data_file['MSO24:Ch4:Trace'])
        time = np.array(Data_file['MSO24:Time'])
        current = np.array(Data_file['MSO24:Ch1:Trace'])

        if filename == f'{file_path}/magnetZscan-1coil-100V-0cm-2025-06-16.h5':
            voltage_clean = voltage[:10]
            time_clean = time[:10]
            current_clean = current[:10]
            ave_current = np.average(current_clean, axis = 0)
            current_max = np.max(ave_current)
            magnet_current.append(current_max) #This is to attain the average max current at each position

            field = B_field_reconstruct(voltage_clean, time_clean, -0.000447134918, 1, 1, -3.1174319180e-08)
            max_ = np.max(field[0])
            field_max.append(max_)
            max_test.append(field[1])
            field_list.append(field[0])
            
            voltage_list.append(voltage_clean)
            time_list.append(time_clean)
        else:
            ave_current = np.average(current, axis = 0)
            current_max = np.max(ave_current)
            magnet_current.append(current_max)
            
            field_test = B_field_reconstruct(voltage, time, -0.000447134918, 1, 1, -3.1174319180e-08)
            max_ = np.max(field_test[0])
            field_max.append(max_)
            max_test.append(field_test[1])
            field_list.append(field_test[0])
            voltage_list.append(voltage)
            time_list.append(time)

    plt.plot(positions, field_max, label = 'Max Field Curve', color = 'blue')
    plt.scatter(positions, field_max, label = 'Max Field Points', color = 'Red')
    plt.legend()
    plt.title('Position vs Field - 1 coil, 100V')
    plt.xlabel('Positions (cm)') 
    plt.ylabel('Field (T)')
    plt.show()
#-------------------------------------------------------------------------------------------------------------------------------
    #Now to plot the current at each point 
    plt.plot(positions, magnet_current, label = 'Max current curve', color = 'blue')
    plt.scatter(positions, magnet_current, label = 'Max current at each position', color = 'red')
    print(np.average(magnet_current[:10]), ':Is the max current for 1 coil')
    print(f'If current is Ch1 * 1000, then average current is {np.average(magnet_current[:10]) * 1000} A')

    plt.legend()
    plt.title('Position vs Magnet Current')
    plt.xlabel('Position (cm)')
    plt.ylabel('Current (A)')
    plt.show()





