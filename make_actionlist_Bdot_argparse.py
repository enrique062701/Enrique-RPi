#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:18:25 2025

@author: Enrique
This python file creates an action list that moves a Bdot probe in a sweep in the xy plane while keeping the z-plane constant. Removed the file.write variables to prevent from
the PV variables being publically available.

The file only writes the desired inputs to the file. It has the 'Motor:Read' because another data acquisition file requires it. This is to ensure that data is taken when the input and read 
variables match.
"""
import numpy as np
import argparse
import sys
import os
file = open("Bdot_actionlist.txt", "w")

file.write('Motor:Input\tMotor:Input\tMotor:Input\t13PICAM2:RepetitiveGateDelay\n'
          'Motor:Read\tMotor:Read\tMotor:Read\t13PICAM2:RepetitiveGateDelay_RBV\n')


#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#Make functions depending on the probe being used
def one_mm_lineout(step_size, repititions):
    x_center = 3.4
    x_positions_x = np.arange(1.9, 4.9, step_size)
    y_positions_x = [1.5, 2.7]
    z_position_x = 0.5
    delay = 330

    for i in range(len(y_positions_x)):
        x_range = range(len(x_positions_x)) if i % 2 == 0 else range(len(x_positions_x) -1, -1, -1)
        for j in x_range:
            for repition in range(repititions):
                file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(x_positions_x[j],y_positions_x[i], z_position_x, delay))
                delay += 10

    #Now for the y_axis lineout. Since it can not be evenly spaced, the final point must be added separetely
    x_positions_y = 3.4
    y_positions_y = np.arange(0.8, 2.3 + step_size, step_size)
    x_positions_y = 3.4

    for i in range(len(y_positions_y)):
        for repition in range(repititions):
            file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(x_positions_y, y_positions_y[i], z_position_x, delay))
            delay += 10

    #Adding the final point
    for repitition in range(repititions):
        file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(x_positions_y,2.7, z_position_x, delay))
        delay += 10
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def one_inch_lineout(step_size, repititions):
    #Change the coordinates for the 1in probe. So instead of rewriting the numbers and losing the previous values, just use a different function instead
    x_center = 3.0
    x_positions_x = np.arange(1.9, 4.9, step_size)
    y_positions_x = [1.5, 2.7]
    z_position_x = 0.5
    delay = 330

    for i in range(len(y_positions_x)):
        x_range = range(len(x_positions_x)) if i % 2 == 0 else range(len(x_positions_x) -1, -1, -1)
        for j in x_range:
            for repition in range(repititions):
                file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(x_positions_x[j],y_positions_x[i], z_position_x, delay))
                delay += 10

    #Now for the y_axis lineout. Since it can not be evenly spaced, the final point must be added separetely
    x_positions_y = 3.4
    y_positions_y = np.arange(0.8, 2.3 + step_size, step_size)
    x_positions_y = 3.4

    for i in range(len(y_positions_y)):
        for repition in range(repititions):
            file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(x_positions_y, y_positions_y[i], z_position_x, delay))
            delay += 10

    #Adding the final point
    for repitition in range(repititions):
        file.write("{:.3f}\t{:.3f}\t{:.3f}\t{:.0f}\n".format(x_positions_y,2.7, z_position_x, delay))
        delay += 10

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("function", nargs = "?", choices = ['one_mm_lineout', 'one_inch_lineout'],
                            default = 'one_mm_lineout')
    
    args, sub_args = base_parser.parse_known_args()

    function = args.function

    parser = argparse.ArgumentParser(
        prog = f"{os.path.basename(sys.argv[0])} {function}",
        description = f" Arguments for the {function}"
    )

    parser.add_argument('-a', type = float, required = True, help ="Argument a")
    parser.add_argument('-b', type = int, required = True, help = "Argument b")

    args = parser.parse_args(sub_args)

    if function == "one_mm_lineout":
        one_mm_lineout(args.a, args.b)

    elif function == "one_inch_lineout":
        one_inch_lineout(args.a, args.b)

