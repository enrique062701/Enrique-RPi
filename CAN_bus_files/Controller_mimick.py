"""
This will mimick the controller.
"""

import can
import os
import time
import csv


try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Cannot find PiCAN board. Check connections.')

print('Connection complete. Will now send command.')

while True:
    try:
        message = bus.recv()

        if message.a

