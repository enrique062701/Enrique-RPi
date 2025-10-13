"""
This script will run multiple tests on the BNC boxes to see if they are able to operate properly. It will test the
latency, the response time, exceptions, and accuracy.
Enrique C.
"""
import epics
import subprocess
import numpy as np
import threading
import socket
import time

USER = "BNC1:"

#Next step is to create delays by testing the limits of the bnc:
#Can range from T0 to 999.99999999975s after T0 (or channel synced too), so from 0s to MAX
MAX = 999.99999999975

Delays = np.arange(0, MAX, 1) #Do intervals of 1s for the first rounf
Delays_small = np.arange(0, 0.5, 0.0001) # This will be 5,000 trials. 
Delay_limits = [1, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001, 0.0000000001, 0.00000000001] # This will test the precision of the bnc


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
width_small = np.arange(0, 0.0000001, 0.00000001)
width_regular = np.arange(0, MAX, 1)

channel_width = {
    "Ch1" : width_regular,
    "Ch2" : width_regular,
    "Ch3" : width_regular,
    "Ch4" : width_regular,
    "Ch5" : width_regular,
    "Ch6" : width_regular,
    "Ch7" : width_regular,
    "Ch8" : width_regular,
}
 
channel_width_small = {
    "Ch1" : width_small,
    "Ch2" : width_small,
    "Ch3" : width_small,
    "Ch4" : width_small,
    "Ch5" : width_small,
    "Ch6" : width_small,
    "Ch7" : width_small,
    "Ch8" : width_small,
}

channel_width_limits = {
    "Ch1" : Delay_limits,
    "Ch2" : Delay_limits,
    "Ch3" : Delay_limits,
    "Ch4" : Delay_limits,
    "Ch5" : Delay_limits,
    "Ch6" : Delay_limits,
    "Ch7" : Delay_limits,
    "Ch8" : Delay_limits,
}



#delay = 0.01 #Delay to see how fast we can input the PVs without crashing the program. 


def delay_loop(dictionary, USER, delay):
    delay_per_channel = []
    count = 0
    start_time = time.time() #Keep track of the time

    for channel, values in dictionary.items():
        start_time2 = time.time()
        for value in values:
            try:
                epics.caput(f"{USER}{channel}:Delay", value)
                time.sleep(delay)
                count += 1 #This is so you can know which delay it crashed on by indexing later.
                print(f"Done with the value: {value}")

            except socket.error as e:
                print(f'Socket error occured: {e}')

            except Exception as e:
                print(f"Error occured {e}. It occured at {count} with delay {value[count]}")

        target_value = values[-1] # Gets the final value in the list
        timeout = 100 # Timout after 100s.
        precision = 1e-9 # Nanosecond precision for the BNC 575

        while True:
            current_value = epics.caget(f"{USER}{channel}:Delay_RBV")
            if current_value is None:
                print(f"Epics is not responding... Check for socket errors or EPICS errors.")
            
            elif abs(current_value - value) <= precision: #Doing absoulute difference instead of "==" bc of float precision. BNC limit is 10ns so ns precision is required.
                total_time = time.time() - start_time2
                delay_per_channel.append(total_time) # Append the time it takes for the device to catch up
                print(f"The BNC has now caught up in values. The BNC RBV is: {current_value} and the value is: {value}")
                break        

        print(f"Done with channel: {channel}. It took a totla of {time.time() - start_time2} to complete")

    print(f"Total time for this function to finish is: {time.time() - start_time}")
    average = np.average(delay_per_channel)

    return average


def width_loop(dictionary, USER, delay):
    width_per_channel = []
    count = 0
    start_time = time.time() #Keep track of the time

    for channel, values in dictionary.items():
        start_time2 = time.time()
        for value in values:
            try:
                epics.caput(f"{USER}{channel}:Width", value)
                time.sleep(delay)
                count += 1 #This is so you can know which delay it crashed on by indexing later.
                print(f"Done with the value: {value}")

            except socket.error as e:
                print(f'Socket error occured: {e}')

            except Exception as e:
                print(f"Error occured {e}. It occured at {count} with delay {value[count]}")

        target_value = values[-1] # Gets the final value in the list
        timeout = 500 # Timout after 100s.
        precision = 1e-9 # Nanosecond precision for the BNC 575

        while True:
            current_value = epics.caget(f"{USER}{channel}:Width_RBV")
            if current_value is None:
                print(f"Epics is not responding... Check for socket errors or EPICS errors.")
            
            elif abs(current_value - value) <= precision: #Doing absoulute difference instead of "==" bc of float precision. BNC limit is 10ns so ns precision is required.
                total_time = time.time() - start_time2
                width_per_channel.append(total_time) # Append the time it takes for the device to catch up
                print(f"The BNC has now caught up in values. The BNC RBV is: {current_value} and the value is: {value}")
                break
            if time.time() - start_time2 < timeout:
                print(f"Timeout has been reached. Breaking the loop")
                break

        print(f"Done with channel: {channel}. It took a totla of {time.time() - start_time2} to complete")

    print(f"Total time for this function to finish is: {time.time() - start_time}")
    average = np.average(width_per_channel)

    return average    

            
def all_loop(USER, channels):
    """
    This function will generate random numbers to feed into all of the channels at the same time instead of just one 
    channel at a time.
    """
    channels = np.linspace(1, channels, 1)
    delays = np.random.default_rng().uniform(0.001,0.01, size = 100)
    



try:
    delays = np.arange(0.01, 0.1, 0.01)
    print(delays)
    averages = []
    for delay in delays:
        #reg_delay = delay_loop(channel_delays, USER, delay)
        #small_delay = delay_loop(channel_delays_small, USER, delay)
        limits_delay = delay_loop(channel_delays_limits, USER, delay)
        #reg_width = width_loop(channel_width, USER, delay)
        #small_width = width_loop(channel_width_small, USER, delay)
        limits_width = width_loop(channel_width_limits, USER, delay)
        #np.savez(f"Average_delay_delay_{delay}.npz", Delays_normal = reg_delay, Small_delay = small_delay, Limits_delay = limits_delay, Width_normal = reg_width,
        #Small_width = small_width, Limits_width = limits_width)
        

# Notice that there is a problem with the limits in the width. Crashes when the width changes to 1e-12



except Exception as e:
    print(f"An error occured: {e}")
    














