"""
This python script will be an OO script that can be used for any BMC timing box. This will by pass the
need form multiple longs python scripts. Can just define each box in one script.
"""
import socket
import time
import epics

class TimingBoxBNC:
    USER = "BNC" # This is constant because all boxes are called BNCs there are multiple

    def __init__(self, IP_addr, port_number, verbose = True):
        self.verbose = verbose


    def connect_device(self, IP_addr, port_number):
        """
        Uses socket communication to connect to device.
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect(self.IP_addr, self.port_number)
        except socket.error as e:
            if self.verbose: print(f"Initial socket connection failed: {e}")
            client_socket = None


    def write_pv(self, pv, value):
        try:
            if pv.connected:
                pv.put(value, wait = True, timeout = 0.05)
            else:
                if self.verbose: print(f'Failed to connect to {pv.pvname}.')
        except:
            if self.verbose: print(f"PV Error on {pv.name}")

    
    def channels(self, number_of_channels):
        self.number_of_channels = number_of_channels

        max_channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        delay_read_ch = {}
        delay_desired_ch = {}
        source_read_ch = {}
        source_desired_ch = {}
        width_read_ch = {}
        width_desired_ch = {}

        for i in range(number_of_channels):










