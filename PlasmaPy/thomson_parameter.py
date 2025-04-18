import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from math import sqrt
from plasmapy.diagnostics import thomson
from matplotlib import rcParams
from matplotlib.widgets import Slider, Button

rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial']

    








probe_wavelength = 532*u.nm
wavelengths = np.arange(probe_wavelength.value-0.5, probe_wavelength.value+0.5, 0.0001)*u.nm


ne = 2.e14
Te = 20
Ti = 1
scatter_angle = 90


def spectrum(ne, Te, Ti, scatter_angle_deg):
    probe_vec = np.array([1, 0, 0])
    scattering_angle = np.deg2rad(scatter_angle_deg)
    scatter_vec = np.array([np.cos(scattering_angle), np.sin(scattering_angle), 0])
    n_e = ne*u.cm**-3
    T_e = Te*u.eV
    T_i = Ti*u.eV

    alpha, Skw = thomson.spectral_density(wavelengths, probe_wavelength,
                                            n_e, T_e=T_e, T_i=T_i, probe_vec=probe_vec,
                                            scatter_vec=scatter_vec)
    #Skw[1000-20:1000+20]=0.
    Skw*=2.5e15   # calib factor to match our data
    return Skw

#Skw[2000-20:2000+20]=0


fig, ax = plt.subplots()
line, = ax.plot(wavelengths, spectrum(ne, Te, Ti, scatter_angle))

fig.subplots_adjust(left=0.5, bottom=0.25)

ax_n = fig.add_axes([0.1, 0.25, 0.0225, 0.63])
n_slider = Slider(
    ax=ax_n,
    label='ne (log, cm-3)',
    valmin=10,
    valmax=20,
    valinit=13,
    orientation='vertical'
)

ax_Te = fig.add_axes([0.2, 0.25, 0.0225, 0.63])
Te_slider = Slider(
    ax=ax_Te,
    label='Te (eV)',
    valmin=1,
    valmax=50,
    valinit=20,
    orientation='vertical'
)

ax_Ti = fig.add_axes([0.3, 0.25, 0.0225, 0.63])
Ti_slider = Slider(
    ax=ax_Ti,
    label='Ti (eV)',
    valmin=1,
    valmax=5,
    valinit=1,
    orientation='vertical'
)

ax_ang = fig.add_axes([0.25, 0.1, 0.65, 0.03])
ang_slider = Slider(
    ax=ax_ang,
    label='α',
    valmin=0,
    valmax=180,
    valinit=90,
)

def update(val):
    ydata = spectrum(10**n_slider.val, Te_slider.val, Ti_slider.val, ang_slider.val)
    max = np.max(ydata.value)
    min = np.min(ydata.value)
    line.set_ydata(ydata)
    ax.set_ybound(min-(max-min)*.1,max+(max-min)*.1)
    fig.canvas.draw_idle()

n_slider.on_changed(update)
Te_slider.on_changed(update)
Ti_slider.on_changed(update)
ang_slider.on_changed(update)

# plt.plot(wavelengths, Skw,color="red",linewidth=2,label='5 eV PlasmaPy')

ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Counts per shot per bin')


plt.show()