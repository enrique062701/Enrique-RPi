"""
This is a python file for BNC box for 8 different channels. This is the long way.
"""
import epics
import time
import socket
import sys
from decimal import Decimal, getcontext

# This section is for getting the macros from the st.cmd file

###
USER = "BNC1:"

channels = ['1', '2', '3', '4', '5', '6', '7', '8']

n1 = 0.0
n2 = 0.02
n3 = 0.1 # This is for chaning the mode of the channels and the box. This will also be for turning on and off the channels.

Delay_ch = {}
Delay_RBV_ch = {}
Source_ch = {}
Source_RBV_ch = {}
ChannelState_ch = {}
ChannelState_RBV_ch = {}
Width_ch = {}
Width_RBV_ch = {}
Mode_ch = {}
Mode_RBV_ch = {}
print("Initiating channels...")

for channel in channels:
    Delay_ch[channel] = epics.PV(f"{USER}Ch{channel}:Delay")
    Delay_RBV_ch[channel] = epics.PV(f"{USER}Ch{channel}:Delay_RBV")
    Source_ch[channel] = epics.PV(f"{USER}Ch{channel}:Source")
    Source_RBV_ch[channel] = epics.PV(f"{USER}Ch{channel}:Source_RBV")
    ChannelState_ch[channel] = epics.PV(f"{USER}Ch{channel}:ChannelState") #Turning on or off channels
    ChannelState_RBV_ch[channel] = epics.PV(f"{USER}Ch{channel}:ChannelState_RBV")
    Width_ch[channel] = epics.PV(f"{USER}Ch{channel}:Width")
    Width_RBV_ch[channel] = epics.PV(f"{USER}Ch{channel}:Width_RBV")
    Mode_ch[channel] = epics.PV(f"{USER}Ch{channel}:Mode")
    Mode_RBV_ch[channel] = epics.PV(f"{USER}Ch{channel}:Mode_RBV")

    Delay_ch[channel].connect(timeout = 5)
    Delay_RBV_ch[channel].connect(timeout = 5)
    Source_ch[channel].connect(timeout = 5)
    Source_RBV_ch[channel].connect(timeout = 5)
    ChannelState_ch[channel].connect(timeout = 5)
    ChannelState_RBV_ch[channel].connect(timeout = 5)
    Width_ch[channel].connect(timeout = 5)
    Width_RBV_ch[channel].connect(timeout = 5)
    Mode_ch[channel].connect(timeout = 5)
    Mode_RBV_ch[channel].connect(timeout = 5)
    print(f"Channel {channel} done initializing.")

# Now initializing the leftover PVs, one per device only
TriggerMode = epics.PV(f"{USER}TriggerMode")
TriggerMode_RBV = epics.PV(f"{USER}TriggerMode_RBV")
Run = epics.PV(f"{USER}Run")
Run_RBV = epics.PV(f"{USER}Run_RBV")
Auto = epics.PV(f"{USER}Auto")
Auto_RBV = epics.PV(f"{USER}Auto_RBV")
Update = epics.PV(f"{USER}Update")
Period = epics.PV(f"{USER}Period")
Period_RBV = epics.PV(f"{USER}Period_RBV")
Mode = epics.PV(f"{USER}Mode")
Mode_RBV = epics.PV(f"{USER}Mode_RBV")

TriggerMode.connect(timeout = 5)
TriggerMode_RBV.connect(timeout = 5)
Run.connect(timeout = 5)
Run_RBV.connect(timeout = 5)
Auto.connect(timeout = 5)
Auto_RBV.connect(timeout = 5)
Update.connect(timeout = 5)
Period.connect(timeout = 5)
Period_RBV.connect(timeout = 5)
Mode.connect(timeout = 5)
Mode_RBV.connect(timeout = 5)


print('Done initializing remaining channels.')

BNC_IP = "10.97.106.100" #"10.97.106.97"
BNC_Port = 4001 #2101

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(2)
try:
    client_socket.connect((BNC_IP, BNC_Port))
except socket.error as e:
    print(f"Failed to connect: {e}")
    client_socket = None

print("Connected to device, ready to start")

