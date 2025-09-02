import numpy as np 
import can
import os
import time

"""
This file will rotate through different bitrates to see if it picks up anything.
Enrique C
"""

# First step is to create the different bitrates you would want to cycle through
min_ = 10000
max_ = 500000
step_size = 1000
bitrates = np.arange(min_, max_ + step_size, step_size) # I want it to cycle through intervals of 1000 bitrates, starting at 11000. ChatGPT says that laser might be 15360 bits/s
bitrates = np.insert(bitrates, 6, 15360) #Adding the 15360

# Next is to find the can port to see if it is active
os.system('sudo /sbin/ip link set can0 up type can bitrate 500000') # This is what the company does for startup
try:
    bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan' )
except OSError:
     print('Can not find port, double check if it is on or working')

print('Port has been found, ready to cycle through bitrates.')

# Next step is to shut down the port to change the bitrate
os.system('sudo ip link set can0 down')

#The next step is to rotate through the bitrates
for bitrate in bitrates:
    os.system('sudo ip link set can0 down') # Set it down after each bitrate
    os.system(f'sudo ip link set can0 type can bitrate {bitrate}')
    os.system('sudo ip link set can0 up')
    print(f'Starting the cycle. On bitrate: {bitrate}. Will timeout after 10 seconds of listening.')
    os.system('timeout 10 candump can0')
    print('Moving to the next bitrate') 






