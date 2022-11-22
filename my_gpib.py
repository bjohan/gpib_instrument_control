#!/usr/bin/python3
import sys
sys.path.append("/usr/lib/python3.8/site-packages/")
import gpib

class MyGpib:
    def __init__(self, sad, pad=0, defaultReadSize=8192, verbose=False):
        self.con = gpib.dev(pad, sad);
        gpib.timeout(self.con, gpib.T1000s)
        self.defaultReadSize = defaultReadSize
        self.verbose=verbose


    def verbosePrint(self, s, nl=True):
        if self.verbose:
            if nl :
                print(s)
            else:
                print(s, end='', flush=True)

    def lines(self):
        return gpib.lines(0)

    def getHsDict(self):
        d={}
        ls = self.lines()

        if ls & gpib.ValidDAV:
            d['DAV']=ls&gpib.BusDAV

        if ls & gpib.ValidNDAC:
            d['NDAC']=ls&gpib.BusNDAC

        if ls & gpib.ValidNRFD:
            d['NRFD']=ls&gpib.BusNRFD

        if ls & gpib.ValidIFC:
            d['IFC']=ls&gpib.BusIFC

        if ls & gpib.ValidREN:
            d['REN']=ls&gpib.BusREN

        if ls & gpib.ValidSRQ:
            d['SRQ']=ls&gpib.BusSRQ

        if ls & gpib.ValidATN:
            d['ATN']=ls&gpib.BusATN

        if ls & gpib.ValidEOI:
            d['EOI']=ls&gpib.BusEOI


        return d


    def testSrq(self):
        return self.lines()&gpib.BusSRQ

    def ifc(self):
        self.verbosePrint("IFC")
        return gpib.interface_clear(0)

    def clear(self):
        self.verbosePrint("IFC")
        return gpib.clear(self.con)

    def read(self, readSz=None):
        rstr="R: "
        if readSz is not None:
            rstr="R(%d): "%(readSz)
        self.verbosePrint(rstr, nl=False)
        for i in range(5):
            try:
                if readSz is not None:
                    data = gpib.read(self.con, readSz)
                else:
                    data = gpib.read(self.con, self.defaultReadSize)
                #print('read: "'+str(data)+'"')
                self.verbosePrint(str(data))
                return data
            except gpib.GpibError:
                pass

    def write(self, data):
        self.verbosePrint("W: "+str(data))
        gpib.write(self.con, data);

    def query(self, data, readSz=None):
        self.write(data);
        return self.read(readSz=readSz);


    def opc(self):
        return self.query("*OPC?");
