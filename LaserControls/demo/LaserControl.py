"""
This python file is to try and communicate with the Green laser using the RS232 to USB adapter provided by
EKSPLA. The usb is connected to the rasperry pi.
- Enrique Cisneros 07/30/25
"""
import numpy as np 
import time
from ctypes import *
import os

  
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

##################################################################################################################################################################
# Now inputting the functions that will communicate with the laser.

def StartLaser():
    write_register(deviceNameId = "NL30x:8", registerName = "State", value = "ON")
    return


def StopLaser():
    write_register(deviceNameId = "NL30x:8", registerName = "State", value = "STOP")
    return


def SetEnergyLevel(energylevel):
    write_register(deviceNameId = "NL30x:8", registerName = "Output level", value = energylevel)
    return


def SetBatchMode(batchMode):
    write_register(deviceNameId = "NL30x:8", registerName = "Continuous / Burst mode / Trigger burst", value = batchMode)
    return


def setWaveLength(wavelength):
    write_register(deviceNameId = "Master:20", registerName = "WaveLength", value = wavelength)
    return


def SetConfiguration(configuration):
    write_register(deviceNameId = "Maser:20", registerName = "Configuration", value = configuration)
    return


def readWaveLength():
    return read_register(deviceNameId = 'Master:20', registerName = 'WaveLength')


def readConfiguration():
    return read_register(deviceNameId = 'Master:20', registerName = "Configuration")


def readPGStatus():
    return read_register(deviceNameId = 'Master:20', registerName = 'PG Status')


def SetNVWavelength(wavelength):
    NV_write_register(deviceNameId = "Master:20", registerName = "WaveLength", value = wavelength)
    return


def SetNVEnergyLevel(energyLevel):
    NV_write_register(deviceNameId = "NL30x:8", registerName = "Output level", value = energyLevel)
    return

##################################################################################################################################################################
# Now to handle the connection type
# We will be connecting through the USB using com1 that has been mapped in wine.
t = time.time()
connectionType = 0 # This is through the usb that was given: USB to RS232
USB_serial = "FT7D0TLO"

int_p = ctypes.POINTER(ctypes.c_int)


dll_path = os.path.join(os.path.dirname(__file__), "REMOTECONTROL64.dll")
dll = ctypes.POINTER(ctypes.c_int)
connectDevice = dll.rcConnect2

#Specify argument and return types for the DLL function
connectDevice.argtypes = [int_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
connectDevice.restype = ctypes.c_int(0)

# Now naming the path of the CSV file
iniFilePathBuffer = create_string_buffer(128)

iniFilePathBuffer.value = b''

#Calling funtion to connect to the device
#connectionStatus = connectDevice(ctypes.byref(connectionHandle), connectionType, deviceAddressBuff, iniFilePathBuffer)
connectionStatus = connectDevice(ctypes.byref(connectionHandle), connectionType, USB_serial, iniFilePathBuffer)
# Check the connection status, return one of RMTCTRLERR_xxx list
if not(connectionStatus == 0):
    raise RuntimeError("Some error: " + str(connectionStatus))

cnn_time = time.time() - t

print("Connection time", cnn_time, "Connection Status", connectionStatus)

# Now to test the laser
print("Test 1")

print(f"The wavelength is: {readWaveLength()}")






