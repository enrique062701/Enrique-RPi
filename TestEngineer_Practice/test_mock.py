"""
This file will simulate a sensor recieving live data.
Enrique
"""
from unittest.mock import MagicMock

def read_sensor(device):
    return device.read_voltage()

def test_mock_device():
    mock_device = MagicMock()
    mock_device.read_voltage.return_value = 3.3
    result = read_sensor(mock_device)
    assert result == 3.3
    mock_device.read_voltage.asser_called_once()

if __name__ == "__main__":
    test_mock_device()


