"""
This file will test functions using the pytest python library.
Enrique
"""
import pytest
from Sensor_example import move_motor

@pytest.mark.parametrize("position", [0,10,20,30,40,50,60,70,80,90,100])
def test_motor_position(position):
    assert move_motor(position) == f"Motor moved to {position}"
    
def test_valid_positions():
    assert move_motor(10) == "Motor moved to 10"
    assert move_motor(0) == "Motor moved to 0"

def test_out_of_range():
    with pytest.raises(ValueError):
        move_motor(-5)
    with pytest.raises(ValueError):
        move_motor(150)



if __name__ == "__main__":
    print(test_out_of_range())
    print(test_valid_positions())




