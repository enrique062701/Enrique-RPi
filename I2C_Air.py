import busio
import board
import time
import epics

class AirSensor:
    def __init__(self, Device_addr):
        self.Device_addr = Device_addr

  
    def connect(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        response = bytearray(2)
        if not self.Device_addr in self.i2c.scan():
            print(f"Could not find sensor on Bus! Check connections")

        self.i2c.writeto_then_readfrom(self.Device_addr, bytes([0x71]), response)
        status = response[0]
        if (status & 0x18) == 0x18:
            time.sleep(0.1)
        else:
            print("Retry again.")

    def query_data(self):
        self.i2c.writeto(self.Device_addr, bytes([0xAC, 0x33, 0x00]))
        time.sleep(0.1)
        response = bytearray(6)
        self.i2c.readfrom_into(self.Device_addr, response)
        try:
            if(response[0] & (1 << 7)) == 0:
                self.temperature_raw = (
                    ((response[3] & ((1 << 4) - 1)) << 16) | (response[4] << 8) | response[5]
                )
                self.humidity_raw = (
                    (response[1] << 12) | (response[2] << 4) | (response[3] >> 4)
                )
        except Exception as e:
            print(f"Error: {e}")
        
        temperature = self.read_temperature()
        humidity = self.read_humidity()

        print(f"Temperature: {temperature:0.1f}C | Humidity: {humidity:0.1f} %")
        

    def read_humidity(self):
        self.RH = (self.humidity_raw / (2 ** 20)) * 100
        return self.RH

    def read_temperature(self):
        self.RT = (self.temperature_raw / (2 ** 20)) * 200 - 50
        return self.RT


if __name__ == "__main__":
    AIRSENSOR = 0x38
    Ada_fruit = AirSensor(AIRSENSOR)
    Ada_fruit.connect()
    while True:
        Ada_fruit.query_data()
        



