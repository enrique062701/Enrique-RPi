import time
import time
import ctypes
import os
from ctypes import *

# demo for device control.  
# The demo is only for the reference of the device control, please refer to the device manual for the real control logic and parameters.



# # Read register value from the device 
#     This is a simplified version of reading a value from a device register. 
#     Modify the function if you need to:
#       - Retrieve the read status (`operationStatus`) for error handling.
#       - Access the timestamp of the read operation.
#       - Adjust the timeout value for the operation.
# #asString (bool): 
#             - If True, returns the register value as a string.
#             - If False, returns the register value as a double (floating-point number).
# 
#      
def read_register(deviceNameId, registerName, asString = True):    
    # Sets up the device name and ID 
    deviceNameIdBuf = create_string_buffer(128)
    deviceNameIdBuf.value = (deviceNameId).encode()
     # Sets up the register name to read data from
    registerNameBuf = create_string_buffer(128)
    registerNameBuf.value = registerName.encode()

    if asString == True:
        readRegisterValue = dll.rcGetRegAsString2

        # Specify argument and return types for the DLL function
        readRegisterValue.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int ,ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        readRegisterValue.restype = ctypes.c_int

        # Create a buffer to hold the read value
        maxvallen = 512  # maximum length of value string, including terminating character
        readValueBuffer = create_string_buffer(maxvallen)

        # Create a timestamp variable
        timestamp = ctypes.c_int(0)
        
        #  timeout:   timeout in milliseconds. (-1) - infinite timeout
        timeout = -1

        #  Check the operationStatus status, return one of  RMTCTRLERR_xxx  list
        operationStatus = readRegisterValue(connectionHandle, deviceNameIdBuf, registerNameBuf, readValueBuffer, maxvallen, timeout, ctypes.byref(timestamp))
        return readValueBuffer.raw.decode('utf-8').strip().strip('\x00')
    else:
        readRegisterValue = dll.rcGetRegAsDouble2

        # Specify argument and return types for the DLL function
        readRegisterValue.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        readRegisterValue.restype = ctypes.c_int
        readValueBuffer = ctypes.c_double(0)
        timestamp = ctypes.c_int(0)

         #  timeout:   timeout in milliseconds. (-1) - infinite timeout
        timeout = -1

        #  Check the operationStatus status, return one of  RMTCTRLERR_xxx  list
        operationStatus = readRegisterValue(connectionHandle, deviceNameIdBuf, registerName, readValueBuffer, timeout, ctypes.byref(timestamp))   
    return readValueBuffer
    
def write_register(deviceNameId, registerName, value):
    if type(value) is str:
        setRegisterValueAsString  = dll.rcSetRegFromString2
         # Specify argument and return types for the DLL function
        setRegisterValueAsString.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        setRegisterValueAsString.restype = ctypes.c_int
        
        # Sets up the device name and ID 
        deviceNameIdBuf = create_string_buffer(128)
        deviceNameIdBuf.value = deviceNameId.encode()
        
        # Sets up the register 
        registerNameBuf = create_string_buffer(128)
        registerNameBuf.value = registerName.encode()

        writeValueBuffer = create_string_buffer(512)
        writeValueBuffer = value.encode()

        #  Check the operationStatus status, return one of  RMTCTRLERR_xxx  list
        operationStatus = setRegisterValueAsString(connectionHandle, deviceNameIdBuf, registerNameBuf, writeValueBuffer)  
        if not(operationStatus == 0):
            raise RuntimeError("Some error: " + str(operationStatus))
    else:
        setRegisterValueAsDouble = dll.rcSetRegFromDouble2

        # Specify argument and return types for the DLL function
        setRegisterValueAsDouble.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
        setRegisterValueAsDouble.restype = ctypes.c_int

        # Sets up the device name and ID 
        deviceNameIdBuf = create_string_buffer(128)
        deviceNameIdBuf.value = (deviceNameId).encode()
        
        # Sets up the register name 
        registerNameBuf = create_string_buffer(128)
        registerNameBuf.value = registerName.encode()

        #  Check the operationStatus status, return one of  RMTCTRLERR_xxx  list
        operationStatus = setRegisterValueAsDouble(connectionHandle, deviceNameIdBuf, registerNameBuf, value) 
        
        if not(operationStatus == 0):
            raise RuntimeError("Some error: " + str(operationStatus)) 
    return   

