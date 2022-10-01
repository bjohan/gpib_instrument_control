#!/usr/bin/python3
import my_gpib


class TtiCpx400DpChannel:
    def __init__(self, parent, num):
        self.parent=parent
        self.num=num

    def set(self, cmdFmt, value):
        self.parent.write(cmdFmt%(self.num, value))

    def get(self, cmdFmt, skipUnit=False):
        resp = self.parent.query(cmdFmt%(self.num))
        v = resp.split(b' ')[-1].strip()
        if skipUnit:
            v=v[0:-2]
        return float(v.strip())

    def setVoltage(self, v):
        self.set('V%d %f', v);

    def getVoltage(self):
        return self.get(b'V%d?')

    def setCurrentLimit(self, v):
        self.set('I%d %f', v);

    def getCurrentLimit(self):
        return self.get(b'I%d?')

    def getVoltageOutput(self):
        return self.get(b'V%dO?', skipUnit=True)

    def getCurrentOutput(self):
        return self.get(b'I%dO?', skipUnit=True)

    def enableOutput(self, on):
        if on:
            self.set("OP%d %d", 1)
        else:
            self.set("OP%d %d", 0)

class TtiCpx400Dp(my_gpib.MyGpib):
    def __init__(self, addr=11):
        my_gpib.MyGpib.__init__(self, addr, verbose=False)
        ver=self.query('*IDN?')
        if b'CPX400DP' not in ver:
            raise ValueError('Not a tti CPX400DP at gpib addr %'%(addr))
        self.ch = [TtiCpx400DpChannel(self, 1), TtiCpx400DpChannel(self, 2)];

if __name__ == '__main__':
    print("Creating instrument")
    psu=TtiCpx400Dp()
    print("Setting setVoltage")
    psu.ch[0].setVoltage(1.23)
    print("Getting voltage");
    print(psu.ch[1].getVoltage())

    print("Setting current limit")
    psu.ch[0].setCurrentLimit(0.56)

    print("Get current limit")
    print(psu.ch[1].getCurrentLimit())

    print("Get output voltage")
    print(psu.ch[1].getVoltageOutput())

    print("Get output current")
    print(psu.ch[1].getCurrentOutput())