################################################################################################################
# Next is to start writing the functions.
def write_pv(pv, value):
    try:
        if pv.connected:
            pv.put(value, wait = True, timeout = 0.05)
        else:
            print(f"Failed to connect to {pv.pvname}")
    except:
        print(f'PV Error on {pv.pvname}')

################################################################################################################
def on_pv_change_width_Ch1(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
      
        value_str = str(value)
        message = f":PULSE1:WIDTH {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE1:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['1'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch1(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE1:DELAY {value_str}\r\n"
        print("Sending message: ", message)
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE1:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['1'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch1(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE1:SYNC {value}\r\n'
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)
        

        # Check the RBV to confirm
        message = ":PULSE1:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['1'], source)

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch1(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        #value_str = str(value)
        print(value_str)
        message = f":PULSE1:STATE {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE1:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['1'], int(state))

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch1(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE1:CMODE {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE1:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['1'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch2(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE2:WIDTH {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE2:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['2'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################    

def on_pv_change_delay_Ch2(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE2:DELAY {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE2:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['2'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch2(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE2:SYNC {value}\r\n'
        client_socket.send(message.encode())
        print(f"Message sent: {message}")
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE2:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['2'], source)

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch2(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE2:STATE {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE2:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['2'], int(state))

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch2(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE2:CMODE {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE2:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['2'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch3(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE3:WIDTH {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE3:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['3'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch3(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE3:DELAY {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE3:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['3'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch3(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE3:SYNC {value}\r\n'
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE3:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['3'], source)

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch3(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE3:STATE {value_str}\r\n"
        print(f"Message sent: {message}")
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE3:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['3'], int(state))

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")
  
################################################################################################################

def on_pv_change_mode_Ch3(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle    
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE3:CMODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE3:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['3'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch4(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE4:WIDTH {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE4:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['4'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch4(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE4:DELAY {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE4:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['4'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch4(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE4:SYNC {value}\r\n'
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE4:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['4'], int(source))

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch4(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE4:STATE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE4:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['4'], state)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch4(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE4:CMODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n3)

        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE4:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['4'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch5(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE5:WIDTH {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE5:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['5'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch5(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE5:DELAY {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE5:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['5'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch5(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE5:SYNC {value}\r\n'
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE5:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['5'], int(source))

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch5(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE5:STATE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE5:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['5'], state)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch5(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE5:CMODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE5:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['5'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch6(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE6:WIDTH {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE6:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['6'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch6(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE6:DELAY {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE6:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['6'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch6(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE6:SYNC {value}\r\n'
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE6:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['6'], int(source))

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch6(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value ==  1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE6:STATE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE6:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['6'], state)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch6(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE6:CMODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE6:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['6'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch7(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE7:WIDTH {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE7:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['7'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch7(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE7:DELAY {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE7:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['7'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch7(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE7:SYNC {value}\r\n'
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE7:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['7'], int(source))

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch7(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel.
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE7:STATE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE7:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['7'], state)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch7(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE7:CMODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE7:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['7'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
def on_pv_change_width_Ch8(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE8:WIDTH {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming with RBV
        message_rbv = ":PULSE8:WIDTH?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        width = client_socket.recv(2048).decode().strip()
        print("Width: ", width)
        write_pv(Width_RBV_ch['8'], width)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_delay_Ch8(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE8:DELAY {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Confirming the RBV
        message_rbv = ":PULSE8:DELAY?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        delay = client_socket.recv(2048).decode().strip()
        print('Delay: ', delay)
        write_pv(Delay_RBV_ch['8'], delay)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")
    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_source_Ch8(pvname = None, value = None, char_value = None, **kwargs):
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing values {value}")

    try:
        value_str = str(value)
        message = f':PULSE8:SYNC {value}\r\n'
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE8:SYNC?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        source = client_socket.recv(2048).decode().strip()
        print(f"Source: {source}")
        write_pv(Source_RBV_ch['8'], int(source))

    except socket.error as e:
        print(f"Socket error during communication")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"PV {pvname} changed to {value} ({char_value})")

################################################################################################################

def on_pv_change_state_Ch8(pvname = None, value = None, char_value = None, **kwargs):
    """
    Turns on or off the channel. 
    PULSE8:STATE ON --> Turns channel on
    PULSE8:STATE OFF --> Turns channel off
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"
        print(value_str)
        message = f":PULSE8:STATE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Check the RBV to confirm
        message = ":PULSE8:STATE?\r\n"
        client_socket.send(message.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(ChannelState_RBV_ch['8'], state)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_mode_Ch8(pvname = None, value = None, char_value = None, **kwargs):
    """
    Sets the channel to continuous, single, etc. Use command :CMODE
    Possible entries:
        NORMal
        SINGle
        BURSt
        DCYCle
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value: {value}")
    try:
        value_str = str(value)
        message = f":PULSE8:CMODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n3)
        client_socket.recv(2048)

        # Confirming with the RBV
        message_rbv = f":PULSE8:CMODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        mode = client_socket.recv(2048).decode().strip()
        print("Mode: ", mode)
        write_pv(Mode_RBV_ch['8'], mode)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
################################################################################################################
# Now to do the remaining commands that control the entire box instead of individual channels
def on_pv_change_trigger(pvname = None, value = None, char_value = None, **kwargs):
    """
    This command will change it from external to internal trigger and vice versa.
    PULSE0:TRIG:MODE DIS --> disables external trigger --> Internal Trigger
    PULSE0:TRIG:MODE TRIG --> Enables external trigger.
    """
    global client_socket
    if client_socket is None:

        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Write values {value}")
    try:
        value_str = str(value)
        message = f":PULSE0:TRIG:MODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Checking RBV
        message_rbv = f":PULSE0:TRIG:MODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        trigger = client_socket.recv(2048).decode().strip()
        print(f"Trigger Mode: {trigger}")
        write_pv(TriggerMode_RBV, trigger)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################

def on_pv_change_run(pvname = None, value = None, char_value = None, **kwargs):
    """
    This command turns on or off the the BNC. It is similar to running RUN/STOP:
        0/1 --> OFF/ONN:   0 is off and 1 is on
    We want to make it so that after pressing run, it goes back to 0. Need to do this without creating an infinite loop.
    We just want to turn off the button. So we click button, then turns off but machine is still runnin. We click button 
    again and the machine will stop running.

    NOTE: TRIGGER MUST BE ON EXTERNAL AND ENABLED OR ELSE IT WILL NOT WORK
    """   
    global client_socket
    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return

    print(f"Connected to {pvname}. Write values {value}")
    if value == 0:
        value_str = "OFF"
    elif value == 1:
        value_str = "ON"

    try:
        #value_str = str(value)
        print(f"This is 'value_str': {value_str}")
        message = f":PULSE0:STATE {value_str}\r\n"
        print(message)
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Checking RBV
        message_rbv = f":PULSE0:STATE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        state = client_socket.recv(2048).decode().strip()
        print(f"State: {state}")
        write_pv(Run_RBV, state)

    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")

################################################################################################################
def on_pv_change_update(pvname = None, value = None, char_value = None, **kwargs):
    """
    Command to update the screen:
    :PULSE:UPDate? --> Updates the LED screen with values sent.
    Manual states must be used when mode is false.
    """
    global client_socket
    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Write values {value}")

    try:
        value_str = str(value)
        message = f":DISPLAY:UPDate?"
        client_socket.send(message.encode())
        time.sleep(n2)
        response = client_socket.recv(2048).decode().strip()
        if response != "ok":
            raise KeyError("Display did not change try again")
            return
        
        print(f"Response: {response}")
        write_pv() #Update with the proper PV
    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occured: {e}")


################################################################################################################
def on_pv_change_auto(pvname = None, value = None, char_value = None, **kwargs):
    """
    This command will turn on or off the automatic screen updates. If automatic speed updates is on
    the program will not be able to sned and proccess commands in 0.03s. It has to be at minumum 0.05s
    If the autodisplay is off then the device can process commands at 0.03s. So:

        auto_update = ON ---> time.sleep(0.05)
        auto_update = OFF ---> time.sleep(0.03)
    """
    global client_socket

    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value {value}")
    
    try:
        value_str = str(value)
        message = f":DISPLAY:MODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048) # Clear buffer

        # Checking the RBV value
        message_rbv = ":DISPLAY:MODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        rbv = client_socket.recv(2048).decode().strip()
        print("The auto update is: ", rbv)
        write_pv()
    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
def on_pv_change_period(pvname = None, value = None, char_value = None, **kwargs):
    """
    This function changes the period at which the box triggers at. Ranges from 100ns to 5000s.
    :PULSE0:PERIOD {value} --> Send the value
    :PULSE0:PERIOD? --> Returns the RBV for the period
    """
    global client_socket
    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socket reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value {value}")

    try:
        value_str = str(value)
        message = f":PULSE0:PERIOD {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Checking for the RBV 
        message_rbv = ":PULSE0:PERIOD?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        rbv = client_socket.recv(2048).decode().strip()
        print("The Period is now: ", rbv)
        write_pv(Period_RBV, rbv)
    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
def on_pv_change_mode(pvname = None, value = None, char_value = None, **kwargs):
    """
    This function will change the mode of the entire scope:
        :PULSE0:MODE {value} --> Possible values: Normal , Single, Burst, Dcycle
        :PULSE0:MODE? --> Returns the readback value 
    """
    global client_socket
    if client_socket is None:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((BNC_IP, BNC_Port))
        except socket.error as e:
            print(f"Socekt reconnection failed: {e}")
            return
    print(f"Connected to {pvname}. Writing value {value}")

    try:
        value_str = str(value)
        message = f":PULSE0:MODE {value_str}\r\n"
        client_socket.send(message.encode())
        time.sleep(n1)
        client_socket.recv(2048)

        # Checking for RBV
        message_rbv = ":PULSE0:MODE?\r\n"
        client_socket.send(message_rbv.encode())
        time.sleep(n2)
        rbv = client_socket.recv(2048).decode().strip()
        print(f"The mode now is: ", rbv)
        write_pv(Mode_RBV, rbv)
    except socket.error as e:
        print(f"Socket error during communication: {e}")
        client_socket.close()
        client_socket = None
    except Exception as e:
        print(f"An error occurred: {e}")


################################################################################################################
# The next step initialize the PVs.
for channel in channels:
    write_pv(Delay_ch[channel], 0)
    write_pv(Delay_RBV_ch[channel], 0)
    write_pv(Source_ch[channel], "T0")
    write_pv(Source_RBV_ch[channel], "T0")
    write_pv(ChannelState_ch[channel], 0)
    write_pv(ChannelState_RBV_ch[channel], 0)
    write_pv(Width_ch[channel], 0)
    write_pv(Width_RBV_ch[channel], 0)
    write_pv(Mode_ch[channel], "NORMAL")
    write_pv(Mode_RBV_ch[channel], "NORMAL")
    print(f"Finished initializing channel {channel}.")
print(f"Finished inilializing individual channels")

# Now adding callbacks to each function
Delay_ch['1'].add_callback(on_pv_change_delay_Ch1)
Source_ch['1'].add_callback(on_pv_change_source_Ch1)
ChannelState_ch['1'].add_callback(on_pv_change_state_Ch1)
Width_ch['1'].add_callback(on_pv_change_width_Ch1)
Mode_ch['1'].add_callback(on_pv_change_mode_Ch1)


Delay_ch['2'].add_callback(on_pv_change_delay_Ch2)
Source_ch['2'].add_callback(on_pv_change_source_Ch2)
ChannelState_ch['2'].add_callback(on_pv_change_state_Ch2)
Width_ch['2'].add_callback(on_pv_change_width_Ch2)
Mode_ch['2'].add_callback(on_pv_change_mode_Ch2)


Delay_ch['3'].add_callback(on_pv_change_delay_Ch3)
Source_ch['3'].add_callback(on_pv_change_source_Ch3)
ChannelState_ch['3'].add_callback(on_pv_change_state_Ch3)
Width_ch['3'].add_callback(on_pv_change_width_Ch3)
Mode_ch['3'].add_callback(on_pv_change_mode_Ch3)


Delay_ch['4'].add_callback(on_pv_change_delay_Ch4)
Source_ch['4'].add_callback(on_pv_change_source_Ch4)
ChannelState_ch['4'].add_callback(on_pv_change_state_Ch4)
Width_ch['4'].add_callback(on_pv_change_width_Ch4)
Mode_ch['4'].add_callback(on_pv_change_mode_Ch4)


Delay_ch['5'].add_callback(on_pv_change_delay_Ch5)
Source_ch['5'].add_callback(on_pv_change_source_Ch5)
ChannelState_ch['5'].add_callback(on_pv_change_state_Ch5)
Width_ch['5'].add_callback(on_pv_change_width_Ch5)
Mode_ch['5'].add_callback(on_pv_change_mode_Ch5)


Delay_ch['6'].add_callback(on_pv_change_delay_Ch6)
Source_ch['6'].add_callback(on_pv_change_source_Ch6)
ChannelState_ch['6'].add_callback(on_pv_change_state_Ch6)
Width_ch['6'].add_callback(on_pv_change_width_Ch6)
Mode_ch['6'].add_callback(on_pv_change_mode_Ch6)


Delay_ch['7'].add_callback(on_pv_change_delay_Ch7)
Source_ch['7'].add_callback(on_pv_change_source_Ch7)
ChannelState_ch['7'].add_callback(on_pv_change_state_Ch7)
Width_ch['7'].add_callback(on_pv_change_width_Ch7)
Mode_ch['7'].add_callback(on_pv_change_mode_Ch7)


Delay_ch['8'].add_callback(on_pv_change_delay_Ch8)
Source_ch['8'].add_callback(on_pv_change_source_Ch8)
ChannelState_ch['8'].add_callback(on_pv_change_state_Ch8)
Width_ch['8'].add_callback(on_pv_change_width_Ch8)
Mode_ch['8'].add_callback(on_pv_change_mode_Ch8)


# Initializing and adding callbacks for the other functions
write_pv(TriggerMode, 0)
write_pv(TriggerMode_RBV, 0)
write_pv(Run, "OFF")
write_pv(Run_RBV, "OFF")
write_pv(Auto, 0)
write_pv(Auto_RBV, 0)
write_pv(Mode, "NORM")
write_pv(Mode_RBV, "NORM")
write_pv(Period, 1.00)
write_pv(Period_RBV, 1.00)
#write_pv(Update, "ON")

# Adding callbacks to these functions
TriggerMode.add_callback(on_pv_change_trigger)
Run.add_callback(on_pv_change_run)
Auto.add_callback(on_pv_change_auto)
Mode.add_callback(on_pv_change_mode)
Period.add_callback(on_pv_change_period)
#Update.add_callback(on_pv_change_update)

getcontext().prec = 20 # Set precision high enough to handle nanosecond additions


print("SCRIPT IS DONE, READY TO CONTROL DEVICE.")
### The END ###
#NEED TO ADD LONGER WAIT TIME WHEN SWITCHING BETWEEN MODES

# Now to keep the script running forever
while True:
    try:
        # In order to make the calback function return to zero each time, can do the following
        button = epics.caget(f"{USER}Button")
        if button == 1: # User presses button so it turns on
            print("Button activated")

            message_mode = ":PULSE0:MODE?\r\n"
            client_socket.send(message_mode.encode())
            time.sleep(n1)
            response_mode = client_socket.recv(2048).decode().strip()
            if response_mode == "SING":
                # Do not need to query the state of the bnc bc it will always be OFF since it is in single mode
                # If it does not work, will just send the commands directly without updating EPICS variables.
                epics.caput(f"{USER}Run", "1") # Turn it on
                time.sleep(n2) 
                epics.caput(f"{USER}Run", "0") # You send the zero to update the epics PV variable.

            elif response_mode == "NORM":
                message = ":PULSE0:STATE?\r\n"
                client_socket.send(message.encode()) # Checks whether the machine is running or not
                time.sleep(n2)
                response = client_socket.recv(2048).decode().strip()
                time.sleep(n2)

                print(f"Message recieved: {response}")

                if response == "1":
                    epics.caput(f"{USER}Run", "0") # If the BNC is running it will turn it off
                    print("Turning off the BNC")

                elif response == "0":
                    epics.caput(f"{USER}Run", "1")
                    print("Turning on the BNC")

            epics.caput(f"{USER}Button", 0) # Sets it back to zero
            time.sleep(0.5)

        epics.ca.poll()
        time.sleep(0.01)
    except KeyboardInterrupt:
        break




