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

        if message.arbitration_id == 0x1803280a:
            initial_message = can.Message(arbitration_id == 0x3080a, data = bytes.fromhex('00000000'), is_extended_id = True)
            bus.send(initial_message)
            
            

1100