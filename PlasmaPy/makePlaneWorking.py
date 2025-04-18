import numpy as np
import os

def make_plane(x_start, x_stop, y_start, y_stop, z1, z2, z3, z4, x_bin, y_bin, m_offset, rep=1,
                 mode='P', l_d='x', l_pos=0):

    '''
    Make plane or linear action list from 4 corner reference points. Coordinates are motor coordinates.
    Do zigzag iteration that first goes in y direction
    x_start: smaller x coordinate of the reference points
    x_stop: larger x coordinate of the reference points
    y_start: smaller y coordinate of the reference points
    y_stop: larger y coordinates of the reference points
    z1, z2, z3, z4: four z coordinates of the 4 corners, in the order of x from small to large and then y from small to large.
    In other words, z1 at (x_start, y_start), z2 at (x_stop, y_start), z3 at (x_start, y_stop), z4 at (x_stop, y_stop).
    x_bin: number of bins in the x direction. Number of data points in the x direction is thus x_bin + 1.
    y_bin: number of bins in the y direction. These bins are also used in lineout modes
    m_offset: offset for the mirror coordinates. mirror_coordinate = motor_coordinate + m_offset
    rep: number of repetitions for each spatial point
    mode: set plane ('P') or lineout ('L') modes
    l_d: axis along which lineout points are taken
    l_pos: position where lineout is taken, in absolute coordinates. For example, if you want to take lineouts in y direction, 
    l_pos is the x coordinate of these lineout points
    WARNING: lineout modes have not been verified. Please check actionlist before implementing
    '''

    dir = './'
    name = 'actionList.txt'
    file = open(os.path.join(dir, name), 'w')
    file.write('RESOURCE ID=124' '\t' 'RESOURCE ID=124' '\t' 'RESOURCE ID=124' '\t' 'RESOURCE ID=122' '\n'
               'CHANNEL ID=0' '\t' 'CHANNEL ID=1' '\t' 'CHANNEL ID=2' '\t' 'CHANNEL ID=0' '\n'
               'UNIT=MM' '\t' 'UNIT=MM' '\t' 'UNIT=MM' '\t' 'UNIT=MM' '\n' '###')

    

    if mode == 'P':
        b = np.indices((x_bin + 1, y_bin + 1))
        xf = b[0] / x_bin
        yf = b[1] / y_bin
        z = (1 - xf - yf + xf*yf) * z1 + (xf - xf*yf) * z2 + (yf - xf*yf) * z3 + xf * yf * z4
        z = np.around(z, 4) # NOTE: here you can set significant digit for the action list


        xx = np.linspace(x_start, x_stop, x_bin + 1)
        yy = np.linspace(y_start, y_stop, y_bin + 1)
        x, y = np.meshgrid(xx, yy)
        x = np.transpose(x)
        y = np.transpose(y)
        for i in range(1, x_bin + 1, 2):
            x[i] = np.flip(x[i])
            y[i] = np.flip(y[i])
            z[i] = np.flip(z[i])


        xm = x + m_offset
        for xi in range(x_bin + 1):
            for yi in range(y_bin + 1):
                for i in range(rep):
                    file.write('\n')
                    s1 = str(x[xi][yi])
                    s2 = str(y[xi][yi])
                    s3 = str(z[xi][yi])
                    s4 = str(xm[xi][yi])
                    list = [s1, s2, s3, s4]
                    file.write('\t'.join(list))

    elif mode == 'L':
    # WARNING: lineout modes have not been verified. Please check actionlist before implementing
        if l_d == 'x':
            y = l_pos
            x = np.linspace(x_start, x_stop, x_bin + 1)
            z_start = z1 + (z3 - z1) * (l_pos - y_start) / (y_stop - y_start)
            z_stop = z2 + (z4 - z2) * (l_pos - y_start) / (y_stop - y_start)
            z = np.linspace(z_start, z_stop, x_bin + 1)
            for i in range(x_bin + 1):
                for i in range(rep):
                    file.write('\n')
                    s1 = x[i]
                    s2 = y
                    s3 = z[i]
                    s4 = x[i] + m_offest
                    list = [s1, s2, s3, s4]
                    file.write('\t'.join(list))
        elif l_d == 'y':
            x = l_pos
            y = np.linspace(y_start, y_stop, y_bin + 1)
            z_start = z1 + (z3 - z1) * (l_pos - x_start) / (x_stop - x_start)
            z_stop = z2 + (z4 - z2) * (l_pos - x_start) / (y_stop - x_start)
            z = np.linspace(z_start, z_stop, y_bin + 1)
            for i in range(y_bin + 1):
                for i in range(rep):
                    file.write('\n')
                    s1 = x
                    s2 = y[i]
                    s3 = z[i]
                    s4 = x + m_offest
                    list = [s1, s2, s3, s4]
                    file.write('\t'.join(list))
        else:
            raise Exception('Error: invalid sample direction. Please enter \'x\' or \'y\'.')
    file.close()

    

# Origin of physical frame in motor coordinates
x0 = 49
y0 = 91.3
z0 = 59

# Enter physical coordinates here. Assume positive x points to the right
x_start_p = 1
x_stop_p = 24
y_start_p = 5
y_stop_p = 24

x_start = x_start_p + x0
x_stop = x_stop_p + x0
y_start = y0 - y_start_p
y_stop = y0 - y_stop_p
# z coordinates are in motor coordinates
z1 = 57.9
z2 = 58.7
z3 = 58.2
z4 = 58.4
x_bin = 23
y_bin = 19
m_offest = 99.5
make_plane(x_start, x_stop, y_start, y_stop, z1, z2, z3, z4, x_bin, y_bin, m_offest, mode='P', rep=5)