# Saves and set a value to a device register.
def NV_write_register(deviceNameId ='', registerName='', value=700):
    if type(value) is str:
        # Use the DLL function to set the register value as a string
        setRegisterNVFromString = dll.rcSetRegNVFromString2

        # Specify argument and return types for the DLL function
        setRegisterNVFromString.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        setRegisterNVFromString.restype = ctypes.c_int

        # Prepare buffers for device name and register name
        deviceNameIdBuf = create_string_buffer(128)
        deviceNameIdBuf.value = deviceNameId.encode()

        registerNameBuf = create_string_buffer(128)
        registerNameBuf.value = registerName.encode()

        # Prepare the value buffer
        valueBuffer = create_string_buffer(512)
        valueBuffer.value = value.encode()

        # Call the DLL function
        operationStatust = setRegisterNVFromString(connectionHandle, deviceNameIdBuf, registerNameBuf, valueBuffer)
        if operationStatust != 0:
            raise RuntimeError(f"Failed to write string value to register '{registerName}'. Error code: {operationStatust}")

    else:
        # Use the DLL function to set the register value as a double
        setRegisterNVFromDouble = dll.rcSetRegNVFromDouble2
        setRegisterNVFromDouble.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
        setRegisterNVFromDouble.restype = ctypes.c_int

        # Prepare buffers for device name and register name
        deviceNameIdBuf = create_string_buffer(128)
        deviceNameIdBuf.value = deviceNameId.encode()

        registerNameBuf = create_string_buffer(128)
        registerNameBuf.value = registerName.encode()

        # Call the DLL function
        operationStatust = setRegisterNVFromDouble(connectionHandle, deviceNameIdBuf, registerNameBuf, float(value))
        if operationStatust != 0:
            raise RuntimeError(f"Failed to write double value to register '{registerName}'. Error code: {operationStatust}")
    return






# From the INI file
# [Product]
# Name=Laser
# [StartStopControl]
# MasterModule=NL30x:8
# StartStopRegister=State
# StartValue=ON
# StopValue=STOP

def StartLaser():
    write_register(deviceNameId="NL30x:8", registerName="State", value="ON")
    return

def StopLaser():
    write_register(deviceNameId="NL30x:8", registerName="State", value="STOP")
    return

# From the INI file
# [OutputControl]
# OutputControlEnable=1
# OutputControlModule=NL30x:8
# OutputControlRegister=Output level

# Take value from remotecontrol.csv 'NL030x' device, and register name 'Output level'
#NL30x   ;$8;$11;$1;u8;AUS;NV;0;2;Energy;[OFF,Adjustment,Max];Output level;OFF
#  In that case possible values are: OFF, Adjustment, Max

def SetEnergyLevel(energyLevel):
    write_register(deviceNameId="NL30x:8", registerName="Output level", value=energyLevel)
    return

# From the INI file
# [BatchControl]
# BatchControlEnable=1
# BatchControlModule=NL30x:8
# BatchControlRegister=Continuous / Burst mode / Trigger burst

# Take value from remotecontrol.csv 'NL030x' device, and register name 'Continuous / Burst mode / Trigger burst'
# NL30x   ;$8;$18;$1;u8;AS;;0;2;BatchM;[Continuous,Burst,Trigger];Continuous / Burst mode / Trigger burst;Continuous

def SetBatchMode(batchMode):
    write_register(deviceNameId="NL30x:8", registerName="Continuous / Burst mode / Trigger burst", value=batchMode)
    return

# From the INI file
# [EditList]
# S1=Master:20;WaveLength;WaveLength
# S2=Master:20;Configuration;Configuration

# Take value from remotecontrol.csv 'Master' device, and register name 'WaveLength'
# Master  ;$14;$10;$0;float;AUS;NV;2;1320;Wl;%.7gnm;WaveLength;840.4

# Posiible values are: [2;1300]
def setWaveLength(wavelengths):
    write_register(deviceNameId="Master:20", registerName="WaveLength", value=wavelengths)
    return

# Take value from remotecontrol.csv 'Master' device, and register name 'Configuration'
# Master  ;$14;$13;$3;u8;AUS;NV;0;4;Conf;[OUT1A,OUT1B,OUT1C,OUT1D,DETIIH];Configuration;OUT1A

