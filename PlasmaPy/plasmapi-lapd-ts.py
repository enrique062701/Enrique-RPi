import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
import warnings
from math import sqrt

def gaussian(x, amplitude, mean, stddev):
    return amplitude*np.exp(-(x - mean)**2 / (2*stddev**2))


from plasmapy.diagnostics import thomson
from plasmapy.utils.exceptions import ImplicitUnitConversionWarning

from matplotlib import rcParams
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']

    


plt.rcParams.update({'font.size':14}) 

plt.figure(figsize=(6,5),dpi=300)

#plt.plot(wavelength, profile,color="black")


plt.xlabel('Wavelength (nm)')
plt.ylabel('Counts per shot per bin')



import astropy.units as u
import warnings

from plasmapy.diagnostics import thomson
from plasmapy.utils.exceptions import ImplicitUnitConversionWarning

probe_wavelength = 532*u.nm
wavelengths = np.arange(probe_wavelength.value-0.5, probe_wavelength.value+0.5, 0.0001)*u.nm
probe_vec = np.array([1, 0, 0])
scattering_angle = np.deg2rad(2)
scatter_vec = np.array([np.cos(scattering_angle), np.sin(scattering_angle), 0])

ne = 2.e12*u.cm**-3
Te = 20*u.eV
Ti = 1*u.eV

with warnings.catch_warnings():
    warnings.simplefilter("ignore", ImplicitUnitConversionWarning)

    # This line actually runs the program - note that there is other functionality
    # that is not highlighted here, see the documentation for more details
    alpha, Skw = thomson.spectral_density(wavelengths, probe_wavelength,
                                          ne, Te, Ti, probe_vec=probe_vec,
                                          scatter_vec=scatter_vec)
#Skw[1000-20:1000+20]=0.
Skw*=2.5e15   # calib factor to match our data

#Skw[2000-20:2000+20]=0

plt.plot(wavelengths, Skw,color="red",linewidth=3,label='5 eV PlasmaPy')





plt.legend()


plt.show()
