import pigpio


class SerialReader:

    def __init__(self, pi, rx):
        self.pi = pi
        self.rx = rx
        pigpio.exceptions = False
        self.pi.bb_serial_read_close(self.rx)
        pigpio.exceptions = True
        self.pi.bb_serial_read_open(self.rx, 9600, 8)
        self.data = b''

    def __del__(self):
        pigpio.exceptions = False
        self.pi.bb_serial_read_close(self.rx)
        pigpio.exceptions = True

    def read(self, n):
        while len(self.data) < n:
            sz, dat = self.pi.bb_serial_read(self.rx)
            if sz > 0:
                self.data = self.data + dat
            elif sz < 0:
                pass
        res = self.data[0:n]
        self.data = self.data[n:]
        return res
