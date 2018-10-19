import re
import os
import copy
import datetime

from tinydb import TinyDB, Query

from logger.logger import SensorDataLogger


class ToFileSensorDataLogger(SensorDataLogger):

    def __init__(self, path):
        self.path = path
        self.current_date = None
        self.db = None

    @staticmethod
    def remove_outdated(path, date):
        for file in os.listdir(path):
            res = re.match('sensordata(\d{4})-(\d{2})-(\d{2})\.json', file)
            if res:
                file_date = datetime.date(int(res.group(1)), int(res.group(2)), int(res.group(3)))
                if file_date < date:
                    os.remove(os.path.join(path, file))

    @staticmethod
    def generate_file_name(path, date):
        filename = 'sensordata{0}.json'.format(date.isoformat())
        return os.path.join(path, filename)

    @staticmethod
    def serialize_sample(sample):
        s = copy.deepcopy(sample)
        s['timestamp'] = s['timestamp'].timestamp()
        return s

    @staticmethod
    def deserialize_sample(sample):
        sample['timestamp'] = datetime.fromtimestamp(sample['timestamp'])
        return sample

    @staticmethod
    def db_exists(path, date):
        return os.path.isfile(ToFileSensorDataLogger.generate_file_name(path, date))

    def open_db(self, date):
        if self.db:
            self.db.close()
        self.db = TinyDB(self.generate_file_name(self.path, date))
        self.current_date = date

    def load_data(self, from_timestamp, to_timestamp):
        from_date = from_timestamp.date()
        to_date = to_timestamp.date()
        data = {}
        while from_date <= to_date:
            if self.db_exists(self.path, from_date):
                with TinyDB(self.generate_file_name(self.path, from_date)) as db:
                    for name in db.tables():
                        table = db.table(name)
                        q = Query()
                        res = table.search((q.timestamp >= from_timestamp.timestamp()) &
                                           (q.timestamp <= to_timestamp.timestamp()))
                        samples = data.get(name, [])
                        samples.append(res)
                        data[name] = samples
            from_date += datetime.timedelta(days=1)

    def log(self, sensor, sample):
        sample_date = sample['timestamp'].date()
        if sample_date != self.current_date:
            self.open_db(sample_date)
            self.remove_outdated(sample_date - datetime.timedelta(days=2))
        table = self.db.table(sensor)
        table.insert(self.serialize_sample(sample))


if __name__ == '__main__':
    logger = ToFileSensorDataLogger('.')
    logger.log('TEST_SENSOR', {'temperature': 'cold', 'timestamp': datetime.now()})
    #print(logger.get_day(datetime.now().date()))
