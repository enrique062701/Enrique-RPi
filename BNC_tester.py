"""
This script will run multiple tests on the BNC boxes to see if they are able to operate properly. It will test the
latency, the response time, exceptions, and accuracy.
Enrique C.
"""
import epics
import numpy
import os 
import socket
import time

USER = "BNC1:"

#Next step is to create delays by testing the limits of the bnc:
#Can range from T0 to 999.99999999975s after T0 (or channel synced too), so from 0s to MAX
MAX = 999.99999999975

Delays = np.arange(0, MAX, 1) #Do intervals of 1s for the first rounf
Delays_small = np.arange(0, 0.5, 0.0001) # This will be 5,000 trials. 
Delay_limits = [1, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001, 0.0000000001, 0.00000000001, 0.000000000001] # This will test the precision of the bnc


# The first step is too initialize dictionaries for corresponding channels and values. 

channel_delays = {
    "Ch1" : Delays,
    "Ch2" : Delays,
    "Ch3" : Delays,
    "Ch4" : Delays,
    "Ch5" : Delays,
    "Ch6" : Delays,
    "Ch7" : Delays,
    "Ch8" : Delays,
}
 
channel_delays_small = {
    "Ch1" : Delays_small,
    "Ch2" : Delays_small,
    "Ch3" : Delays_small,
    "Ch4" : Delays_small,
    "Ch5" : Delays_small,
    "Ch6" : Delays_small,
    "Ch7" : Delays_small,
    "Ch8" : Delays_small,
}

channel_delays_limits = {
    "Ch1" : Delay_limits,
    "Ch2" : Delay_limits,
    "Ch3" : Delay_limits,
    "Ch4" : Delay_limits,
    "Ch5" : Delay_limits,
    "Ch6" : Delay_limits,
    "Ch7" : Delay_limits,
    "Ch8" : Delay_limits,
}

# The next step is to initialize the dictionaries for the width of the waveform.
# Can do width from 10 ns to 999.99999999975
width_small = np.arange(0, 0.0000001, 0.000000001)
width_regular = np.arange(0, MAX, 1)

delay = 0.01 #Delay to see how fast we can input the PVs without crashing the program. 

for keys, items in channel_delays.items():
    epics.caput(f"{USER}{keys}:Delay", items)















