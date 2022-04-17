#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/python3.8/site-packages/")
import gpib

class MyGpib:
    def __init__(self, sad, pad=0, defaultReadSize=8192):
        self.con = gpib.dev(pad, sad);
        gpib.timeout(self.con, gpib.T1000s)
        self.defaultReadSize = defaultReadSize

    def ifc(self):
        return gpib.interface_clear(0)

    def clear(self):
        return gpib.clear(self.con)

    def read(self, readSz=None):
        for i in range(5):
            try:
                if readSz is not None:
                    data = gpib.read(self.con, readSz)
                else:
                    data = gpib.read(self.con, self.defaultReadSize)
                #print('read: "'+str(data)+'"')
                return data
            except gpib.GpibError:
                pass

    def write(self, data):
        gpib.write(self.con, data);

    def query(self, data, readSz=None):
        self.write(data);
        return self.read(readSz=readSz);

