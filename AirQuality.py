"""
This script will communicate with the air quality sensor and have it send a notification if level gets to low.
Will use epics to communicate.
"""
import time
import board
import adafruit_ahtx0
import inspect

# Communication over the board's default I2C bus

# First step is to create a sensor object
#print(inspect.getsource(board))



sensor = adafruit_ahtx0.AHTx0(board.I2C())

while True:
    print(sensor.temperature)
    time.sleep(2)


print('Test')


