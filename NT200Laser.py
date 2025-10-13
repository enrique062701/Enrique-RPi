import numpy as np 
import epics
import socket
import time
from urllib.request import urlopen
import re
"""
This script communicates with the NT230 Laser via TCP/IP using their REST API commands.
To find a list of all the possible commands, visit {BASE_URL}/list(). The commands vary very differently than the ones 
from the manual. Some examples of sending commands are:
BASE_URL = http://10.97.106.119:8080 --> IP Address of device : Port used for communication
The rest of the examples will abbreviate the base url to {BU}:
    Name:                                           Syntax:
    Communication test                      |       {BU}/
    Device ID                               |       {BU}/id()
    Register list query                     |       {BU}/list()
    Read Command                            |       {BU}/(Module Name)/(ID)/(Register Name)
    Write Command                           |       {BU}/(Module Name)/(ID)/(Register Name)/(Value)
    Write to NVRAN command                  |       {BU}/(Module Name)/(ID)/(Register Name)/(Value)/NV
    Start/stop logging register updates     |       {BU}/(Module Name)/(ID)/(Register Name)/logstart()/(buffer size in bytes) --> Refer to manual for diff byte sizes. 
    Receive values with timestamps fro

There is also another method for sending commands - using the same commands as the RS232 command set in the manual
The base url is different:
BASE_URL = http://10.97.106.119:8081/REST/HTTP_CMD --> Same IP address, different port. Now specify the REST API usage
I think it is better to use the second url method becasue it has less in the HTML file. It makes it easier to extract
the data from the HTML file, using less regular experessions. The difference is that there are more commands and possibilities
using the first url method. To send the command using the ASCII, it goes at following.
    BU = BASE_URL = http://10.97.106.119:8081/REST/HTTP_CMD
    Request:                                Description:
    {BU}/?RDVAR/State                       Laser State --> Ready or not ready
Check manual for the full list of commands or go to https://10.97.106.119:8080/REMOTECONTROL.CSV to find all the possible commands.
"""
#First define global variables and Constants

BASE_URL = "http://10.97.106.119:8081/REST/HTTP_CMD"
BASE_URL_2 = "http://10.97.106.119:8080"
USER = "NT230Laser:"
# Next define the main PVs that we will be using for the laser
print("Defining PVs...")
laser_wavelength = epics.PV(USER+"Wavelength")
laser_wavelength_RBV = epics.PV(USER+"WavelengthRBV")
laser_burstlength = epics.PV(USER+"Burstlength")
laser_burstlength_RBV = epics.PV(USER+"BurstlengthRBV")
laser_status = epics.PV(USER+"STATE")
laser_temp = epics.PV(USER+"Temperature")
lifetime_shots = epics.PV(USER+"LifetimeShots")

laser_trigger_type = epics.PV(USER+"TriggerType")
laser_trigger_typeRBV = epics.PV(USER+"TriggerTypeRBV")
phoenix_epoch = epics.PV("phoeniX:epoch") #To check temp and other diagnostics every second

print(f"Connecting to PV's...")
laser_wavelength.connect(timeout = 5)
laser_wavelength_RBV.connect(timeout = 5)
laser_burstlength.connect(timeout = 5)
laser_burstlength_RBV.connect(timeout = 5)
laser_status.connect(timeout = 5)
laser_temp.connect(timeout = 5)
lifetime_shots.connect(timeout = 5)
laser_trigger_type.connect(timeout = 5)
laser_burstlength_RBV.connect(timeout = 5)
phoenix_epoch.connect(timeout = 5)
print("Connection Successful!")
############################################################################################################
# Next is to define the functions that will be used.
def write_pv(pv, value):
    try:
        if pv.connected:
            pv.put(value, wait = True, timeout = 0.05)
        else:
            print(f"Faild to connect to {pv.name}.")
    except:
        print(f"PV Error on {pv.pvname}")


def read_command(command):
    """
    This function will only retrieve data from the laser. It will not change any parameters or values. Can be
    used as the callback function.
    Input:
        Input the command of the information you would like to retrive. Commands must be inputted as strings

    Return:
        Returns the value of the desired value
    """
    command = str(command)
    if "?" in command:
        #This is to see whether the first or second url method is used instead of making a new function with new patterns.
        pattern = r'<br>\s*(.*?)\s*<br>' #The pattern to remove html and attain the raw strings only.
        link = urlopen(BASE_URL + command)
        webpage = link.read().decode("utf-8")
        clean = re.search(pattern, webpage)
        response = clean.group(1)
        return response
    else:
        pattern = r'<td id=V1>([\d.]+)C</td>'
        link = urlopen(BASE_URL_2 + command)
        webpage = link.read().decode("utf-8")
        clean = re.search(pattern, webpage)
        response = clean.group(1)
        return response


def turn_laser_on(pvname = None, value = None, char_value = None, **kwargs):
    """
    This function will allow the user to remotely turn the laser on or off. Have not tested because laser safety is not 
    set ip properly. Need to wait set up proper beam dumps, etc. If PV == 1, laser status to run. If PV == 0, laser status is stop.
    """
    if value == 1:
        command = f"{BASE_URL}/?EXE/Run"
        url(command)
        time.sleep(0.07)
        print(f"The laser has started running!")
    elif value == 0:
        command = f"{BASE_URL}/?EXE/Stop"
        url(command)
        time.sleep(0.07)
        print(f"The laser has stoped running!")

    state = read_command("/?RDVAR/State")
    write_pv(laser_status, state)
    print(f"The state of the laser is now {state}")


