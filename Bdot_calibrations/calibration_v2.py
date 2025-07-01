import numpy as np
import matplotlib.pyplot as plt
import h5py
from scipy.integrate import cumulative_trapezoid

def B_field_reconstruct(voltage, time, a, g, N, tau_s):
    '''
    Function integrates Erics everson equation 10 to get the reconstructed field. Averages the first 10-100 points
    and subtracts it from CH4 to rid of the noise before integrating. If average is false, it will calculate it for just one
    data trace.

    --Edit: Instead of averaging first, it will integrate first and then average.

    NOTE:TURNS OUT IT IS BETTER TO GET THE MAX FROM THE AVERAGE MAX FIELD.
    '''
    #Will first integrate over each data point and then average it out to get std and plot error bar
    fields = []
    max_field = []
    print(len(voltage), 'This is the shape of the original voltage')
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

    return fields, field_average, average_max, field_std
        
def plotting_func(voltage, time, fields_tuple, **kwargs):
    """
    This file will plot the data with the std and other information.
    """
    fields = fields_tuple[0]
    field_average = fields_tuple[1]
    average_max = fields_tuple[2]
    field_std = fields_tuple[3]

    arguments = kwargs.items()







if __name__ == "__main__":
    filename = 'magnetZscan-9cm-2025-06-16.h5'
    file_path = '/home/phoenix/Enrique-RPi/Bdot_calibrations/magnet_data'
    Data_file = h5py.File(filename, 'r')
    positions = np.arange(0,22, 1)

    MSO_voltage = np.array(Data_file['MSO24:Ch4:Trace'])
    MSO_time = np.array(Data_file['MSO24:Time'])

    field = B_field_reconstruct(np.array(Data_file["MSO24:Ch4:Trace"]), np.array(Data_file["MSO24:Time"]), -0.000447134918, 1, 1, -3.1174319180e-08)

    for i in range(len(field[0])):
        plt.plot(MSO_time[0], field[0][i], label = f'Trace {i}')
    plt.show()

    y_upper = field[1] + field[3]
    y_lower = field[1] - field[3]
    print(field[3], 'This is the standard deviation')
    plt.plot(MSO_time[0], field[1], label = 'Average field')
    plt.fill_between(MSO_time[0], y_lower, y_upper, color = 'red', alpha = 0.3, label = 'Standard Deviation')
    print(f'The max field strength is {field[2]}')
    plt.xlabel('Time (s)')
    plt.ylabel('B-field (T)')
    plt.title('B-field vs Time')
    plt.legend()
    plt.show()

  
