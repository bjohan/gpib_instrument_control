#!/usr/bin/python3
import my_gpib
import gpib

class Hp5340A(my_gpib.MyGpib):
    def __init__(self, addr=18):
        my_gpib.MyGpib.__init__(self, addr);
        self.write(b'H')
        self.write(b'0')
        self.write(b'P')
        self.write(b'@')
        self.write(b'J')
        self.write(b'L')
        self.write(b'N')
        #self.write(b'H')
        self.write(b'O')
        self.setResolution(4)
        #self.write(b'J')
        #self.write(b'K')
        #self.write(b'@')
        #self.write(b'L')

    def __delete__(self):
        self.write(b'N')


    def setRange(self, range):
        if range == 'check':
            self.setRangeCheck()
        if range == 'low':
            self.setRangeLow()
        if range == 'high':
            self.setRangeHigh()
        if range == 'wide':
            self.setRangeWide()

    def setRangeCheck(self):
        self.write(b'U')

    def setRangeLow(self):
        self.write(b'S')

    def setRangeHigh(self):
        self.write(b'T')

    def setRangeWide(self):
        self.write(b'P')

    def setResolution(self, res):
        resolutions=[b'0', b'1', b'2', b'3', b'4', b'5', b'6']
        self.write(resolutions[res])

    def readSafe(self, readSz, tries=10):
        for a in range(tries):
            #print("Attempting to read try %d of %d"%(a, tries))
            try:
                c=self.read(readSz=readSz)
            except gpib.GpibError as e:
                print(e)
                pass
            else:
                return c
        raise IOError("Unable to read gpib after %d tries"%(tries))

    def recoverPosition(self):
        while True:
            c = self.readSafe(readSz=1)
            if c == b'\n':
                break

    def readValue(self):
        #self.write(b'H')
        try:
            c=self.readSafe(readSz=16)
        except gpib.GpibError:
            self.recoverPosition()
            return self.readValue()
        data=c.decode('utf-8')
        try:
             v= float(data[2:-2])
        except:
            self.recoverPosition()
            return self.readValue()
        return v

if __name__ == '__main__':
    instr = Hp5340A()
    #instr.write(b'@')
    #instr.write(b'J')
    #instr.write(b'L')
    #instr.setResolution(6)
    #instr.setRangeCheck()
    #while True:
    print(instr.readValue())
