import time
import threading
import RPi.GPIO as GPIO

import datetime

from screen import MeteoScreen
from sensor.bme280_sensor import BME280Sensor
from sensor.mhz19_sensor import MHZ19Sensor
from sensor.ze08ch2o_sensor import ZE08CH2OSensor
from sensor.pms5003_sensor import PMS5003Sensor
from sensor.bh1750_sensor import BH1750Sensor
from data_collector import DataCollector
from logger.logger import InMemorySensorDataLogger
from logger.file_logger import ToFileSensorDataLogger


class MeteoPi:

    def __init__(self):
        self.screen = MeteoScreen()
        self.collector = DataCollector()
        self.data = InMemorySensorDataLogger()
        self.collector.add_logger(self.data)
        file_logger = ToFileSensorDataLogger('./db')
        self.collector.add_logger(file_logger)
        now = datetime.datetime.now()
        last24h_data = file_logger.load_data(now - datetime.timedelta(days=1), now)
        self.data.set_data(last24h_data)
        self.screen_update_interval = 10
        self.current_screen_draw = self.draw_screen1
        self.update_timer_stop = threading.Event()
        self.screen_update_lock = threading.RLock()

        def timer():
            while not self.update_timer_stop.is_set():
                time.sleep(self.screen_update_interval)
                self.update_screen()

        self.timer_thread = threading.Thread(target=timer)

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

    def update_screen(self):
        with self.screen_update_lock:
            self.current_screen_draw()

    def start(self):
        self._init_sensors()
        self.screen.draw_countdown_screen(60, 10)
        # self.collector.start()
        self.screen.draw_countdown_screen(10, 0)
        self.draw_screen1()
        self.timer_thread.start()
        # init button switch
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button to GPIO4
        # main loop
        screen_num = 0
        screen_draw = [self.draw_screen1, self.draw_screen2, self.draw_screen3, self.draw_screen4]

        def cleanup():
            GPIO.cleanup()
            self.update_timer_stop.set()
            self.timer_thread.join()

        try:
            while True:
                GPIO.wait_for_edge(4, GPIO.FALLING)
                screen_num = (screen_num + 1) % 4
                with self.screen_update_lock:
                    self.current_screen_draw = screen_draw[screen_num]
                    self.current_screen_draw()
                time.sleep(0.2)
                # button_state = GPIO.input(4)
        except Exception as e:
            cleanup()
            raise e
        cleanup()


if __name__ == '__main__':
    app = MeteoPi()
    app.start()
