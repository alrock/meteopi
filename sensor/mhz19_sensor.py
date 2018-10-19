import serial
import time

from datetime import datetime

from sensor.sensor import Sensor, SensorException


class MHZ19Sensor(Sensor):

    CACHE_UPDATE_INTERVAL = 10  # in seconds

    def __init__(self, port='/dev/serial0'):
        super().__init__('MH-Z19')
        self.port = port
        self.sensor = serial.Serial(self.port, 9600, timeout=2.0)
        # 'warm up' with reading one input
        self.sensor.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
        time.sleep(0.1)
        self.sensor.read(9)  # Ignore the response
        self.data_cache = None

    def _parse_data(self, data):
        return {'co2': data[2] * 256 + data[3], 'temperature': data[4] - 40, 'status': data[5],
                'unknown': data[6] * 256 + data[7], 'timestamp': datetime.now()}

    @staticmethod
    def crc8(a):
        # Function to calculate MH-Z19 crc according to datasheet
        crc = 0x00
        count = 1
        b = bytearray(a)
        while count < 8:
            crc += b[count]
            count = count + 1
        # Truncate to 8 bit
        crc %= 256
        # Invert number with xor
        crc = ~crc & 0xFF
        crc += 1
        return crc

    def calibrate(self):
        self.sensor.write(b"\xFF\x01\x87\x00\x00\x00\x00\x00\x78")

    def abc(self, enable=True):
        if enable:
            self.sensor.write(b"\xFF\x01\x79\xA0\x00\x00\x00\x00\xE6")
        else:
            self.sensor.write(b"\xFF\x01\x79\x00\x00\x00\x00\x00\x86")

    @property
    def sample(self):
        if not self.data_cache or (datetime.now() - self.data_cache['timestamp']).seconds > self.CACHE_UPDATE_INTERVAL:
            # Send "read value" command to MH-Z19 sensor
            self.sensor.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
            time.sleep(0.1)
            s = self.sensor.read(9)
            z = bytearray(s)
            crc = self.crc8(s)
            # Calculate crc
            if crc != z[8]:
                raise SensorException(self.SENSOR_NAME,
                                      'CRC error calculated %d bytes= %d:%d:%d:%d:%d:%d:%d:%d crc= %dn' % (
                                          crc, z[0], z[1], z[2], z[3], z[4], z[5], z[6], z[7], z[8]))
            self.data_cache = self._parse_data(s)
        return self.data_cache

    @property
    def co2(self):
        return self.sample['co2']

    @property
    def temperature(self):
        return self.sample['temperature']
