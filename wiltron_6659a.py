#!/usr/bin/python3
import my_gpib

class Wiltron6659A(my_gpib.MyGpib):
    def __init__(self, addr=19):
        my_gpib.MyGpib.__init__(self, addr);

    def setLevel(self, level):
        self.write(b'LVL%2.2fDM'%(level))

    def setCwMode(self):
        self.write(b'CF0')

    def setCwFreq(self, f):
        self.write(b'F0%.2fMH'%(f/1e6))

if __name__ == '__main__':
    instr = Wiltron6659A()
    instr.setLevel(3.3)
    instr.setCwMode()
    instr.setCwFreq(12.345678e9)
