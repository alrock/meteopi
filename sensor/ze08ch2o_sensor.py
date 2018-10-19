from datetime import datetime

import pigpio

from sensor.sensor import Sensor
from sensor.serial_reader import SerialReader


class ZE08CH2OSensor(Sensor):

    CACHE_UPDATE_INTERVAL = 10  # in seconds

    def __init__(self, rx=23):
        super().__init__('ZE08-CH2O')
        self.rx = rx
        self.pi = pigpio.pi()
        self.pi.set_mode(self.rx, pigpio.INPUT)
        self.data_cache = None

    def __del__(self):
        self.pi.stop()

    def _parse_data(self, data):
        return {'ch2o': data[4] * 256 + data[5], 'full_range': data[6] * 256 + data[7], 'timestamp': datetime.now()}

    @property
    def sample(self):
        if not self.data_cache or (datetime.now() - self.data_cache['timestamp']).seconds > self.CACHE_UPDATE_INTERVAL:
            reader = SerialReader(self.pi, self.rx)
            while True:
                data = reader.read(1)
                if data[0] == 0xFF:
                    data += reader.read(1)
                    if data[1] == 0x17:
                        data += reader.read(7)
                        self.data_cache = self._parse_data(data)
                        break
        return self.data_cache

    @property
    def ch2o(self):
        return self.sample['ch2o']
