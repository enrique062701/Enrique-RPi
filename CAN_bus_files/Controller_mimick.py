"""
This will mimick the controller.
"""

import can
import os
import time
import csv

# Could make a map so whenever a message is recieved it responds with the corresponding message
try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Cannot find PiCAN board. Check connections.')

print('Connection complete. Will now send command.')

message_status = ['030000', '020000', '070000', '100000', '100000', '020000', '070000',
                    '020000', '100000', '100000', '020000', '070000', '020000', '100000',
                    '100000', '020000', '070000', '0d0000', '020000', '100000', '100000', 
                    '0d0000', '0a0000', '0a0000', '020000', '130000', '130000', '130000',
                    '121fff', '111fff']




while True:
    try:
        message = bus.recv()

        while message.arbitration_id == 0x1803280a:
            if message.data == 00000000:
                initial_message = can.Message(arbitration_id = 0x3080a, data = bytes.fromhex('00000000'), is_extended_id = True)
                bus.send(initial_message)
        
        while message.arbitration_id == 0x18820810:
            if message.data == 01:
                second_message = can.Message(arbitration_id = 0x1900410, data = bytes.fromhex('010000'), is_extended_id = True)
                bus.send(second_message)
            if message.data == 1100:
                for i in message_status:
                    data = fromhex(i)
                    cycle = can.Message(arbitration_id = 0x1900410, data = data, is_extended_id = True)
            



                
        
        
    except KeyboardInterrupt:
        break

while True:
    try:
        message2 = bus.recv()


            

1100