"""
This python script will be an OO script that can be used for any BMC timing box. This will by pass the
need form multiple longs python scripts. Can just define each box in one script.
"""
import socket
import time
import epics

class TimingBoxBNC:

    def __init__(self, USER, IP_addr:str, port_number: int, verbose = True):
        self.USER = USER
        self.verbose = verbose
        self.IP_addr = IP_addr
        self.port_number = port_number
        self.client_socket = None


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


    def write_pv(self, pv, value):
        try:
            if pv.connected:
                pv.put(value, wait = True, timeout = 0.05)
            else:
                if self.verbose: print(f'Failed to connect to {pv.pvname}.')
        except:
            if self.verbose: print(f"PV Error on {pv.pvname}: {e}")


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
        self.Delay_desired_ch = {}
        self.Delay_RBV_ch = {}
        self.Width_desired_ch = {}
        self.Width_RBV_ch = {}
        self.Source_desired_ch = {}
        self.Source_RBV_ch = {}
        self.Mode_desired_ch = {}
        self.Mode_RBV_ch = {}
        self.TriggerMode_desired_ch = {}
        self.TriggerMode_RBV_ch = {}

        # Desired PVs and their callbacks
        pv_types = {
            "DelayDesired": self.on_pv_change_delay,
            "WidthDesired": self.on_pv_change_width,
            "SourceDesired": self.on_pv_change_source,
            "ModeDesired": self.on_pv_change_mode,
            "TriggerModeDesired": self.on_pv_change_trigger,
        }

        # Mapping from Desired PVs to their readbacks
        readback_map = {
            "DelayDesired": "Delay_RBV",
            "WidthDesired": "Width_RBV",
            "SourceDesired": "Source_RBV",
            "ModeDesired": "Mode_RBV",
            "TriggerModeDesired": "TriggerMode_RBV",
        }

        # Mapping Desired PV names to attribute dictionaries
        pv_attr_map = {
            "DelayDesired": "Delay_desired_ch",
            "WidthDesired": "Width_desired_ch",
            "SourceDesired": "Source_desired_ch",
            "ModeDesired": "Mode_desired_ch",
            "TriggerModeDesired": "TriggerMode_desired_ch",
        }

        # Loop through channels and create PVs
        for ch_letter, ch_num in channels_map.items():
            for pv_name, callback in pv_types.items():
                if self.verbose: print(f"Doing {pv_name} with callback {callback}") #For sanity check to see if its working
                dict_name = pv_attr_map[pv_name]
                pv_dict = getattr(self, dict_name)

                # Connects to desired PV using the Dictionary mapping and connects callback function
                pv_dict[ch_letter] = epics.PV(f"{self.USER}ch{ch_letter}:{pv_name}")
                pv_dict[ch_letter].connect(timeout=5)
                pv_dict[ch_letter].add_callback(
                    lambda pvname = None, value = None, char_value = None,
                        ch_letter = ch_letter, ch_num = ch_num, callback = callback, **kwargs:
                        callback(ch_num, ch_letter, pvname, value, char_value, **kwargs)
                )

                # Maps the readback values.
                rbv_name = readback_map[pv_name]              
                rbv_dict_name = f"{rbv_name}_ch"             
                rbv_dict = getattr(self, rbv_dict_name)

                rbv_dict[ch_letter] = epics.PV(f"{self.USER}ch{ch_letter}:{rbv_name}")
                rbv_dict[ch_letter].connect(timeout=5)
                if self.verbose: print(f"PV {pv_name} and callback {callback} has been done.") # For sanity check to see if its working

            if self.verbose:
                print(f"Channel {ch_num} ({ch_letter}) setup complete.")


    
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
            value_str = str(value)
            message = f":PULSE{ch_num}:DELAY {value_str}\r\n"
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)
            
            # Confriming the RBV
            message_rbv = f":PULSE{ch_num}:DELAY?\r\n"
            time.sleep(0.02)
            delay = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print('Delay: ', delay)
            self.write_pv(self.Delay_read_ch[ch_letter], delay)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

        
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
            value_str = str(value)
            message = f':PULSE{ch_num}:WIDT {value_str}\r\n'
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)

            # Check RBV to confirm again
            message = f"PULSE{ch_num}:WIDT?\r\n"
            time.sleep(0.02)
            width = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Width: {width}")
            self.write_pv(self.Width_read_ch[ch_letter], width)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")


    def on_pv_change_source(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
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

            # Check RBV to confirm again
            message = f"PULSE{ch_num}:SYNC?\r\n"
            time.sleep(0.02)
            source = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Width: {source}")
            self.write_pv(self.Source_RBV_ch[ch_letter], source)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

    
    def on_pv_change_mode(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        """
        Possible commands that can be inputted:
            NORM --> Sets system mode to continuous
            SING --> Sets system mode to single
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
            message = f':PULSE{ch_num}:MODE {value_str}\r\n' # ADD the command for mode- continuous or single
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)

            # Check RBV to confirm again
            message = f"PULSE{ch_num}:MODE?\r\n" # Same here
            time.sleep(0.02)
            source = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Width: {source}")
            self.write_pv(self.Mode_RBV_ch[ch_letter], source)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

    
    def on_pv_change_trigger(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        """
        This function changes the trigger mode of the BNC box. Possible commands that can be inputted are:
            DIS  --> Disables external trigger
            TRIG --> Sets system to external trigger
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
            message = f':PULSE{ch_num}:TRIG:MODE {value_str}\r\n' # ADD the command for mode- continuous or single
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)

            # Check RBV to confirm again
            message = f"PULSE{ch_num}:TRIG:MODE?\r\n" # Same here
            time.sleep(0.02)
            trigger_type = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Width: {source}")
            self.write_pv(self.Trigger_RBV_ch[ch_letter], trigger_type)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

if __name__ == "__main__":
    
    BNC1 = TimingBoxBNC(USER = USER, IP_addr = IP_addr, port_number = port_number)
    BNC1.setup_channels(8) # Define 8 different channels

    while True:
        try:
            epics.ca.poll()
            time.sleep(0.01)
            print("Python script is active ready to control")
        except KeyboardInterrupt:
            break






        

            











