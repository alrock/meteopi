import time

from PIL import ImageFont

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306


class MeteoScreen:

    DEGREE_SYMBOL = u'\u00B0'
    ARROW_UP_SYMBOL = u'\u2191'
    ARROW_DOWN_SYMBOL = u'\u2193'

    def __init__(self):
        # init device
        serial = i2c(port=1, address=0x3C)
        self.device = ssd1306(serial, width=128, height=32, rotate=0)

        # init fonts
        font_path = '/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf'
        self.font = ImageFont.truetype(font_path, 16)
        self.font_medium = ImageFont.truetype(font_path, 12)
        self.font_small = ImageFont.truetype(font_path, 8)

    def draw_countdown_screen(self, from_sec, to_sec):
        while from_sec > to_sec:
            with canvas(self.device) as draw:
                draw.text((0, 0), 'Starting...', fill="white", font=self.font)
                draw.text((0, 16), '{0}sec. left'.format(from_sec), fill="white", font=self.font)
            from_sec -= 1
            time.sleep(1)

    def _growth(self, param):
        return ' ' if param[1] == 0 else (self.ARROW_UP_SYMBOL if param[1] else self.ARROW_DOWN_SYMBOL)

    def draw_screen1(self, temperature, humidity):
        """
        Draws the specified temperature and humidity on the screen.
        :param temperature: tuple of size two, where first value is temperature and second value is growth direction
                            (<0 if temperature is getting down, 0 if no changes, >0 if it growth)
        :param humidity: tuple of size two, same as temperature
        """
        with canvas(self.device) as draw:
            draw.text((0, 0), 'T:{0: 3}{1} {2}'.format(int(temperature[0]), self.DEGREE_SYMBOL,
                                                       self._growth(temperature)), fill="white", font=self.font)
            draw.text((0, 16), 'H:{0: 3}% {1}'.format(int(humidity[0]),
                                                      self._growth(humidity)), fill="white", font=self.font)

    def draw_screen2(self, co2, ch2o):
        """
        Draws the specified temperature and humidity on the screen.
        :param co2: tuple of size two, where first value is co2 concentration and second value is growth direction
                    (<0 if co2 is getting down, 0 if no changes, >0 if it growth)
        :param ch2o: tuple of size two, same as co2
        """
        with canvas(self.device) as draw:
            draw.text((0, 0), ' CO2:{0: 5} {2}'.format(int(co2[0]), self.DEGREE_SYMBOL, self._growth(co2)),
                      fill="white", font=self.font)
            draw.text((0, 16), 'CH2O:{0: 5} {1}'.format(int(ch2o[0]), self._growth(ch2o)), fill="white", font=self.font)

    def draw_screen3(self, apm10, apm25, apm100):
        """
        Draws the specified temperature and humidity on the screen.
        :param apm10: tuple of size two, where first value is PM1.0 dust and second value is growth direction
                    (<0 if PM1.0 is getting down, 0 if no changes, >0 if it growth)
        :param apm25: tuple of size two, same as apm10
        :param apm100: tuple of size two, same as apm10
        """
        with canvas(self.device) as draw:
            draw.text((0, 0), ' PM1.0:{0: 4} {2}'.format(int(apm10[0]), self.DEGREE_SYMBOL, self._growth(apm10)),
                      fill="white", font=self.font)
            draw.text((0, 16), ' PM2.5:{0: 4} {2}'.format(int(apm25[0]), self.DEGREE_SYMBOL, self._growth(apm25)),
                      fill="white", font=self.font)

    def draw_screen4(self, lx):
        with canvas(self.device) as draw:
            draw.text((0, 0), 'Lx:{0: 4} {2}'.format(int(lx[0]), self.DEGREE_SYMBOL, self._growth(lx)),
                      fill="white", font=self.font)
