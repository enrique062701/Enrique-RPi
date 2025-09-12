"""
This script will send messages to the second pi and then reply when it recieves a message in an infinite loop.
This will act as the laser. 0x18820810

THIS WILL ACT AS THE LASER
"""
import os
import can
import time


message_cycle = ['00202000', '0020312000', '00302500', '00f84300', '0200007a20', '02010c3b09',
 '0201163b09', '020a016f09', '023e0c3b09', '070101', '070202',
 '0a0000000901', '0a00003b0001', '0d00', '0d01',
 '101e00', '102045204f464620', '1020506b20202020'
 '10506d702020302e', '1074202020302e30', '12']


os.system('sudo ip link set can0 down')
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ip link set can0 up')
print('Port has been configured')


try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Can not create bus connection')

print('Bus connection has been created')


while True:
    try:
        message_received = bus.recv(timeout = 1)

        print('Looking for initial message')
        if message_received is None:
            while True:
            # If no message is recieved from the controller it will just cycle its ID at 2Hz
                echo_ = can.Message(arbitration_id = 0x18820810, data = b'ID', is_extended_id = True)
                bus.send(echo_)
                time.sleep(0.5)

                message_received = bus.recv(timeout = 1)

                if message_received is not None:
                    if message_received.arbitration_id == 0x19000410:
                        print('Controller detected.')
                        break
       
        if message_received.arbitration_id == '0x19000410':
            try:
                # This checks if the controller sent an initial message 'hello' indicating controller is active
                text = message_received.decode("ascii")
                print('Got initial message')
                if text == 'hello':
                    message_reply = can.Message(arbitration_id = 0x18820810, data = b'Copy', is_extended_id = True)
                    while True:
                        for message in message_cycle:
                            msg = can.Message(arbitration_id = 0x18820810, data = bytes.fromhex(message), is_extended_id = True)
                            bus.send(msg)
                    


            except UnicodeDecodeError:
                print(f"Got no text data: {message_received.hex()}")
         

    except KeyboardInterrupt:
        print("Program stopped")
        break





