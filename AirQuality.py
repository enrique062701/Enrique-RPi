import busio
import board
import time


class AirQuality:
    def __init__(self, Device_addr, byte_size):
        self.Device_addr = Device_addr
        self.byte_size = byte_size

    def connect(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        response = bytearray(2)

        if self.Device_addr not in self.i2c.scan():
            print("Device not found")
        else:
            print("Device found")
        
    def read_data(self):
        response = bytearray(self.byte_size)
        self.i2c.readfrom_into(self.Device_addr, response)
        
        print([hex(x) for x in response])

        self.header = response[:2] # First two are always fixed
        print(f"This is the header: {[hex(x) for x in self.header]}")
        self.frame_length = response[2:4]
        print(f"This is the frame_length{[hex(x) for x in self.frame_length]}")
        self.data1 = response[4:6]
        self.data2 = response[6:8]
        self.data3 = response[8:10]

        



if __name__ == "__main__":
    DEVICE = 0x12
    Sensor1 = AirQuality(DEVICE, 35)
    Sensor1.connect()
    Sensor1.read_data()





