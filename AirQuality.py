"""
This script will communicate with the air quality sensor and have it send a notification if level gets to low.
Will use epics to communicate.
"""
import time
import board
import adafruit_ahtx0
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
# Communication over the board's default I2C bus

# First step is to create a sensor object
i2c = board.I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    print(f"\nTemperature: {sensor.temperature:0.1f} C")
    print(f"Humidity: {sensor.relative_humidity:0.1f} %")
    time.sleep(0.1)




