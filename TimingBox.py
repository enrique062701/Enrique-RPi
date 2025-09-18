"""
This python script will be an OO script that can be used for any BMC timing box. This will by pass the
need form multiple longs python scripts. Can just define each box in one script.
"""
import socket
import time
import epics

class TimingBoxBNC:
    USER = "BNC" # This is constant because all boxes are called BNCs there are multiple

    def __init__(self, IP_addr:str, port_number: int, verbose = True):
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
            if self.verbose: print(f"PV Error on {pv.name}")


    def get_channels(self, number_of_channels: int) -> list:
        """
        Helper function that converts the number of channels to a list of all the channels available.
        Returns:
        {'A': 1, 'B': 2, 'C': 3, ....}
        """
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.channels = {
            letters[i]: i+1 for i in range(number_of_channels)
        }
        return channels

    
    def channels(self, number_of_channels: int) -> dict:
        """
        Input the number of channels your specific BNC box has. Returns dictionaries that will be used to
        index for specific quantities. This function also adds callback funcctions to it.
        """

        channels_map = self.get_channels(number_of_channels)
        channels = list(channels_map.keys())

        self.delay_RBV_ch = {}
        self.delay_desired_ch = {}
        self.source_RBV_ch = {}
        self.source_desired_ch = {}
        self.width_RBV_ch = {}
        self.width_desired_ch = {}
        self.mode_desired_ch = {}
        self.mode_RBV_ch = {}
        self.trigger_desired_ch = {}
        self.trigger_RBV_ch = {}

        # Define all the PVs that you want to create callbacks for and control. Can add them here if you would like to add more.
        pv_types = [
            ("DelayDesired", self.on_pv_change_delay),
            ("WidthDesired", self.on_pv_change_width),
            ("SourceDesired", self.on_pv_change_source),
            ("ModeDesired", self.on_pv_change_mode),
            ("TriggerDesired", self.on_pv_change_trigger)
        ]

        readback_map = { # The PVs that will be used.
            "DelayDesired": "Delay_RBV",
            "WidthDesired": "Width_RBV",
            "SourceDesired": "Sourc_RBV",
            "ModeDesired": "Mode_RBV",
            "TriggerDesired": "TriggerMode_RBV"
        }

        for ch_letter, ch_num in channels_map.items():
            for pv_name, callback in pv_types:
                dict_name = f"{pv_name.lower()}_ch"
                pv_dict = getattr(self, dict_name)

                # Creating the PV object
                pv_dict[ch_letter] = epics.PV(f"{USER}ch{ch_letter}:{pv_name}")
                pv_dict[ch_letter].connect(timeout = 5)
                pv_dict[ch_letter].add_callback(
                    lambda pvname = None, value = None, char_value = None, 
                    ch_letter = ch_letter, ch_num = ch_num, callback = callback, **kwargs:
                    callback(ch_num, ch_letter, pvname, value, char_value, **kwargs)
                )

                # Corresponding PV for the readback values
                rbv_name = readback_map[pv_name]
                rbv_dict_name = f"{rbv_name.lower()}_ch"
                rbv_dict = getattr(self, rbv_dict_name)
                rbv_dict[ch_letter] = epics.PV(f"{USER}ch{ch_letter}:{rbv_name}")
                rbv_dict[ch_letter].connect(timeout = 5)

    
    def on_pv_change_delay(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr,self.port_number))
            except socket.error as e:
                if self.verbose: print(f"Socket reconnection failed: {e}")
                return


        channels = self.get_channels()
        
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
            self.delay_read_ch[ch_letter].put(delay, wait = True, timeout = 0.2)

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
        
        channels = self.get_channels()
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
            self.width_read_ch[ch_letter].put(width, wait = True, timeout = 0.2)

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
        
        channels = self.get_channels()
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
            self.source_RBV_ch[ch_letter].put(source, wait = True, timeout = 0.2)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")

    
    def on_pv_change_mode(self, ch_num: int, ch_letter: str, pvname = None, value = None, char_value = None, **kwargs):
        if self.client_socket is None:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.IP_addr, self.port_number))
            except socket.error as e:
                if self.verbose: print(f'Socket reconnection failed: {e}')
                return
        
        channels = self.get_channels()
        if self.verbose: print(f"Connected to {pvname}. Writing value: {value}")
        try:
            value_str = str(value)
            message = f':PULSE{ch_num}:SYNC {value_str}\r\n' # ADD the command for mode- continuous or single
            self.client_socket.send(message.encode())
            self.client_socket.recv(2048)

            # Check RBV to confirm again
            message = f"PULSE{ch_num}:SYNC?\r\n" # Same here
            time.sleep(0.02)
            source = self.client_socket.recv(2048).decode().strip()
            if self.verbose: print(f"Width: {source}")
            self.mode_RBV_ch[ch_letter].put(source, wait = True, timeout = 0.2)

        except socket.error as e:
            if self.verbose: print(f"Socket error during communication: {e}")
            self.client_socket.close()
            self.client_socket = None
        except Exception as e:
            if self.verbose: print(f"An error occured: {e}")






        

            











