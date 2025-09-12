"""
This file will test sending a command to the laser via the can bus system. This command should change the burst mode
of the laser from continuous to burst.
"""
import os
import can
import time

# Connect to the can device first
#os.system('sudo ip link set can0 down')
#os.system('sudo ip link set can0 type can bitrate 1000000')
#os.system('sudo ip link set can0 up')

try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Cannot find PiCAN board. Check connections.')
    exit()

print('Connection complete. Will now send command.')

# Next is to send the messages to the CAN bus system

while True:
    try:
        message = bus.recv()
        if message.arbitration_id == 0x18820810:
            print('Laser is active')
            break
        else:
            print('Laser is not active. Searching again')
            time.sleep(0.1)
    except KeyboardInterrupt:
        break

commands = [ "121fef", "071fef", "101fef", "101fef"]
controller_id = 0x19000410

send_message = can.Message

for command in commands:
    msg = can.Message(arbitration_id = controller_id, data=bytes.fromhex(command), is_extended_id = True)

    try:
        bus.send(msg)
        print(f'Message: {command} has been sent')
        time.sleep(0.001)
    except can.CanError:
        print('Message not sent.')







