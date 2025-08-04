import numpy as np 
import epics
import socket
import time
from urllib.request import urlopen
import re
"""
NOTE: THIS IS A COPY. FOR SAFTEY REASONS, THE IP HAS BEEN CHANGED, EVEN THOUGH IT IS A LOCAL NETWORK.

This script communicates with the NT230 Laser via TCP/IP using their REST API commands.
To find a list of all the possible commands, visit {BASE_URL}/list(). The commands vary very differently than the ones 
from the manual. Some examples of sending commands are:
BASE_URL = http://xxx.xxx.xxx.xxx:xxxx --> IP Address of device : Port used for communication
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
BASE_URL = http://xxx.xxx.xxx.xxx:xxxx/REST/HTTP_CMD --> Same IP address, different port. Now specify the REST API usage
I think it is better to use the second url method becasue it has less in the HTML file. It makes it easier to extract
the data from the HTML file, using less regular experessions. The difference is that there are more commands and possibilities
using the first url method. To send the command using the ASCII, it goes at following.
    BU = BASE_URL = http://xxx.xxx.xxx.xxx:xxxx/REST/HTTP_CMD
    Request:                                Description:
    {BU}/?RDVAR/State                       Laser State --> Ready or not ready
Check manual for the full list of commands or go to https://xxx.xxx.xxx.xxx:xxxx/REMOTECONTROL.CSV to find all the possible commands.
"""
#First define global variables and Constants
global command

BASE_URL = "http://xxx.xxx.xxx.xxx:xxxx/REST/HTTP_CMD"
BASE_URL_2 = "http://xxx.xxx.xxx.xxx:xxxx"
USER = "NT230Laser:"
# Next define the main PVs that we will be using for the laser
laser_wavelength = epics.PV(USER+"Wavelength")
laser_wavelength_RBV = epics.PV(USER+"WavelengthRBV")
laser_burstlength = epics.PV(USER+"Burstlength")
laser_burstlength_RBV = epics.PV(USER+"BurstlengthRBV")
laser_status = epics.PV(USER+"Status")


laser_wavelength.connect(timeout = 5)
laser_wavelength_RBV.connect(timeout = 5)
laser_burstlength.connect(timeout = 5)
laser_burstlength_RBV.connect(timeout = 5)
laser_status.connect(timeout = 5)


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
    #if type(command) != str:
    #    raise TypeError('Command must be in string!!')

    pattern = r'<br>\s*(.*?)\s*<br>' #The pattern to remove html and attain the raw strings only.
    link = urlopen(BASE_URL + command)
    webpage = link.read().decode("utf-8")

    clean = re.search(pattern, webpage)
    response = float(clean.group(1))
    return response


def change_wavelength_callback(pvname = None, value = None, char_value = None, **kwargs):
    """
    Function that sends commands to the laser. It sends a new command when the callback function is updated.
    Double checks that the wavelength is changed by comparing the inputted value and the read back value.
    """
    try:
        if not (210.0 <= value <= 2600.0):
            raise KeyError(f"{value} is out of range. Choose wavelength between 210nm - 2600nm")

        #value_str = str(value)
        command = f"{BASE_URL}/?EXE/SetWL/{value}"
        urlopen(command)
        time.sleep(0.05) #Must wait 0.05 seconds before trying to read the callback value.
        # To check if the value updated:
        command_rbv = f"/?RDVAR/Wavelength"
        response = read_command(command_rbv)
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
    time.sleep(0.05)
    # To check if the value updated:
    command_rbv = f"/?RDVAR/PRR"
    response = read_command(command_rbv)
    write_pv(laser_burstlength_RBV, response)
    
    if value != response:
        raise ValueError("The value and readback values do not match. Try again.")
    else:
        print(f"The burstlength has been sent to: {response}")
    except Exception as e:
        print(f"An error has occured: {e}")


# Initialize PVs
write_pv(laser_wavelength, 0)
write_pv(laser_burstlength_RBV, 0)
write_pv(laser_burstlength, 0)
write_pv(laser_burstlength_RBV, 0)


laser_wavelength.add_callback(change_wavelength_callback)
laser_burstlength.add_callback(change_burstlength_callback)


###############################################################################
#To keep the python script running forever
while True:
    epics.ca.poll()
    time.sleep(0.01)

