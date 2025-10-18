"""
This python script will be an OO script that can be used for any BMC timing box, converting Jacksons TimingBoxBNC4.py to work
for an n amount of channels, preventing thousands of lines of code. This will by pass the need form multiple longs python scripts. 
Can just define each box in one script.
NOTE: Looking at the command syntax it goes as PULSE0:MODE SING and PULSE0: STATE ON. The reason for this might be because these
commands reflect all channels. So the trigger type and the state should not be in the channels section because they are independent
of channels.
PULSE == PULSE0 == T_0 --> Affects the whole instrument / every channel that is active. 

Author: Enrique C.
"""
import socket
import time
import epics
import sys

class TimingBoxBNC:

    def __init__(self, USER, IP_addr:str, port_number: int, verbose = True):
        # All of these will now be set automatically when instantiated 
        #self.get_macros()
        #self.setup_channels(self.number_of_channels)
        
        self.USER = USER
        self.verbose = verbose
        self.IP_addr = IP_addr
        self.port_number = port_number
        self.client_socket = None
        # Different limitations.
        self.n1 = 0.00 
        self.n2 = 0.02
        self.MAX_ = 999.99999999975
        self.MIN_ = 1e-9


#########################################################################################################################################

    def get_macros(self):
        """
        This function will parse the st.cmd file and fill in the macros from it. That way you dont
        have to keep creating new files for each new device. It is a generic one.
        NOTE: Must name the macros as named here in the st.cmd file or else it will not recognize it.
        """
        macros = {}

        for arg in sys.argv[1:]:
            if '=' in sys.arg:
                key, val = arg.split('=', 1)
                macros[key] = val
        
        required_macros = ["P", "IP_addr", "port_number", "number_of_channels"]
        
        for macro in required_macros:
            if macro not in macros.keys():
                raise ValueError(f"Required Macro missing: {macro}")
            else:
                self.USER = macros["P"]
                self.IP_addr = macros["IP_addr"]
                self.port_number = int(macros["port_number"])
                self.number_of_channels = int(macros["number_of_channels"])
        
