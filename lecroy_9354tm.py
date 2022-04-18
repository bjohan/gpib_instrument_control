#!/usr/bin/python3
import my_gpib
import aux
import struct
import numpy as np


class Lecroy9354Tm(my_gpib.MyGpib):
    def __init__(self, addr=4, reset=False, verbose=False):
        my_gpib.MyGpib.__init__(self, addr, verbose=verbose);
        self.checkIdn()
        if verbose:
            print("Instrument ID ok")
        if reset:
            print("Resetting instrument")
            self.reset()

    def idn(self):
        return self.query("*IDN?");

    def checkIdn(self):
        refIdn = b'*IDN LECROY,9354TM,935402378,08.2.2\n'
        s=self.idn()
        if s == refIdn:
            return
        if b"LECROY,93" in s:
            print("WARNING, idn", s, "does not match driver exactly", refIdn);
            return
        raise Exception("Instrumtn idn %s does not match driver %s"%(s, refIdn))


    def reset(self):
        self.write("*RST;*OPC?")
        self.read()


    def parseWaveDesc(self, d):
        di={}
        di['descriptorName'] = d[:16] #Byte 0-15
        di['templateName'] = d[16:32] #Byte 16-31
        #d = d[4:] #skip byte 32-35
        di['descriptorLength'] = struct.unpack(">I", d[36:40])[0] #byte 36-39
        #d = d[76-16-16-4-4:] #skip byte 40-75
        di['waveArrayLength'] = struct.unpack(">I", d[60:64])[0] #byte 60-63
        di['instrumentName'] = d[76:92] #byte 76-91
        di['waveArrayCount'] = struct.unpack(">I", d[116:120])[0] #byte 116-119
        sampleStart=di['descriptorLength'];
        numSamples=di['waveArrayCount']
        sampleEnd=sampleStart+numSamples*2;
        di['samples']=struct.unpack(">"+"h"*numSamples, d[sampleStart:sampleEnd])
        di['verticalGain'] = struct.unpack(">f", d[156:160])[0] 
        di['verticalOffset'] = struct.unpack(">f", d[160:164])[0] 
        di['verticalUnit'] = chr(d[196])
        di['horizontalInterval']= struct.unpack(">f", d[176:180])[0]
        di['horizontalOffset'] = struct.unpack(">d", d[180:188])[0]
        di['horizontalUnit'] = chr(d[244])
        return di


    def parseWaveformData(self, d):
        di={}
        di['queryResponse'], d = d[:10], d[10:]
        di['fooData'], d = d[:2], d[2:]
        di['length'], d = int(d[:9]), d[9:]
        di['waveDesc'] = self.parseWaveDesc(d)
        return di

    def extractTrace(self, di, name):
        samples=np.array(di['waveDesc']['samples'])
        vg=di['waveDesc']['verticalGain']
        vo=di['waveDesc']['verticalOffset']
        hi=di['waveDesc']['horizontalInterval']
        ho=di['waveDesc']['horizontalOffset']
        xunit=di['waveDesc']['horizontalUnit']
        yunit=di['waveDesc']['verticalUnit']
        y=samples*vg-vo;
        x=np.arange(len(samples))*hi+ho
        return aux.Trace(x, y, xunit, yunit, name=name)
        

    def getWaveform(self, wf='TA'):
        aux.checkParam(wf, ["TA", "TB", "TC", "TD", "C1", "C2", "C3", "C4"], "Not a valid waveform")
        d=self.query("%s:WF?"%(wf), readSz=32768*16)
        wd=self.parseWaveformData(d)
        return self.extractTrace(wd, wf)

    def setVdiv(self, ch, vdiv):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4"], "Not a valid channel")
        self.write('%s:VDIV %f'%(ch, vdiv))

    def setTdiv(self, tdiv):
        self.write("TDIV %f"%(tdiv))

    def setCoupling(self, ch, coupling):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid channel")
        aux.checkParam(coupling, ["D1M","A1M","D50","GND"], "Not a valid coupling")
        self.write("%s:CPL %s"%(ch, coupling))

    def getCoupling(self, ch):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid channel")
        return self.query("%s:CPL?"%(ch))

    def setAttenuation(self, ch, coupling):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid channel")
        aux.checkParam(coupling, [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 10000], "attenuation")
        self.write("%s:ATTN %s"%(ch, coupling))

    def getAttenuation(self, ch):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid channel")
        return self.query("%s:ATTN?"%(ch))

    def setOffset(self, ch, voff):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4"], "Not a valid channel")
        self.write('%s:OFST %f'%(ch, voff))

    def getOffset(self, ch):
        aux.checkParam(ch, ["C1", "C2", "C3", "C4"], "Not a valid channel")
        return self.query('%s:OFST?'%ch)

    def setTrigCoupling(self, src, cpl):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        aux.checkParam(cpl, ['AC', 'DC', 'HFREJ', 'LFREJ', 'AUTO'], "Invalid coupling type")
        self.write("%s:TRCP %s"%(src, cpl))

    def getTrigCoupling(self, src):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        return self.query("%s:TRCP?"%(src))

    def setTrigDelayTime(self, dly):
        self.write("TRDL %fS"%(dly))
    
    def setTrigDelayPct(self, pct):
        if pct < 0.0 or pct > 100.0:
            raise ValueError("trigger delay in percent must be more than 0 and less than 100")
        self.write("TRDL %fPCT"%(pct))

    def getTrigDelay(self):
        return self.query("TRDL?")

    def setTrigLevel(self, src, lvl):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        self.write("%s:TRLV %f"%(src, lvl))

    def getTrigLevel(self, src):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        return self.query("%s:TRLV?"%(src))

    def setTrigMode(self, mode):
        aux.checkParam(mode, ['AUTO', 'NORM', 'SINGLE', 'STOP'], "Not a valid trigger mode")
        self.write("TRMD %s"%(mode))

    def getTrigMode(self):
        return self.query("TRMD?")


    def setTrigSlope(self, src, slope):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        aux.checkParam(slope, ["NEG", "POS"], "Not a valid slope")
        self.write("%s:TRSL %s"%(src, slope))

    def getTrigSlope(self, src):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        return self.query("%s:TRSL?"%(src))

    def setTrigSource(self, src, trigType="EDGE"):
        aux.checkParam(src, ["C1", "C2", "C3", "C4", "EX", "EX10"], "Not a valid trigger source")
        aux.checkParam(trigType, ["STD", "SNG", "SQ", "TEQ", "DROP", "EDGE", "GLIT", "INTV", "PA", "TV"], "Not a valid trig type")
        self.write("TRSE %s,SR,%s"%(trigType, src))

    def getTrigSource(self):
        return self.query("TRSE?")

if __name__ == "__main__":
    s=Lecroy9354Tm(verbose=False)
    s.setVdiv('C1', 0.002)
    s.setVdiv('C2', 5)
    s.setVdiv('C3', 1)
    s.setVdiv('C4', 2)
    s.setOffset('C1', -0.003)
    s.setTdiv(0.0005)
    s.setTrigDelayPct(50)
    s.setTrigSource("C1")
    s.opc()
    print("trig delay", s.getTrigDelay())
    print("trig coupling", s.getTrigCoupling('C1'))
    print("trig clevel", s.getTrigLevel('C1'))
    print("trig mode", s.getTrigMode())
    print("trig slope", s.getTrigSlope('C1'))
    print("trig source", s.getTrigSource())
    for tn in ["C1", "C2", "C3", "C4"]:
        s.setCoupling(tn, "A1M")
        s.setAttenuation(tn, 1)
        s.opc()
        print("get");
        t = s.getWaveform(wf=tn)
        t.draw()
        print("coupling", tn, s.getCoupling(tn), end='\t')
        print("attenuation", tn, s.getAttenuation(tn), end='\t')
        print("offset", tn, s.getOffset(tn))
    t.show()


