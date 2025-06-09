#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 10:31:17 2025
This actionlist will stay at the desired motor position throughout the acquisition.
@author: Enrique
"""
import numpy as np
import argparse
import epics


def TCC_to_motor(array):
    x,y,z = array

    x_beam_offset = epics.caget('TS:BeamOffsetX')
    y_beam_offset = epics.caget('TS:BeamOffsetY')
    z_beam_offset = epics.caget('TS:BeamOffsetZ')

    x_collection_offset = epics.caget('TS:CollectionOffsetX')
    y_collection_offset = epics.caget('TS:CollectionOffsetY')
    z_collection_offset = epics.caget('TS:CollectionOffsetZ')

    motor1 = x_beam_offset + x
    motor2 = y_beam_offset + y
    motor3 = z_beam_offset + z

    motor4 = x_collection_offset + x
    motor5 = y_collection_offset + y
    motor6 = z_collection_offset + z
    return motor1, motor2, motor3, motor4, motor5, motor6


def desired_positions(location, delay_shift):
    """
    Parameters
    -User enters a number that corelates to the location they wish to acquire data at. Coordiantes are entered in TCC.
    The z-axis changes as the location changes. Must be calibrated before each run.

    Returns
    Will return the positions of the motors (1-6) in motor coordinates. Will also change the delay for the Thomson and the self-emission camera

    """
    #First step is to convert your TCC coordinates to motor coordinates

    location_matrix = np.array([[0, - 0.9, - 0.85],
                                [0, - 1.3, - 0.85],
                                [0, - 1.8, - 0.85],
                                [0, - 2.1, - 0.85],
                                [0, - 2.3, - 0.85],
                                [0, - 2.7, - 0.85]])

    #motor_positions[6] += motor_positions[6] + float(delay_shift)

    delay_matrix = np.array([[110 + delay_shift, 150 + delay_shift, 160 + delay_shift, 170 + delay_shift, 210 + delay_shift], #Location 1
                              [140 + delay_shift, 190 + delay_shift, 210 + delay_shift, 230 + delay_shift, 280 + delay_shift] , #Location 2
                              [190 + delay_shift, 230 + delay_shift, 260 + delay_shift, 290 + delay_shift, 330 + delay_shift], #Location 3
                              [300 + delay_shift, 370 + delay_shift, 400 + delay_shift, 430 + delay_shift, 500 + delay_shift], #Location 4
                              [350 + delay_shift, 420 + delay_shift, 450 + delay_shift, 480 + delay_shift, 550 + delay_shift], #Location 5
                              [480, 600, 630, 660, 780]])#Location 6


    for location in range(len(location_matrix)):
        pass

    if location == 'Location1':
        motor1, motor2, motor3, motor4, motor5, motor6 = TCC_to_motor(location_matrix[0])
        return motor1, motor2, motor3, motor4, motor5, motor6, delay_matrix[0]

    if location == 'Location2':
        motor1, motor2, motor3, motor4, motor5, motor6 = TCC_to_motor(location_matrix[1])
        return motor1, motor2, motor3, motor4, motor5, motor6, delay_matrix[1]

    if location == 'Location3':
        motor1, motor2, motor3, motor4, motor5, motor6 = TCC_to_motor(location_matrix[2])
        return motor1, motor2, motor3, motor4, motor5, motor6, delay_matrix[2]

    if location == 'Location4':
        motor1, motor2, motor3, motor4, motor5, motor6 = TCC_to_motor(location_matrix[3])
        return motor1, motor2, motor3, motor4, motor5, motor6, delay_matrix[3]

    if location == 'Location5':
        motor1, motor2, motor3, motor4, motor5, motor6 = TCC_to_motor(location_matrix[4])
        return motor1, motor2, motor3, motor4, motor5, motor6, delay_matrix[4]

    if location == 'Location6':
        motor1, motor2, motor3, motor4, motor5, motor6 = TCC_to_motor(location_matrix[5])
        return motor1, motor2, motor3, motor4, motor5, motor6, delay_matrix[5]





if __name__ == "__main__":
    repititions = 5

    file = open('actionlist-tsline.txt', 'w')
    file.write("TS:1w2wDelay\tTS:Shutter\t13PICAM2:cam1:RepetitiveGateDelay\n"
               "TS:1w2wDelay\tTS:Shutter\t13PICAM2:cam1:RepetitiveGateDelay_RBV\n")

    motor_positions = desired_positions('Location4', 70)
    blowoff_delay = 1120

    delay_total = len(motor_positions[6])


    print(motor_positions[6], 'These are the delays')

    for delay in range(len(motor_positions[6])):
        for repitition in range(repititions):
            file.write("{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[6][delay],0, blowoff_delay))
            file.write("{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[6][delay],0, blowoff_delay))
            file.write("{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[6][delay],1, blowoff_delay))
            file.write("{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[6][delay],1, blowoff_delay))
            blowoff_delay += 10


