#########################################################################################################################################
    
    def connect_device(self, IP_addr: str, port_number: int):
        """
        Uses socket communication to connect to device.
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect(self.IP_addr, self.port_number)
        except socket.error as e:
            if self.verbose: print(f"Initial socket connection failed: {e}")
            self.client_socket = None
        if self.verbose: print("Connected to devices. Ready to send commands.")


#########################################################################################################################################
    def write_pv(self, pv, value):
        try:
            if pv.connected:
                pv.put(value, wait = True, timeout = 0.05)
            else:
                if self.verbose: print(f'Failed to connect to {pv.pvname}.')
        except:
            if self.verbose: print(f"PV Error on {pv.pvname}: {e}")


#########################################################################################################################################
    
    def get_channels(self, number_of_channels: int) -> dict:
        """
        Helper function that converts the number of channels to a list of all the channels available.
        Returns:
        {'A': 1, 'B': 2, 'C': 3, ....}
        If for some reason you need more channels, add them to where it says letters.
        """
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.channels = {
            letters[i]: i+1 for i in range(number_of_channels)
        }
        return self.channels

#########################################################################################################################################

    def setup_channels(self, number_of_channels: int):
        """
        Setup PVs and callbacks for each channel. If you wish to add more commands or PVs, add them to the 
        respective dictionary. Also create a new dictionary where you wish to store the values.
        An example of what the empty dictionaries have that are intialized are:
            self.Delay_desired_ch = {
                "A" : epics.PV(BNC1:chA:DelayDesired)
                .       .
                .       .
                .       .
            }
        So later down the script, when writing a value to a PV, you write:
            self.write_pv(self.delay_desired_ch['A'], value) 
            - This lets you write a value to the object inside the dictionary, which corresponds to a PV variable.
        """
        # Build channel map (e.g. {"A":1, "B":2, ...})
        channels_map = self.get_channels(number_of_channels)

        # Initialize dictionaries for PV storage
        self.Delay_ch = {} 
        self.Delay_RBV_ch = {}
        self.Width_ch = {}
        self.Width_RBV_ch = {}
        self.Source_ch = {}
        self.Source_RBV_ch = {}
        self.Mode_ch = {}
        self.Mode_RBV_ch = {}
        self.ChannelState_ch = {}
        self.ChannelState_RBV_ch = {}

        # Desired PVs and their callbacks
        pv_types = {
            "Delay": self.on_pv_change_delay,
            "Width": self.on_pv_change_width,
            "Source": self.on_pv_change_source,
            "Mode": self.on_pv_change_mode, 
            "ChannelState": self.on_pv_change_state,
        }

        # Mapping from Desired PVs to their readbacks
        readback_map = {
            "Delay": "Delay_RBV",
            "Width": "Width_RBV",
            "Source": "Source_RBV",
            "Mode": "Mode_RBV",
            "ChannelState": "ChannelState_RBV",
        }

        # Mapping Desired PV names to attribute dictionaries
        pv_attr_map = {
            "Delay": "Delay_ch",
            "Width": "Width_ch",
            "Source": "Source_ch",
            "Mode": "Mode_ch",
            "ChannelState": "ChannelState_ch",
        }

        # Loop through channels and create PVs
        for ch_letter, ch_num in channels_map.items():
            for pv_name, callback in pv_types.items():
                if self.verbose: print(f"Doing {pv_name} with callback {callback}") #For sanity check to see if its working
                dict_name = pv_attr_map[pv_name]
                pv_dict = getattr(self, dict_name)

                # Connects to desired PV using the Dictionary mapping and connects callback function
                pv_dict[ch_letter] = epics.PV(f"{self.USER}Ch{ch_num}:{pv_name}")
                pv_dict[ch_letter].connect(timeout=5)
                pv_dict[ch_letter].add_callback(
                    lambda pvname = None, value = None, char_value = None,
                        ch_letter = ch_letter, ch_num = ch_num, callback = callback, **kwargs:
                        callback(ch_num, ch_letter, pvname, value, char_value, **kwargs))

                # Maps the readback values.
                rbv_name = readback_map[pv_name]              
                rbv_dict_name = f"{rbv_name}_ch"             
                rbv_dict = getattr(self, rbv_dict_name)

                rbv_dict[ch_letter] = epics.PV(f"{self.USER}Ch{ch_num}:{rbv_name}")
                rbv_dict[ch_letter].connect(timeout=5)
                if self.verbose: print(f"PV {pv_name} and callback {callback} has been done.") # For sanity check to see if its working

            if self.verbose:
                print(f"Channel {ch_num} ({ch_letter}) setup complete.")

    
        # This is for the functions that are one per device
        self.Mode = {}
        self.Mode_RBV = {}
        self.TriggerMode = {}
        self.TriggerMode_RBV = {}
        self.Run = {}
        self.Run_RBV = {}
        self.Period = {}
        self.Period_RBV = {}
        self.update = {}
        self.Auto = {}
        self.Auto_RBV = {}

        pv_types_device = {
            "Mode" : self.on_pv_change_mode_device,
            "TriggerMode" : self.on_pv_change_trigger,
            "Run" : self.on_pv_change_run,
            "Period" : self.on_pv_change_period,
            #"Update" : self.on_pv_change_update,
            "Auto" : self.on_pv_change_auto,
        }

        readback_device = {
            "Mode" : "Mode_RBV",
            "TriggerMode" : "TriggerMode_RBV",
            "Run" : "Run_RBV",
            "Period" : "Period_RBV",
            "Auto" : "Auto_RBV",
        }
        
        for pvname, callback in pv_types_device.items():
            if self.verbose: print(f"Doing {pvname} with callback {callback}")
            pv_dict_device = getattr(self, pvname)

            # Next step is to connect to the PVs
            pv_dict_device[pvname] = epics.PV(f"{self.USER}{pv_name}")
            pv_dict_device[pvname].connect(timeout = 5)
            pv_dict_device[pvname].add_callback(lambda pvname = None, value = None, char_value = None, callback = callback, **kwargs:
                                                callback(pvname, value, char_value, **kwargs))
            
            # Now for the RBV callbacks

            rbv_name = readback_device[pvname]
            rbv_dict = getattr(self, rbv_name)

            rbv_dict["device"] = epics.PV(f"{self.USER}{rbv_name}")
            rbv_dict["device"].connect(timeout = 5)
            if self.verbose: print(f'PV {pvname} and callback {callback} has been done. Setup complete.')


#########################################################################################################################################
    
    def on_pv_change_delay(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr,self.port_number))
            except socket.error as e:
                if self.verbose: print(f"Socket reconnection failed: {e}")
                return
        
        if self.verbose: print(f"Conected to {pvname}. Writing value: {value}")
        try:
            if value > self.MAX_:
                raise ValueError(f"{value} is too big. Input smaller number.")
            else:
                value_str = str(value)
                message = f":PULSE{ch_num}:DELAY {value_str}\r\n"
                self.client_socket.send(message.encode())
                self.client_socket.recv(2048)
                time.sleep(0.02)
                
                
                # Confriming the RBV
                message_rbv = f":PULSE{ch_num}:DELAY?\r\n"
                self.client_socket.send(message_rbv.encode())
                time.sleep(0.02)
                delay = self.client_socket.recv(2048).decode().strip()
                if self.verbose: print('Delay: ', delay)
                self.write_pv(self.Delay_RBV_ch[ch_letter], delay)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

#########################################################################################################################################
        
    def on_pv_change_width(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f'Socket reconnection failed: {e}')
                return
        
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")
    
        try:
            if (value > self.MAX_) or (value < self.MIN_):
                raise ValueError(f"{value} is out of bounds. Try another value.")
            else:
                value_str = str(value)
                message = f':PULSE:WIDT {value_str}\r\n'
                
                self.client_socket.send(message.encode())
                time.sleep(0.02)
                self.client_socket.recv(2048)

                # Check RBV to confirm again
                message_rbv = f":PULSE:WIDT?\r\n"
            
                self.client_socket.send(message_rbv.encode())
                time.sleep(0.02)
                width = self.client_socket.recv(2048).decode().strip()
                if self.verbose: print(f"Width: {width}")
                self.write_pv(self.Width_RBV_ch[ch_letter], width)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as error:
            if self.verbose: print(f"An error occured: {error}")

#########################################################################################################################################

    def on_pv_change_source(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        """
        This function will change the source of the channel. For example if you want to sync ChA to ChB or T0, etc.
        """
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f'Socket reconnection failed: {e}')
                return
        
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")
        try:
            value_str = str(value)
            message = f':PULSE{ch_num}:SYNC {value_str}\r\n'
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)
            time.sleep(0.02)

            # Check RBV to confirm again
            message_rbv = f":PULSE{ch_num}:SYNC?\r\n"
            self.client_socket.send(message_rbv.encode())
            time.sleep(0.02)
            source = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Source: {source}")
            self.write_pv(self.Source_RBV_ch[ch_letter], source)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

#########################################################################################################################################
    
    def on_pv_change_mode(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        """
        Possible commands that can be inputted:
            NORM --> Sets system mode to continuous
            SING --> Sets system mode to single

        NOTE: COME BACK TO THIS ONE, MODE might be universal so no need to index by channel. FIX This one.
        """
        
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f'Socket reconnection failed: {e}')
                return
        
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")
        try:
            value_str = str(value)
            message = f':PULSE{ch_num}:CMODE {value_str}\r\n' # ADD the command for mode- continuous or single
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)
            time.sleep(0.02)

            # Check RBV to confirm again
            message_rbv = f":PULSE{ch_num}:MODE?\r\n" # Same here
            self.client_socket.send(message_rbv.encode())
            time.sleep(0.02)
            source = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Source: {source}")
            self.write_pv(self.Mode_RBV_ch[ch_letter], source)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

#########################################################################################################################################

def on_pv_change_state(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
    """
    This function controls the power of the channel. It will either turn it on or off.
    """
    if self.client_socket is None:
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.IP_addr, self.port_number))
        except socket.error as e:
            if self.verbose: print(f"Socket reconnection failed: {e}")
            return
    if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")
    try:
        if value == 1.0:
            value_str = "ON"
        else:
            value_str = "OFF"

        message = f":PULSE{ch_num}:STATE {value_str}\r\n"
        if self.verbose: print(f"Message sent: {message}")
        self.client_socket.send(message.encode())
        time.sleep(self.n1)
        self.client_socket.recv(2048).decode().strip()

        # Checking for the RBV
        message_rbv = f":PULSE{ch_num}:STATE?\r\n"
        self.client_socket.send(message_rbv.encode())
        time.sleep(self.n2)
        state = self.client_socket.recv(2048).decode().strip()
        if self.verbose: print(f"State: {state}")
        self.write_pv(self.ChannelState_RBV_ch[ch_letter], state) # Go back and add the Channel State dictionaries.

    except socket.error as e:
        if self.verbose: print(f"Socket error during communication: {e}")
        self.client_socket.close()
        self.client_socket = None

    except Exception as e:
        if self.verbose: print(f"An error occured: {e}")


#########################################################################################################################################
#########################################################################################################################################
# The following functions are functions for the entire BNC box. They are not indexed by channel.

    def on_pv_change_trigger(self, pvname = None, value = None, char_value = None, **kwargs):
        """
        This function changes the trigger mode of the BNC box. Possible commands that can be inputted are:
            DIS  --> Disables external trigger
            TRIG --> Sets system to external trigger
        Will have to configure this in the PVs because these are string outputs and not floats
        """

        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f'Socket reconnection failed: {e}')
                return
        
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")
        try:
            value_str = str(value)
            message = f':PULSE0:TRIG:MODE {value_str}\r\n' 
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)
            time.sleep(0.02)

            # Check RBV to confirm again
            message_rbv = f":PULSE0:TRIG:MODE?\r\n" 
            self.client_socket.send(message_rbv.encode())
            time.sleep(0.02)
            trigger_type = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Trigger Mode: {trigger_type}")
            self.write_pv(self.TriggerMode_RBV["device"], trigger_type) # Come back to this because Trigger only works for the whole system. Not per channel

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

#########################################################################################################################################

    def on_pv_change_run(self, pvname = None, value = None, char_value = None, **kwargs):
        """
        This function will check if the timing box is running or not. This command is similar to pressing the RUN/STOP button.
            STATE --> ON/OFF == 0/1
        If the device is on single shot, then it will only trigger once and then turn off after. Not sure how this will look like
        when sending a command.
        NOTE: TRIGGER MUST BE ON EXTERNAL AND ENABLED OR ELSE IT WILL NOT WORK
        """
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f"Socket reconnection failed: {e}")
                return
        
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")

        if value == 0:
            value_str = "OFF"
        elif value == 1:
            value_str = "ON"

        try:
            message = f':PULSE0:STATE {value_str}\r\n'
            self.client_socket.send(message.encode())
            time.sleep(self.n1)
            self.client_socket.recv(2048)

            # Reading the RBV
            message_rbv = f"PULSE0:STATE?\r\n"
            self.client_socket.send(message_rbv.encode())
            time.sleep(self.n2)
            state = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"BNC State: {state}")
            self.write_pv(self.Run_RBV["device"], state) #NOTE: No need to define channel because this controls entire system

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

#########################################################################################################################################

    def on_pv_change_period(self, pvname = None, value = None, char_value = None, **kwargs):
        """
        This function changes the period at which the box triggers at. Ranges from 100ns to 5000s.
        :PULSE0:PERIOD {value} --> Send the value
        :PULSE0:PERIOD? --> Returns the RBV for the period
        """
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f"Socket reconnection failed: {e}")
                return

        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")

        try:
            if (value > 5000) or (value < 1e-7):
                raise ValueError(f"Value {value} is out of range. Try another value.")
            else:
                value_str = str(value)
                message = f":PULSE0:PERIOD {value_str}\r\n"
                self.client_socket.send(message.encode())
                time.sleep(self.n1)
                self.client_socket.recv(2048)

                # Checking for RBV
                message_rbv = f":PULSE0:PERIOD?\r\n"
                self.client_socket.send(message_rbv.encode())
                time.sleep(self.n2)
                period = self.client_socket.recv(2048).decode().strip()
                if self.verbose: print(f"The period is: {period}")
                self.write_pv(self.Period_RBV["device"], period)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occurred: {e}")

#########################################################################################################################################
    def on_pv_change_mode_device(self, pvname = None, value = None, char_value = None, **kwargs):
        """
        This function will change the mode of the entire scope:
            :PULSE0:MODE {value} --> Possible values: Normal, Single, Burst, Dcycle
            :PULSE0:MODE? --> Returns the readback value
        """
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f"Socket reconnection failed: {e}")
                return
            
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")

        try:
            value_str = str(value)
            message = f":PULSE0:MODE {value_str}\r\n"
            self.client_socket.send(message.encode())
            time.sleep(self.n1)
            self.client_socket.recv(2048)

            # Checking for RBV
            message_rbv = ":PULSE0:MODE?\r\n"
            self.client_socket.send(message_rbv.encode())
            time.sleep(self.n2)
            mode = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"The mode now is: {mode}")
            self.write_pv(self.Mode_RBV["device"], mode)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occurred: {e}")

#########################################################################################################################################

    def on_pv_change_auto(self, pvname = None, value = None, char_value = None, **kwargs):
        """
        This command will turn on or off the automatic screen updates. If automatic speed updates is on
        the program will not be able to sned and proccess commands in 0.03s. It has to be at minumum 0.05s
        If the autodisplay is off then the device can process commands at 0.03s. So:

            auto_update = ON ---> time.sleep(0.05)
            auto_update = OFF ---> time.sleep(0.03)
        """
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f"Socket reconnection failed: {e}")
                return
        
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")

        try:
            value_str = str(value)
            message = f":DISPLAY:MODE {value_str}\r\n"
            self.client_socket.send(message.encode())
            time.sleep(self.n1)
            self.client_socket.recv(2048)

            # Checking for RBV
            message_rbv = ":DISPLAY:MODE?\r\n"
            self.client_socket.send(message_rbv.encode())
            time.sleep(self.n2)
            rbv = self.client_socket.recv(2048).decode().strip()
            print("The auto update is: ", rbv)
            self.write_pv(self.Auto_RBV["device"], rbv)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None

        except Exception as e:
            if self.verbose: print(f"An error occurred: {e}")


#########################################################################################################################################
#########################################################################################################################################


if __name__ == "__main__":
    # In the st.cmd file, you must enter the corresponding macros. You must define:
        # USER --> The name of BNC that you are going to use
        # IP_addr --> The IP address of the device
        # port_number --> The port number of the box
        # number_of_channels --> You should also define how many channels the device has

    BNC1 = TimingBoxBNC(USER = "BNC1:", IP_addr = "10.97.106.97", port_number = 2101, verbose = True)
    BNC1.setup_channels(8) # Define 8 different channels
    print("Python script is ready for controlling.")

    while True:
        try:
            epics.ca.poll()
            time.sleep(0.01)
            
        except KeyboardInterrupt:
            break

