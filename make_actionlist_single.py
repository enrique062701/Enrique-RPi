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

    location_matrix = np.array([[0, - 0.9, - 0.85], #Location 1
                                [0, - 1.3, - 0.85], #Location 2
                                [0, - 1.8, - 0.85], #Location 3
                                [0, - 2.1, - 0.85], #Location 4
                                [0, - 2.3, - 0.85], #Location 5
                                [0, - 2.7, - 0.85]]) #Location 6
    location_map = {
        'Location 1': 0,
        'Location 2': 1,
        'Location 3': 2,
        'Location 4': 3,
        'Location 5': 4,
        'Location 6': 5
    }

    #motor_positions[6] += motor_positions[6] + float(delay_shift)

    delay_matrix = np.array([[110 + delay_shift, 150 + delay_shift, 160 + delay_shift, 170 + delay_shift, 210 + delay_shift], #Location 1
                              [140 + delay_shift, 190 + delay_shift, 210 + delay_shift, 230 + delay_shift, 280 + delay_shift] , #Location 2
                              [190 + delay_shift, 230 + delay_shift, 260 + delay_shift, 290 + delay_shift, 330 + delay_shift], #Location 3
                              [300 + delay_shift, 370 + delay_shift, 400 + delay_shift, 430 + delay_shift, 500 + delay_shift], #Location 4
                              [350 + delay_shift, 420 + delay_shift, 450 + delay_shift, 480 + delay_shift, 550 + delay_shift], #Location 5
                              [480, 600, 630, 660, 780]])#Location 6


    if location in location_map:
        idx = location_map[location]
        motors = TCC_to_motor(location_matrix[idx])
        return *motors, delay_matrix[idx]

file = open('actionlist-tsline.txt', 'w')
    file.write("Motor1:PositionInput\tMotor2:PositionInput\tMotor3:PositionInput\tMotor4:PositionInput\tMotor5:PositionInput\tMotor6:PositionInput\tTS:1w2wDelay\tTS:Shutter\t13PICAM2:cam1:RepetitiveGateDelay\n"
               "Motor1:PositionRead\tMotor2:PositionRead\tMotor3:PositionRead\tMotor4:PositionRead\tMotor5:PositionRead\tMotor6:PositionRead\tTS:1w2wDelay\tTS:Shutter\t13PICAM2:cam1:RepetitiveGateDelay_RBV\n")

motor_positions = desired_positions('Location 4', 70)
blowoff_delay = 1120

delay_total = len(motor_positions[6])
print(motor_positions)

print(motor_positions[6], 'These are the delays')

for delay in range(len(motor_positions[6])):
    for repitition in range(repititions):
        file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[0], motor_positions[1], motor_positions[2], motor_positions[3], motor_positions[4], motor_positions[5], motor_positions[6][delay],0, blowoff_delay))
        file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[0], motor_positions[1], motor_positions[2], motor_positions[3], motor_positions[4], motor_positions[5], motor_positions[6][delay],0, blowoff_delay))
        file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[0], motor_positions[1], motor_positions[2], motor_positions[3], motor_positions[4], motor_positions[5], motor_positions[6][delay],1, blowoff_delay))
        file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motor_positions[0], motor_positions[1], motor_positions[2], motor_positions[3], motor_positions[4], motor_positions[5], motor_positions[6][delay],1, blowoff_delay))
        blowoff_delay += 10


if __name__ == "__main__":
    base_parser = argparse.ArgumentParser(add_help = False)
    base_parser.add_argument()


















