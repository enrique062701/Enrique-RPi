#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 20 09:50:24 2025

File that makes bdot actionlist
Will do the top half of the square first and then will do the bottom half
"""
import numpy as np
import epics
from epics import caget, caput

file = open('Bdot_actionlist.txt', "w")


def square_sweep_shape(x_max, x_min,step_size):
    '''Parameters:
        x_min, x_max = will determine the volume of the cube. The smaller the shorter the run.
        x_offset
        y_offset
        z_offset
        The offsets are the positions of the motor where it will correspond to zero in the motor space. For example:
            x = 3.4 cm will be the 0 position of the motor., etc...
        step_size: the step size of the probe which was set too 2cm


    Returns:
        x_motor, y_motor, z_motor: These values correspond to the motor space coordinates. So for coordinate 0 it
        will be 3.4cm from the base of the motor.
        '''
    #step_size = 0.2 # 2 milimiter steps

    x_max = x_max #4.5#5.5
    x_min = x_min #2.4# 1.4

    y_max = 2.8 #Furthest from the target
    y_min = 0 #This being the closest to the targtet

    z_min = 0.55 # Closest to the beam path
    z_max = 0 #Furtherst away from beam/ very top

    x_axis_points = np.arange(x_min, x_max, step_size) #Distance is in cm
    y_axis_points = np.arange(y_min, y_max, step_size)
    z_axis_points = np.arange(z_max , z_min , step_size)

    return  x_axis_points, y_axis_points, z_axis_points



#The logic is that it starts at the first x-positions, then does the full yz plane scan, then moves back a step and then
#does the same yz scan again

file.write('Motor4:PositionInput\tMotor5:PositionInput\tMotor6:PositionInput\t13PICAM2:cam1:RepetitiveGateDelay\n'
          'Motor4:PositionRead\tMotor5:PositionRead\tMotor6:PositionRead\t13PICAM2:cam1:RepetitiveGateDelay_RBV\n')


positions = square_sweep_shape(4.4, 2.4, 0.2)#3.4, 3.75, 1.25, 0.2)
delay = 330

for i in range(len(positions[0])):  # x-axis
    y_range = range(len(positions[1])) if i % 2 == 0 else range(len(positions[1]) - 1, -1, -1)

    for j in y_range:  # y-axis
        z_range = range(len(positions[2])) if j % 2 == 0 else range(len(positions[2]) - 1, -1, -1)

        for k in z_range:  # z-axis
            for repetition in range(3):
                file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(
                    positions[0][i], positions[1][j], positions[2][k], delay))
                print(f'The data point {i}, {j}, and {k} has been done')
                delay +=1



print(positions[0], 'This is x_axis')
print(positions[1], 'This is the y_axis')
print(positions[2], 'This is the z-axis')






