"""
This file will save data from the laser can bus system and will try to decode it. It will save data for around
10 seconds. This is too see what the usual message is.

The bitrate that the laser communicates at is 1 M/bit (1,000,000) per second. 
"""
import can
import os
import time
import csv


# Next is to check if the port is up
try:
    bus = can.interface.Bus(channel = 'can0', interface = 'socketcan')
except OSError:
    print('Can port not found, double check if port is connected')
print('Connected to can0, ready for data taking.')

duration = 15
end_time = time.time() + duration

with open("idle_main_menu.csv", "w", newline = "") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Arbitration_id", "dlc", "data"])

    while time.time() < end_time:
        msg = bus.recv(timeout = 1.0)
        if msg:
            writer.writerow([
                msg.timestamp,
                hex(msg. arbitration_id),
                msg.dlc,
                msg.data.hex()
            ])
            print(msg)

bus.shutdown()
print('Saved data to idle_main_menu.csv')


