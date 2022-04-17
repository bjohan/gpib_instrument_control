#!/usr/bin/python3
import my_gpib
class Hp6633A(my_gpib.MyGpib):
    def __init__(self, addr=5):
        my_gpib.MyGpib.__init__(self, addr);
        self.checkId()
        self.voltageResolution=0.0125
        self.currentResolution=0.0005
        self.overVoltageResolution=0.25

    def checkId(self):
        st=self.query("ID?")
        if b"HP6633A" in st:
            return True
        if b"HP663" in st:
            print("WARNING, instrument id", st[:-2], "does not completely match HP8633A")
            return True
        raise Exception("Instrument id", st[:-2], "does not match HP8633A")

    def setOvp(self, voltage):
        self.write("OVSET %f"%(voltage))

    def setVoltage(self, voltage):
        self.write("VSET %f"%(voltage))

    def setCurrent(self, current):
        self.write("ISET %f"%(current))

    def getVoltage(self):
        return float(self.query("VOUT?"))
    
    def getCurrent(self):
        return float(self.query("IOUT?"))

    def setOcp(self, enabled):
        if enabled:
            self.write("OCP 1")
        else:
            self.write("OCP 0")

    def resetProtection(self):
        self.write("RST")

    def enableOutput(self, on):
        if on:
            self.write("OUT 1")
        else:
            self.write("OUT 0")




if __name__== "__main__":
    p=Hp6633A()
    print(p.getVoltage())
    print(p.getCurrent())
