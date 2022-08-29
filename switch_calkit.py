import serial

class SwitchCalkit:
    def __init__(self, device, serialPortPath=None):
        if serialPortPath is None:
            self.device = device
        else:
            self.device=serial.Serial(serialPortPath, 115200)

    def s(self):
        self.device.write(b'S')

    def o(self):
        self.device.write(b'O')

    def l(self):
        self.device.write(b'L')

    def t(self):
        self.device.write(b'T')

    def a(self):
        self.device.write(b'A')

    def b(self):
        self.device.write(b'B')

