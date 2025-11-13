"""
This file will showcase how to use the Python library: unittest
Unittest is Classed based function that requies you to be familiar with classes.
Enrique
"""
import numpy as np
import time
import unittest
from Sensor_example import voltage_to_temp

class TestSensor(unittest.TestCase):
    def test_normal_range(self):
        self.assertEqual(voltage_to_temp(2), 50)
        self.assertAlmostEqual(voltage_to_temp(1.5), 37.5, places = 2)
        print("Ran OK")

    def test_low_voltage(self):
        with self.assertRaises(ValueError):
            voltage_to_temp(-1)

    def test_higgh_voltage(self):
        with self.assertRaises(ValueError):
            voltage_to_temp(6)

if __name__ == "__main__":
    unittest.main()

