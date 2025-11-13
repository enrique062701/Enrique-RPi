"""
This file will contain different functions that will imitate controlling a sensor. It will then be imported 
to different scripts to test out each function individually.
Enrique Cisneros
"""

def voltage_to_temp(voltage):
    """Converts voltage to temperature from Analog signals."""
    if voltage < 0 or voltage > 5:
        raise ValueError("Voltage out of range (0-5V)")
    return 25.0 * voltage


def move_motor(position, max_limit = 100):
    if position < 0 or position > max_limit:
        raise ValueError("Position is out of range")
    return f"Motor moved to {position}"