# Posiible values are: [OUT1A, OUT1B, OUT1C, OUT1D, DETIIH]
def SetConfiguration(configuration):
    write_register(deviceNameId="Master:20", registerName="Configuration", value=configuration)
    return

# From the INI file
# [PollList]
# S1=Master:20;WaveLength;WaveLength
# S2=Master:20;Configuration;Configuration
# S3=Master:20;PG Status;PG Status

# Take value from remotecontrol.csv 'Master' device, and register name 'WaveLength'
# Master  ;$14;$10;$0;float;AUS;NV;2;1320;Wl;%.7gnm;WaveLength;840.4

def readWaveLength():
    return read_register(deviceNameId = 'Master:20',registerName='WaveLength')

# Take value from remotecontrol.csv 'Master' device, and register name 'Configuration'
# Master  ;$14;$13;$3;u8;AUS;NV;0;4;Conf;[OUT1A,OUT1B,OUT1C,OUT1D,DETIIH];Configuration;OUT1A

def readConfiguration():
    return read_register(deviceNameId = 'Master:20',registerName="Configuration")

# Take value from remotecontrol.csv 'Master' device, and register name 'PG Status'
# Master  ;$14;$11;$3;u8;AUS;;0;6;PG_Stat;[Off,Init,Tuning...,Ok,Scanning...,Fault,No Connection];PG Status;Ok

def readPGStatus():
    return read_register(deviceNameId = 'Master:20',registerName='PG Status')


# Set and save register Value
# Avoid to use ....

def SetNVWavelength(wavelength):
        NV_write_register(deviceNameId="Master:20", registerName="WaveLength", value=wavelength)
        return

def SetNVEnergyLevel(energyLevel):
        NV_write_register(deviceNameId="NL30x:8", registerName="Output level", value=energyLevel)
        return

# Connect to the device via the DLL
t = time.time()
#   connectiontype: 0 - direct USB or "gray box"
#                   1 - RS232
#                   2 - TCP/IP
#                   3 - simulate I/O
connectionType = 2

# (deviceAddressBuff)   hwdevice:
#                       in case connectiontype==0 (USB), serial number of USB chip like FT123456
#                       in case connectiontype==1, com port name like "COM1", "COM2", etc
#                       in case connectiontype==2, IP address or (DHCP) host name

deviceAddressBuff = create_string_buffer(13)
deviceAddressBuff.value = b"192.168.0.108"

# Load the DLL and set up the function
int_p = ctypes.POINTER(ctypes.c_int)


dll_path = os.path.join(os.path.dirname(__file__), "REMOTECONTROL64.dll")
dll = ctypes.CDLL(dll_path)
connectDevice = dll.rcConnect2

# Specify argument and return types for the DLL function
connectDevice.argtypes = [int_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
connectDevice.restype = ctypes.c_int

connectionHandle = ctypes.c_int(0)

#  (iniFilePathBuffer) inipath:
#               CSV file name, including or not including full path.
#               In case inipath==NULL, or inipath=="", default REMOTECONTROL.CSV is used.
#               inipath is ignored connecting over TCP/IP. Server uses its own REMOTECONTROL.CSV

iniFilePathBuffer = create_string_buffer(128)
# Since the iniFilePathBuffer is not used in this example (TCP/IP connection), we can leave it empty.
iniFilePathBuffer.value = b''

# Call the DLL function to connect to the device
connectionStatus = connectDevice(ctypes.byref(connectionHandle), connectionType, deviceAddressBuff, iniFilePathBuffer)

# Check the connection status, return one of  RMTCTRLERR_xxx  list
if not(connectionStatus == 0):
    raise RuntimeError("Some error: " + str(connectionStatus))
            
cnn_time = time.time() - t

print("Connection time ", cnn_time, "Connection Status", connectionStatus)


# Demo calls to the demo functions

# Start the laser
StartLaser()
time.sleep(5)  

# Stop the laser
StopLaser()
time.sleep(5)  

# Set energy level
SetEnergyLevel("Max")

# Set batch mode
SetBatchMode("Burst")

# Set and read wavelength
setWaveLength(850.5)
print('Wavelength', readWaveLength())


# Set and read configuration
SetConfiguration("OUT1B")
print("Configuration", readConfiguration())


# Read PG status
print(f"Current PG status:", readPGStatus())


# Demo: Set and save NV values
SetNVWavelength(860.2)
SetNVEnergyLevel("Adjustment")
