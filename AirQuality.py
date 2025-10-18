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
print(inspect.getsource(adafruit_ahtx0))



i2c = board.STEMMA_I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    print("\nTemperature: %0.1f C" % sensor.temperature)
    time.sleep(2)


print('Test')


