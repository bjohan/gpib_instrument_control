#!/usr/bin/python3
import my_gpib
import time
import gpib
import aux

class RacalDana6000(my_gpib.MyGpib):
    def __init__(self, addr=1):
        my_gpib.MyGpib.__init__(self, addr);
    

    def setRange(self, r):
        aux.checkParam(r, range(10), "Failed to set range")
        self.write("R%d"%(r))

    def setNumDigits(self, nd):
        aux.checkParam(nd, [4, 5, 6], "Set number of digits failed")
        m={4:'I2', 5:'I4', 6:'I5'}
        self.write(m[nd])

    def setIntegrationTime(self, it):
        times={0.0:'I0', 0.0016:'I1', 0.004:'I2', 0.016:'I3', 0.04:'I4', 0.1:'0.1'}
        aux.checParam(it, times, "Failed to set integration time");
        self.write(times[it])

    def enableFilter(self, on):
        if on:
            self.write('J1')
        else:
            self.write('J0')

    def readValue(self):
        data=''
        while True:
            try:
                c= self.read(readSz=1)
                data+=c.decode('utf-8')
                if c == b'\n':
                    break
            except gpib.GpibError:
                time.sleep(1)
        if '++' in data:
            data=data.replace('++', '+')
        if '--' in data:
            data=data.replace('--', '-')
        if len(data) < 4:
            return readValue();
        try:
            v = float(data)
        except ValueError:
            time.sleep(2)
            return self.readValue()
        return v

if __name__ == "__main__":
    m=RacalDana6000()
    print("Read value:", m.readValue())
