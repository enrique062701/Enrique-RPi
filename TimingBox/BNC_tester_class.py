import epics
import socket
import subprocess
import threading
import time
import numpy as np

class BNC_Tester:

    def __init__(self, USER: str, channels: int):
        self.USER = USER
        self.channels = channels # Number of channels

    def loop_range(self, MIN: int, MAX: int) -> dict:
        """
        This function returns dictionaries with the inputted range. It will be for both the width and the delay.
        """
        self.Delays = np.arange(0, MAX, 1)
        self.Delay_small = np.arange(0, 0.5, 0.0001)
        self.Delay_limits = [1, 0.1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9]

        self.channel_delay = {}
        self.channel_delays_small = {}
        self.channel_delay_limits = {}
        self.channel_width = {}
        self.channel_width_small = {}
        self.channel_width_small = {}

        for i in range(len(self.channels)):
            self.channel_delay[f'Ch{i}'] = self.Delays
            




