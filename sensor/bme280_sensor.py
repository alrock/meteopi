from datetime import datetime

import smbus2
import bme280

from sensor.sensor import Sensor


class BME280Sensor(Sensor):

    CACHE_UPDATE_INTERVAL = 5  # in seconds

    def __init__(self, port=1, address=0x76):
        super().__init__('BME280')
        self.address = address
        self.bus = smbus2.SMBus(port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)
        self.data_cache = None

    @property
    def sample(self):
        if not self.data_cache or (datetime.now() - self.data_cache['timestamp']).seconds > self.CACHE_UPDATE_INTERVAL:
            sample = bme280.sample(self.bus, self.address, self.calibration_params)
            self.data_cache = {'temperature': sample.temperature, 'humidity': sample.humidity,
                               'pressure': sample.pressure, 'timestamp': sample.timestamp}
        return self.data_cache

    @property
    def temperature(self):
        return self.sample['temperature']

    @property
    def humidity(self):
        return self.sample['humidity']