def change_wavelength_callback(pvname = None, value = None, char_value = None, **kwargs):
    """
    Function that sends commands to the laser. It sends a new command when the callback function is updated.
    Double checks that the wavelength is changed by comparing the inputted value and the read back value.
    """
    try:
        if not (210.0 <= value <= 2600.0):
            raise KeyError(f"{value} is out of range. Choose wavelength between 210nm - 2600nm")
        else:
            #value_str = str(value)
            command = f"{BASE_URL}/?EXE/SetWL/{value}"
            urlopen(command)
            time.sleep(0.07) #Must wait 0.05 seconds before trying to read the callback value.
            # To check if the value updated:
            command_rbv = f"/?RDVAR/Wavelength"
            response = float(read_command(command_rbv))
            write_pv(laser_wavelength_RBV, response)
            if value != response:
                raise ValueError("The wavelength did not change. Try again.")
            else:
                print(f"The wavelength has been set to: {response}")
        
    except Exception as e:
        print(f"An error occured: {e}")


def change_burstlength_callback(pvname = None, value = None, char_value = None, **kwargs):
    """
    Function that sens commands to the laser to change the burstlength of the laser. Similar to the wavelength function.
    """
    try:
        if not (1.0 <= value <= 65535.0):
            raise KeyError(f"{value} is out of range. Chose burstlength between 1 and 65535.")
    
        command = f"{BASE_URL}/?EXE/BurstLn/{value}"
        urlopen(command)
        time.sleep(0.07)
        # To check if the value updated:
        command_rbv = f"/?RDVAR/PRR"
        response = read_command(command_rbv)
        write_pv(laser_burstlength_RBV, response)
        print(f"The burstlength has been set too: {value}")
        
        #if value != response:
        #    raise ValueError("The value and readback values do not match. Try again.")
        #else:
            #print(f"The burstlength has been sent to: {response}")
    except Exception as e:
        print(f"An error has occured: {e}")


def diagnostics_callback(pvname = None, value = None, char_value = None, **kwargs):
    """
    Function that checks different diagnostics such as temp every second to ensure laser is working properly.
    """
    Temperature = read_command("/UniLDM/16/Tpp")
    write_pv(laser_temp, Temperature)
    print(f"The temperature is: {Temperature}")

    LifetimeShots = read_command("/?RDVAR/TotalShots")
    write_pv(lifetime_shots, LifetimeShots)
    print(f"The total number shots throughout laser history is: {LifetimeShots}")
    # Will add other diagnostics depending on what chris wants.


shot_history = 0 # Will store the total number of shots in this list
last_trigger_time = None
time_out = 900 # Clears the total shot counter 15 minutes after not recieving a trigger.


def shot_count(pvname = None, value = None, char_value = None, **kwargs):
    """
    This callback function will count the number of shots taken per run. The command '/?RDVAR/TotalShots' only list the total number of shots
    taken throughout its entire lifestyle. The way to count the total number of shots taken per run will be by starting a counter and adding 1 to it
    each time the laser is triggered. 
    ### Need to define the trigger. What PV will be used as trigger or how will we trigger it?
    """
    global last_trigger_time
    global shot_history

    current = time.time()

    if (last_trigger_time is None or current - last_trigger_time > time_out):
        print("Timeout reached - resetting shot count")
        shot_history = 0

    shot_history += 1
    epics.caput(f"{USER}ShotsPerRun", shot_history)
    time.sleep(0.01)
    last_trigger_time = current
    print(f"Total number of shots is {shot_history}")


def set_trigger_type(pvname = None, value = None, char_value = None, **kwargs):
    """
    Allows the user to set the trigger to external or external. 
    """
    if value == 0:
        command = f"{BASE_URL}/?EXE/SetSyncMode/Internal"
        urlopen(command)
        time.sleep(0.07)
    else:
        command = f"{BASE_URL}/?EXE/SetSyncMode/External"
        urlopen(command)
        time.sleep(0.07)
    # To check look at readback value
    trigger_type = read_command("/?RDVAR/SyncMode")
    write_pv(laser_trigger_typeRBV, trigger_type)
    print(f"The trigger type has been set to: {trigger_type}")
    
# Initialize PVs
print("Initializing PVs...")
write_pv(laser_wavelength, 0)
write_pv(laser_wavelength_RBV, 0)
write_pv(laser_burstlength, 0)
write_pv(laser_burstlength_RBV, 0)
write_pv(laser_temp, 0)


laser_wavelength.add_callback(change_wavelength_callback)
laser_burstlength.add_callback(change_burstlength_callback)
phoenix_epoch.add_callback(diagnostics_callback)
phoenix_epoch.add_callback(shot_count) # Add a different one depending on what will be used as trigger. Maybe camera??
laser_trigger_type.add_callback(set_trigger_type)
print("Program ready to go!")
###############################################################################
#To keep the python script running forever
while True:
    epics.ca.poll()
    time.sleep(0.01)

