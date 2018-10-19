import smbus2
import time

from datetime import datetime

from sensor.sensor import Sensor, SensorException


class BH1750Sensor(Sensor):

    ADDRESS_L = 0x23
    POWER_DOWN = 0x00  # No active state
    POWER_ON = 0x01  # Power on
    RESET = 0x07  # Reset data register value
    # Start measurement at 4lx resolution. Time typically 16ms.
    CONTINUOUS_LOW_RES_MODE = 0x13
    # Start measurement at 1lx resolution. Time typically 120ms.
    CONTINUOUS_HIGH_RES_MODE_1 = 0x10
    # Start measurement at 0.5lx resolution. Time typically 120ms.
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11
    # Start measurement at 1lx resolution. Time typically 120ms.
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_1 = 0x20
    # Start measurement at 0.5lx resolution. Time typically 120ms.
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_HIGH_RES_MODE_2 = 0x21
    # Start measurement at 1lx resolution. Time typically 120ms.
    # Device is automatically set to Power Down after measurement.
    ONE_TIME_LOW_RES_MODE = 0x23

    CACHE_UPDATE_INTERVAL = 10  # in seconds

    def __init__(self, port=1, address=0x23):
        super().__init__('BH1750')
        self.port = port
        self.address = address
        try:
            self.bus = smbus2.SMBus(port)
        except OSError as e:
            raise SensorException(self.SENSOR_NAME, e.strerror) from e
        self.power(False)
        self.sens = 0
        self.set_sensitivity()
        self.resolution = 0
        self.set_resolution(self.ONE_TIME_HIGH_RES_MODE_2)
        self.data_cache = None

    def _set_mode(self, mode):
        try:
            self.bus.write_byte(self.address, mode)
            self.mode = mode
        except OSError as e:
            raise SensorException(self.SENSOR_NAME, e.strerror) from e

    def power(self, on):
        self._set_mode(self.POWER_ON if on else self.POWER_DOWN)

    def reset(self):
        self.power(True)
        self._set_mode(self.RESET)

    def set_sensitivity(self, s=69):
        s = max(min(s, 254), 31)
        self.sens = s
        self.power(True)
        self._set_mode(0x40 | (s >> 5))
        self._set_mode(0x60 | (s & 0x1f))
        self.power(False)

    def get_result(self):
        try:
            data = self.bus.read_word_data(self.address, self.mode)
        except OSError as e:
            raise SensorException(self.SENSOR_NAME, e.strerror) from e
        count = data >> 8 | (data & 0xff) << 8
        coeff = 2 if (self.mode & 0x03) == 0x01 else 1
        ratio = 1 / (1.2 * (self.sens / 69.0) * coeff)
        return ratio * count

    def wait_for_result(self, additional_delay=0):
        basetime = 0.018 if (self.mode & 0x03) == 0x03 else 0.128
        time.sleep(basetime * (self.sens / 69.0) + additional_delay)

    def do_measurement(self, mode, additional_delay=0):
        self.reset()
        self._set_mode(mode)
        self.wait_for_result(additional_delay=additional_delay)
        return self.get_result()

    def set_resolution(self, mode):
        self.resolution = mode

    @property
    def sample(self):
        if not self.data_cache or (datetime.now() - self.data_cache['timestamp']).seconds > self.CACHE_UPDATE_INTERVAL:
            lx = self.do_measurement(self.resolution)
            self.data_cache = {'lx': lx, 'timestamp': datetime.now()}
        return self.data_cache

    @property
    def lx(self):
        return self.sample['lx']