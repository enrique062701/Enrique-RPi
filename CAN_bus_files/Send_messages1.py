"""
This script will send messages to the second pi and then reply when it recieves a message in an infinite loop.
Sender will be 0x19000410.

THIS WILL ACT AS THE CONTROLLER
"""
import os
import can
import time
# The messages that the controller will cycle
message_cycle = ['021fff', '071fff', '0a1fff', '0d1fff', '101fff', '121fff']

os.system('sudo ip link set can0 down')
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ip link set can0 up')
print('Port has been configured')


try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Can not create bus connection')
    exit()

print('Bus connection has been created')


initial_message = can.Message(arbitration_id = 0x19000410, data= b"hello", is_extended_id = True)
bus.send(initial_message)

while True:
    try:
        # The loop will first send an intial message to see if the "controller" is connected.
        message_response = bus.recv(timeout = 2)
        if message_response is None:
            continue
        # Now check if the laser replies. If the laser replies then will continuosly send messages in the can-bus system
        if message_response.arbitration_id == '0x18820810':
            try:
                response = message_response.decode("ascii")
                if response == 'Copy':
                    while True:
                        for message in message_cycle:
                            msg = can.Message(arbitration_id = 0x19000410, data = bytes.fromhex(message), is_extended_id = True)
                            bus.send(msg)
                            
            except UnicodeDecodeError:
                print(f"Got no text data: {message_received.hex()}")

    except KeyboardInterrupt:
        break
                    






