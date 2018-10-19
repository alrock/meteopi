import time
import RPi.GPIO as GPIO

from datetime import datetime

from screen import MeteoScreen
from sensor.bme280_sensor import BME280Sensor
from sensor.mhz19_sensor import MHZ19Sensor
from sensor.ze08ch2o_sensor import ZE08CH2OSensor
from sensor.pms5003_sensor import PMS5003Sensor
from sensor.bh1750_sensor import BH1750Sensor
from data_collector import DataCollector
from logger.logger import InMemorySensorDataLogger


class MeteoPi:

    def __init__(self):
        self.screen = MeteoScreen()
        self.collector = DataCollector()
        self.data = InMemorySensorDataLogger()
        self.collector.add_logger(self.data)
        self.screen_update_interval = 60

    def __del__(self):
        self.collector.stop()

    def _init_sensors(self):
        self.collector.add_sensor(BME280Sensor())
        mhz19 = MHZ19Sensor()
        mhz19.abc(False)
        self.collector.add_sensor(mhz19)
        self.collector.add_sensor(ZE08CH2OSensor())
        pms5003 = PMS5003Sensor()
        # pms5003.enable()
        self.collector.add_sensor(pms5003)
        self.collector.add_sensor(BH1750Sensor())

    def draw_screen1(self):
        sensor_name = 'BME280'
        data = self.data.get_data(sensor_name)
        temperature_data = (0, 0)
        humidity_data = (0, 0)
        if sensor_name in data:
            temperature_data = (data[sensor_name]['temperature'], 0)
            humidity_data = (data[sensor_name]['humidity'], 0)
        self.screen.draw_screen1(temperature_data, humidity_data)

    def draw_screen2(self):
        co2_sensor_name = 'MH-Z19'
        data = self.data.get_data(co2_sensor_name)
        co2_data = (0, 0)
        if co2_sensor_name in data:
            co2_data = (data[co2_sensor_name]['co2'], 0)
        ch2o_sensor_name = 'ZE08-CH2O'
        data = self.data.get_data(ch2o_sensor_name)
        ch2o_data = (0, 0)
        if ch2o_sensor_name in data:
            ch2o_data = (data[ch2o_sensor_name]['ch2o'], 0)
        self.screen.draw_screen2(co2_data, ch2o_data)

    def draw_screen3(self):
        sensor_name = 'PMS5003'
        data = self.data.get_data(sensor_name)
        amp10_data = (0, 0)
        amp25_data = (0, 0)
        amp100_data = (0, 0)
        if sensor_name in data:
            amp10_data = (data[sensor_name]['apm10'], 0)
            amp25_data = (data[sensor_name]['apm25'], 0)
            amp100_data = (data[sensor_name]['apm100'], 0)
        self.screen.draw_screen3(amp10_data, amp25_data, amp100_data)

    def draw_screen4(self):
        sensor_name = 'BH1750'
        data = self.data.get_data(sensor_name)
        lx_data = (0, 0)
        if sensor_name in data:
            lx_data = (data[sensor_name]['lx'], 0)
        self.screen.draw_screen4(lx_data)

    def start(self):
        self._init_sensors()
        self.screen.draw_countdown_screen(60, 10)
        self.collector.start()
        self.screen.draw_countdown_screen(10, 0)
        self.draw_screen1()
        last_screen_update = datetime.now()
        # init button switch
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button to GPIO4
        # main loop
        screen_num = 0
        screen_draw = [self.draw_screen1, self.draw_screen2, self.draw_screen3, self.draw_screen4]
        try:
            while True:
                button_state = GPIO.input(4)
                if not button_state:
                    screen_num = (screen_num + 1) % 4
                    screen_draw[screen_num]()
                    time.sleep(0.2)
                else:
                    now = datetime.now()
                    if (now - last_screen_update).seconds >= self.screen_update_interval:
                        last_screen_update = now
                        screen_draw[screen_num]()
        except Exception as e:
            GPIO.cleanup()
            raise e

