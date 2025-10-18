"""
This script will communicate with the air quality sensor and have it send a notification if level gets to low.
Will use epics to communicate.
"""
import time
import board
import adafruit_ahtx0
import busio
import inspect
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
# Communication over the board's default I2C bus

# First step is to create a sensor object
print(inspect.getsource(PM25_I2C))

reset_pin = None

i2c = busio.I2C(board.SCL, board.SDA, frequency = 100000)

pm25 = PM25_I2C(i2c, reset_pin)

print("Found PM2.5 sensor, reading data...")

while True:
    time.sleep(1)
    try:
        aqdata = pm25.read()

    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue

    except KeyboardInterrupt:
        break
    print()
    print("Connection Units (standard)")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    )
    print("Concentration Units (environmental)")
    print("---------------------")
    print(
        "PM 1.0 %d\tPM2.5: %d\tPM10: $d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    )
    print("---------------------")
    print("Particles > 0.3um / 0.1L air: ", aqdata["particles 03um"])



