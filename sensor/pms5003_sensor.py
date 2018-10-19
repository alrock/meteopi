from datetime import datetime

import pigpio

from sensor.sensor import Sensor
from sensor.serial_reader import SerialReader


class PMS5003Sensor(Sensor):

    CACHE_UPDATE_INTERVAL = 10  # in seconds

    def __init__(self, rx=25, set_gpio=7):
        super().__init__('PMS5003')
        self.rx = rx
        self.set_gpio = set_gpio
        self.pi = pigpio.pi()
        self.pi.set_mode(self.rx, pigpio.INPUT)
        self.pi.set_mode(self.set_gpio, pigpio.OUTPUT)
        self.data_cache = None

    def __del__(self):
        self.pi.stop()

    def disable(self):
        self.pi.write(self.set_gpio, pigpio.HIGH)

    def enable(self):
        self.pi.write(self.set_gpio, pigpio.LOW)

    def _parse_data(self, data):
        return {'apm10': data[4] * 256 + data[5],
                'apm25': data[6] * 256 + data[7],
                'apm100': data[8] * 256 + data[9],
                'pm10': data[10] * 256 + data[11],
                'pm25': data[12] * 256 + data[13],
                'pm100': data[14] * 256 + data[15],
                'gt03um': data[16] * 256 + data[17],
                'gt05um': data[18] * 256 + data[19],
                'gt10um': data[20] * 256 + data[21],
                'gt25um': data[22] * 256 + data[23],
                'gt50um': data[24] * 256 + data[25],
                'gt100um': data[26] * 256 + data[27],
                'timestamp': datetime.now()}

    @property
    def sample(self):
        if not self.data_cache or (datetime.now() - self.data_cache['timestamp']).seconds > self.CACHE_UPDATE_INTERVAL:
            reader = SerialReader(self.pi, self.rx)
            while True:
                data = reader.read(1)
                if data[0] == 0x42:
                    data += reader.read(1)
                    if data[1] == 0x4D:
                        data += reader.read(28)
                        self.data_cache = self._parse_data(data)
                        break
        return self.data_cache

    @property
    def apm10(self):
        return self.sample['apm10']

    @property
    def apm25(self):
        return self.sample['apm25']

    @property
    def apm100(self):
        return self.sample['apm100']
