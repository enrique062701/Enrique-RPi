import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
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
    to calibrate the magnetic field. Will add more in the future. Must pass both together. Adding the follwing methods to allow the 
    class to be iterable and be used as a dictionary for better handling.
    """
    def __init__(self, calibration_data, HDF5_data_):
        self.calibration_data = calibration_data
        self.HDF5_data = h5py.File(HDF5_data_, 'r')

    def __getitem__(self, key):
        return self.HDF5_data[key]

    def __iter__(self):
        return iter(self.HDF5_data)

    def __contains__(self, key):
        return key in self.HDF5_data

    def keys(self):
        return self.HDF5_data.keys()

    def items(self):
        self.HDF5_data.items()

    def values(self):
        return self.HDF5_data.values()        

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
        for key, array in self.HDF5_data.items():
            attr_name = key.replace(':', '_')
            setattr(self, attr_name, np.array(array))


class Bdot_actions(Data_cleaner):
    def __init__(self, calibration_data, HDF5_data_, **kwargs):
        """
        The 'super()' is a built-in class in python that returns a proxy objext that delegates method calls
        to a parent method. This allows you to call 'Data_cleaner' without having to call Data_cleaner itself.
        This makes it cleaner and easier than making them completely independent.
        """
        super().__init__(calibration_data, HDF5_data_, **kwargs)
    
    # The following two functions: re_curve and im_curve are from Nathans code which are part of his professors paper. Could not find the original citation to cite.
    def re_curve(self, w, a, tau, tau_s):
        return self.factor * (a * (w**2) * (tau_s - tau)) / (1 + (tau_s * w) ** 2)

    def im_curve(self, w, a, tau, tau_s):
        return self.factor * (a * tau * tau_s * (w**3) + a * w) / (1 + (tau_s * w) ** 2)

    def combined_curve(self, w_all, a, tau, tau_s):
        n = len(w_all) // 2
        w_re, w_im = w_all[:n], w_all[n:]
        re_model = self.re_curve(w_re, a, tau, tau_s)
        im_model = self.im_curve(w_im, a, tau, tau_s)
        return np.concatenate([re_model, im_model])



    def B_dot_calibration(self, imaginary = False, **kwargs):
        """
        This function will take in the .TXT file attain from the waveform analyser and return the surface area of the bdot.
        This surface area will be used for the reconstruction of the bdot. If imaginary is equal to false, it will first convert the
        data to real and imaginary parts.

        Must first get the clean data by running the clean_data_cal function. Data should have been passed initially so one can just
        run the function without having to pass the data.
        
        N_turns --> The number of turns in the Bdot 
        gain --> Amp gain if using a diff amp
        R_p --> resistor measured across, kg * m^2 * s^-3 * A^-2
        r_helm --> The helmholts coil radius that is used to drive the field
        """
        
        clean_data = self.clean_data_cal() # Run the function by itself to set the clean data equal to a variable to index later
        angular_frequency = clean_data["Frequency"] * 2 * np.pi 
        mag_for_calc = clean_data["Gain"] / 1000

        if imaginary == False:
            phase_for_calc = -clean_data["Phase"] * np.pi / 180

            v_real = mag_for_calc * np.cos(phase_for_calc) # Real part
            v_imaginary = mag_for_calc * np.sin(phase_for_calc) # Imaginary part
        elif imaginary == True:
            phase_for_calc = cleand_data["Phase"]

            v_real = mag_for_calc * np.cos(phase_for_calc)
            v_imaginary = mag_for_calc * np.sin(phase_for_calc)
            
        self.v_real = v_real
        self.v_imaginary = v_imaginary
        # Now that the real and imaginary parts have been set, the next step is to calculate the surface area of the probe
        defaults = { #Set as defaults as they usually do not change, in case they do can be initialized.
            'mu_0': 4 * np.pi * 10e-7, # Vacuum permeability, kg * m * s^-2 * A^-2
            'g': 10, #amp gain, unitless
            'N': 1, # number of turns in probe, unitless
            'R_p': 51, # Resistor measured across, kg * m^2 * s^-3 * A^-2
            'r': 0.048 # helmholtz coil radius, m
        }
        params = {key:kwargs.get(key, default) for key, default in defaults.items()}

        mu_0 = params['mu_0']
        g = params['g']
        N = params['N']
        R_p = params['R_p']
        r = params['r']

        self.factor = (g * N * mu_0 * 16) / (R_p * r * (5 ** 1.5))

        #The next step is to do a best fit along the imaginary part of the data
        
        xdata = np.concatenate([angular_frequency, angular_frequency])
        ydata = np.concatenate([v_real, v_imaginary])

        # Initial guesses
        p0 = [3e-4, 6e-8, -1e-8]
        sigma = np.ones_like(ydata)

        popt, pcov = curve_fit(
            lambda w_all, a, tau, tau_s: self.combined_curve(w_all, a, tau, tau_s), 
            xdata, ydata, p0=p0, sigma = sigma, absolute_sigma = True
        )


        a_fit, tau_fit, tau_s_fit = popt
        effective_area = a_fit

        self.effective_area = effective_area
        self.tau_fit = tau_fit
        self.tau_s_fit = tau_s_fit
        
        return effective_area, 
        

    def B_field_reconstruct(self, voltage, time, **kwargs):
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
            'a': self.effective_area, # -0.000447134918, #This is the value for 1in in Jennas experiment
            'g': 1,
            'N': 1,
            'tau_s': self.tau_s_fit, # -3.1174319180e-08, This is the value for 1in in Jennas experiment
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


    def max_b_field(self, **kwargs):
        """
        Function is called on itself. This function gives out the max B-field of the run. Must specify which channel the B-dot was connected too.
        Params:
            **kwargs: This helps specify which channel Bdot is in. If not specified, used MSO:Ch4:Trace as default.
            Calls on the B_field_reconstruct function to 

        Returns:
            returns the max b-field of the field calibrated using the Bdot. 
        """
        channels = kwargs.get('Channels') #Can set it equal to a value to attain the values in the list
        if channels:
            if len(channels) != 2:
                raise ValueError("You must pass only voltage and time values")
            voltage_key, time_key = channels
            if voltage_key not in self.data or time_key not in self.data:
                raise KeyError(f"Channel not found in data: {channels}")

            voltage = self.data[voltage_key]
            time = self.data[time_key]
            field_average = Bdot_actions.B_field_reconstruct(voltage, time)
        else:
            voltage = self.data.MSO24_Ch4_Trace
            time = self.data.MSO24_Time
            field_average = Bdot_actions.B_field_reconstruct(voltage, time)

        max_field = np.max(field_average)
        return max_field


class Plotting_Functions(Data_cleaner):
    def __init__(self, calibration_data, HDF5_data_, **kwargs):
        super().__init__(calibration_data, HDF5_data_, **kwargs)


    def plot_all_runs(self, **kwargs):
        """
            This function will plot all the runs in one file and show the standard deviation and other paramaters of the data
        """
        fig, ax = plt.subplots(2,1)

        time = self.HDF5_data['MSO24:Time'][0]
        field = Bdot_actions.B_field_reconstruct(self.HDF5_data['MSO24:Ch4:Trace'], self.HDF5_data['MSO24:Time'])

        for trace in range(len(field[0])):
            ax[0].plot(time, field[0][i])
        ax[0].set_title('B-Field vs Time: All runs')
        ax[0].set_xlabel('Time')
        ax[0].set_ylabel('Field Data')






