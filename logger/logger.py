import threading

from datetime import datetime


class SensorDataLogger:

    def log(self, sensor, sample):
        raise NotImplementedError


class InMemorySensorDataLogger(SensorDataLogger):

    def __init__(self, seconds=86400):
        self.seconds = seconds
        self.data = {}
        self.data_lock = threading.RLock()

    @staticmethod
    def remove_outdated(samples, seconds):
        now = datetime.now()
        first = 0
        while first < len(samples):
            if (now - samples[first]['timestamp']).seconds < seconds:
                break
            first += 1
        if first > 0:
            del samples[0:first]

    def log(self, sensor, sample):
        with self.data_lock:
            samples = self.data.get(sensor, [])
            samples.append(sample)
            self.remove_outdated(samples, self.seconds)
            self.data[sensor] = samples

    def get_data(self, sensors=None, timestamp=None):
        if isinstance(sensors, str):
            sensors = (sensors,)
        data = {}
        with self.data_lock:
            sensors = sensors or self.data.keys()
            timestamp = timestamp or datetime.now()
            for sensor in sensors:
                samples = self.data.get(sensor, [])
                for sample in reversed(samples):
                    if sample['timestamp'] <= timestamp:
                        data[sensor] = sample
                        break
        return data

    def set_data(self, data):
        for sensor, samples in data.items():
            for sample in samples:
                self.log(sensor, sample)
