#!/usr/bin/python3
import my_gpib
import aux
#sys.path.append("/usr/lib/python3.1/site-packages/")
import gpib

class Hp3478A(my_gpib.MyGpib):
    def __init__(self, addr=23):
        my_gpib.MyGpib.__init__(self, addr);

    def setNumDigits(self, nd):
        aux.checkParam(nd, [3, 4, 5], "Failed to set number of digits")
        self.ifc()
        self.write("N%d"%(nd))


    def setRange(self, r):
        aux.checkParam(r, [-2, -1, 0, 1, 2, 3, 4, 5, 6, 7], "Failed to set range")
        self.ifc()
        self.write("R%d"%(r))

    def readValue(self):
        for i in range(5):
            data=''
            self.ifc()
            try:
                while True:
                    c= self.read(readSz=1)
                    if c is not None:
                        data+=c.decode('utf-8')
                        if c == b'\n':
                            break
                return float(data)
            except gpib.GpibError:
                pass
            except ValueError:
                pass


if __name__ == "__main__":
    m=Hp3478A()
    print("Read value:", m.readValue())
