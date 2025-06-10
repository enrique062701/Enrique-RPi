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
import os
import sys


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


def desired_positions(location, delay_shift, blowoff_delay, repititions):
    """
    Parameters
    -User enters a number that corelates to the location they wish to acquire data at. Coordiantes are entered in TCC.
    The z-axis changes as the location changes. Must be calibrated before each run.

    Returns
    Will return the positions of the motors (1-6) in motor coordinates. Will also change the delay for the Thomson and the self-emission camera

    """

    file = open('actionlist-tsline.txt', 'w')
    file.write("Motor1:PositionInput\tMotor2:PositionInput\tMotor3:PositionInput\tMotor4:PositionInput\tMotor5:PositionInput\tMotor6:PositionInput\tTS:1w2wDelay\tTS:Shutter\t13PICAM2:cam1:RepetitiveGateDelay\n"
                "Motor1:PositionRead\tMotor2:PositionRead\tMotor3:PositionRead\tMotor4:PositionRead\tMotor5:PositionRead\tMotor6:PositionRead\tTS:1w2wDelay\tTS:Shutter\t13PICAM2:cam1:RepetitiveGateDelay_RBV\n")

    #First step is to convert your TCC coordinates to motor coordinates
    location_matrix = np.array([[0, - 0.9, - 0.85], #Location 1
                                [0, - 1.3, - 0.85], #Location 2
                                [0, - 1.8, - 0.85], #Location 3
                                [0, - 2.1, - 0.85], #Location 4
                                [0, - 2.3, - 0.85], #Location 5
                                [0, - 2.7, - 0.85]]) #Location 6
    location_map = {
        'Location1': 0,
        'Location2': 1,
        'Location3': 2,
        'Location4': 3,
        'Location5': 4,
        'Location6': 5
    }
    delay_matrix = np.array([[110 , 150, 160, 170, 210], #Location 1
                              [140, 190, 210, 230, 280] , #Location 2
                              [190, 230, 260, 290, 330], #Location 3
                              [300, 370, 400, 430, 500], #Location 4
                              [350, 420, 450, 480, 550], #Location 5
                              [480, 600, 630, 660, 780]])#Location 6

    if location in location_map:
        idx = location_map[location]
        motors = TCC_to_motor(location_matrix[idx])
        delays = delay_matrix[idx] - delay_shift

    print(*motors)

    for delay in range(len(delays)):
        for repitition in range(repititions):
            file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motors[0], motors[1], motors[2], motors[3], motors[4], motors[5], delays[delay],0, blowoff_delay))
            file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motors[0], motors[1], motors[2], motors[3], motors[4], motors[5], delays[delay],0, blowoff_delay))
            file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motors[0], motors[1], motors[2], motors[3], motors[4], motors[5], delays[delay],1, blowoff_delay))
            file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\t{:.0f}\t{:.0f}\n".format(motors[0], motors[1], motors[2], motors[3], motors[4], motors[5], delays[delay],1, blowoff_delay))
            blowoff_delay += 10


if __name__ == "__main__":
    base_parser = argparse.ArgumentParser(add_help = False)
    base_parser.add_argument("function", nargs = "?", choices = ["desired_positions"], default = "desired_positions") #Can add future functions here

    args, sub_args = base_parser.parse_known_args()

    function = args.function

    parser = argparse.ArgumentParser(
        prog = f"{os.path.basename(sys.argv[0])} {function}",
        description = f" Arguments for the {function}"
    )

    parser.add_argument('-a', type = str, required = True, help = "Location")
    parser.add_argument('-b', type = float, required = True, help = "TS delay at certain location")
    parser.add_argument('-c', type = int, required = True, help = "Delay for blast wave camera")
    parser.add_argument('-d', type = int, required = True, help = "Number of shots per location")

    args = parser.parse_args(sub_args)

    if function == "desired_positions":
        desired_positions(args.a, args.b, args.c, args.d)









