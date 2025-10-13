#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 11:14:44 2025

@author: enrique
This is a PID controller that will regulate the desired pressure and maintain it.


"""
from epics import caput,caget,PV
import time
import os
import numpy as np

def onChanges(pvname=None, value=None, char_value=None, **kws):
    print(value)
    return value
    
   
mypv = PV('Vacuum:DS:PressurePirani')
mypv.get_ctrlvars()
mypv.add_callback(onChanges)	# add a callback
pstart = caget("Vacuum:DS:PressurePirani") #Starting pressure has to be read outside the loop

caput('Vacuum:Gas:SetFlowRate', 0)

#Initial values for interpolation
SLPM_turbo_off = np.array([0,0.08, 0.1, 1, 2.5,5,10, 15, 20])
Pressure_turbo_off = np.array([0, 0.55, 0.59, 2.74, 5.29, 9.40, 18.03, 25.73, 33.5])

SLPM_turbo_on = np.array([0, 0.10, 0.14, 0.18, 0.22, 0.28, 0.32, 0.34, 0.38, 0.48, 0.54, 0.58, 0.62])
Pressure_turbo_on = np.array([0, 0.0091, 0.0137, 0.0218, 0.0382, 0.0830, 0.100, 0.1431, 0.1912, 0.3228, 0.3988, 0.4624, 0.5253])

try:
    # Keep the program running
    while True:
        DS_Pirani = caget('Vacuum:DS:PressurePirani')
        DS_CC = caget('Vacuum:DS:PressureCC')
        Pi_Pirani = caget('Vacuum:Pi:PressurePirani')
        Pi_MM = caget('Vacuum:Pi:PressureMM')
        
        DS_sensors = [DS_Pirani, DS_CC]
        Pi_sensors = [Pi_Pirani, Pi_MM]

        #Getting the flowrate
        current_flow = caget('Vacuum:Gas:FlowRate')
        current_chamber = caget('Vacuum:Gas:CurrentChamber') #This can be a new PV that states which chamber is use: 0 == DS and 1 == Pi
        turbo_status = caget('Vacuum:Gas:TurboStatus') #This is a switch that states whether turbo is on or off: 0 == Off and 1 == On
        user_interference = caget("Vacuum:UserInterference")
        
        target_pressure = caget('Vacuum:TargetPressure')
        if user_interference == 0: #DS Chamber is 1 and Pi chamber is 0
            if turbo_status == 1:
                SLPM_target_on = np.interp(target_pressure, Pressure_turbo_on, SLPM_turbo_on)
                SLPM_target_on_percent = (SLPM_target_on * 100) / 20 # Converts SLPM to percent
                max_turbo_ds = (np.max(SLPM_target_on) * 100) / 20
                turbo_moderated = max(0, min(SLPM_target_on_percent, max_turbo_ds ))
                caput('Vacuum:Gas:SetFlowRate', turbo_moderated)
            elif turbo_status == 0:
                SLPM_target_off = np.interp(target_pressure, Pressure_turbo_off, SLPM_turbo_off)
                turbo_off_percent = (SLPM_target_off * 100) / 20 
                caput('Vacuum:Gas:SetFlowRate', turbo_off_percent)
        else:
            caput('Vacuum:TargetPressure', 0)

        
        
except KeyboardInterrupt:
    print("Program terminated")
