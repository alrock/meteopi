import threading
import time

from datetime import datetime

from sensor.sensor import Sensor, SensorException
from logger.logger import SensorDataLogger


class DataCollector(threading.Thread):

    def __init__(self):
        super().__init__()
        self.sensors = {}
        self.loggers = []
        self.stop_flag = False

    def add_sensor(self, sensor, interval=10):
        if not isinstance(sensor, Sensor):
            raise TypeError('Object should be an instance of type Sensor')
        self.sensors[sensor.SENSOR_NAME] = {'sensor': sensor, 'interval': int(interval), 'last_update': None}

    def add_logger(self, logger):
        if not isinstance(logger, SensorDataLogger):
            raise TypeError('Object should be an instance of type SensorDataLoggers')
        self.loggers.append(logger)

    def notify_loggers(self, sensor, sample):
        for logger in self.loggers:
            logger.log(sensor, sample)

    def run(self):
        while not self.stop_flag:
            for sensor, value in self.sensors.items():
                last_update = value['last_update']
                now = datetime.now()
                if not last_update or (now - last_update).seconds >= value['interval']:
                    value['last_update'] = now
                    try:
                        sample = value['sensor'].sample
                        self.notify_loggers(sensor, sample)
                    except SensorException as e:
                        print(e)
            time.sleep(1)

    def stop(self):
        if self.is_alive():
            self.stop_flag = True
            self.join()
            self.stop_flag = False
