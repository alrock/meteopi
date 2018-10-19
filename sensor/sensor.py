class SensorException(Exception):

    def __init__(self, sensor, what):
        self.sensor = sensor
        self.what = what

    def __str__(self):
        return '{0}: {1}'.format(self.sensor, self.what)


class Sensor:

    SENSOR_NAME = ''

    def __init__(self, name):
        self.SENSOR_NAME = name

    @property
    def sample(self):
        raise NotImplementedError
