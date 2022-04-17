#!/usr/bin/python3
import my_gpib
import gpib
import gpib
import time
import numpy as np
import scipy.io as sio
import struct
import matplotlib.pyplot as plt
import skrf.network
from aux import checkParam
import tqdm

class Hp8753A(my_gpib.MyGpib):
    def __init__(self, addr=17):
        my_gpib.MyGpib.__init__(self, addr);
        idStr=self.query("*IDN?")
        refStr=b'HEWLETT PACKARD,8753A,0,1.00\n'
        refStr=b'HEWLETT PACKARD,8703A,0,1.00\n'
        if idStr!=refStr:
            if "8753" not in idStr:
                raise Exception("Instrument att address {addr} does not seem to be a 8753")
            else:
                print("Warning, IDN response does not completely match")

    def write(self, data):
        for i in range(5):
            try:
                self.ifc()
                my_gpib.MyGpib.write(self, data)
                return
            except gpib.GpibError:
                pass

    def reset(self):
        self.write('OPC?;*RST;')

    def preset(self):
            self.write('OPC?;PRES;');

    def getStateString(self):
        return self.query("*LRN?");

    def setStateString(self, string):
        self.write(string)

    def readTrace(self):
        self.write("FORM2;")
        data=self.query("OUTPFORM;", readSz=2000*8)
        header=data[0:2];
        length=int.from_bytes(data[2:4], "big")
        valueData=data[4:]
        #print(valueData)
        if length!=len(valueData):
            raise Exception("Unable to read all data got %d of %d"%(len(valueData, length)))
        d = [struct.unpack('>f', data[i:i+4])[0] for i in range(4, len(data),8)]
        return d

    def readComplexTraceData(self):
        self.write('LINM')
        real = self.readTrace()
        self.write('PHAS')
        imag = self.readTrace()
        self.write('LOGM')
        return np.array(real)*np.exp(np.array(imag)*1j*np.pi/180.0)


    def setSParameter(self, param):
        checkParam(param.upper(), ['S11', 'S12', 'S21', 'S22'], 'Invalid S-paramter')
        self.write(param.upper()+';')

    def readSParameter(self, param):
        #print("Measuring", param)
        self.setSParameter(param)
        #self.write(param+';')
        self.write('OPC?;SING;')
        self.read()
        return self.readComplexTraceData()


    def readSParameters(self):
        s11=self.readSParameter('S11')
        s21=self.readSParameter('S21')
        s12=self.readSParameter('S12')
        s22=self.readSParameter('S22')
        return s11, s12, s21, s22

    def sParametersToNetwork(self, f, s11, s12, s21, s22):
        return skrf.network.Network(f=f/1e9, s=mergeVectorsToSparam(s11, s12, s21, s22), z0=[50,50])

    def getScikitRfNetworkSparameters(self):
        params=['S11', 'S21', 'S12', 'S22']
        values=[]

        for par in tqdm.tqdm(params):
            values.append(self.readSParameter(par))
        s11=values[0]
        s21=values[1]
        s12=values[2]
        s22=values[3]
        return skrf.network.Network(f=self.frequencies()/1e9, s=mergeVectorsToSparam(s11, s12, s21, s22), z0=[50,50])

    def setStartFrequency(self, f):
        self.write('STAR %f'%(f))

    def setStopFrequency(self, f):
        self.write('STOP %f'%(f))

    def startFrequency(self):
        return float(self.query("STAR?;"))

    def stopFrequency(self):
        return float(self.query("STOP?;"))

    def frequencyPoints(self):
        return int(float(self.query("POIN?;")))

    def frequencies(self):
        return np.linspace(self.startFrequency(), self.stopFrequency(), self.frequencyPoints())

    def cw(self, freq):
        self.write('CWFREQ  %d;'%(freq))

    def chan(self, ch):
        checkParam(ch, [1, 2], 'Invalid channel number')
        self.write('OPC?;CHAN%d;');
        self.read()

    def wait(self):
        self.write('OPC?;WAIT;')
        self.read()

    def outputPower(self, level):
        checkParam(level, [5, 0, -5, -10, -15, -20, -25, -30, -35, -40, -45, -50], 'Invalid power level')
        self.write('POWE %d'%(level))

    def continous(self):
        self.write("CONT;");

    def setPoints(self, numpoints):
        checkParam(numpoints, [3, 11, 21, 51, 101, 201, 401, 801, 1601], 'Invalid number of points');
        self.write('POIN %d;'%(numpoints));

    def __delete__(self):
        pass

    def roundUpToValidPoints(self,p):
        vp = [3, 11, 21, 51, 101, 201, 401, 801, 1601]
        for v in vp:
            if v >= p:
                return v
        return 1601


    def getHighResolutionSparameters(self, fstart, fstop, fres=1e6):
        f=np.linspace(fstart, fstop, int((fstop-fstart)/fres)+1)
        flist=f
        ss11=np.array(());
        ss12=np.array(());
        ss21=np.array(());
        ss22=np.array(());
        mf=np.array(());
        while True:
            if len(flist) < 2:
                break
            nel=len(flist)
            if nel > 1601:
                nel=1601;
            fs=flist[0:nel]
            flist=flist[nel:]
            self.setStartFrequency(np.min(fs))
            self.setStopFrequency(np.max(fs))
            self.setPoints(self.roundUpToValidPoints(nel))

            t11,t12,t21,t22=self.readSParameters();
            ss11=np.concatenate([ss11, t11]);
            ss12=np.concatenate([ss12, t12]);
            ss21=np.concatenate([ss21, t21]);
            ss22=np.concatenate([ss22, t22]);
            mf=np.concatenate([mf, self.frequencies()])
        f=mf
        self.setStartFrequency(fstart)
        self.setStopFrequency(fstop)
        self.continous()
        return f, ss11, ss12, ss21, ss22

    def getHighResolutionNetwork(self, fstart, fstop, fres=1e6):
        f, s11, s12, s21, s22 = self.getHighResolutionSparameters(fstart, fstop, fres=fres)
        return self.sParametersToNetwork(f, s11, s12, s21, s22)
 
def mergeVectorsToSparam(vs11, vs12, vs21, vs22):
    ss = []
    for s11, s12, s21, s22 in zip(vs11, vs12, vs21, vs22):
        s=np.array([[s11, s12], [s21, s22]])
        ss.append(s)
    return np.stack(ss)

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Make measurements using HP 8753A')
    parser.add_argument('-pres', '--preset-instrument', action='store_true', help='Preset instrument state before doing anything else')
    parser.add_argument('-ss', '--save-state', type=argparse.FileType('wb'), help='Write instrument status (output from *LRN?) to file')
    parser.add_argument('-ls', '--load-state', type=argparse.FileType('rb'), help='Read instrument status from file and write back to instrument')
    parser.add_argument('-hdr', '--high-dynamic-range', action='store_true', help='Set up VNA for accurate reading with high dynamic range');
    parser.add_argument('-wtf', '--write-touchstone-file', type=argparse.FileType('wb'), help='Write measured data in touchstone format to specified file')
    parser.add_argument('-wmf', '--write-matlab-file', type=argparse.FileType('wb'), help='Write measured data in matlab format to specified file')
    parser.add_argument('-od', '--open-deembed', type=argparse.FileType('rb'), help='Use s11/2 and s22/2 from specified touchstone file to deembed s11 and s22 measurements');
    parser.add_argument('-td', '--through-deembed', type=argparse.FileType('rb'), help='Use s21 and s12 from specified touchstone file to deembed s12 and s21 measurements');
    parser.add_argument('-hfr', '--high-frequency-resolution', action='store_true', help='Divide band in to subbands to set frequency resolution to 1MHz')
    parser.add_argument('-p', '--plot', action='store_true', help='Show plot of measured parameters');
    instr = Hp8753A()

    pa=parser.parse_args()
    if pa.preset_instrument:
        instr.reset()
        instr.preset()

    if pa.high_dynamic_range:
        instr.write('POIN 1601;')
        instr.write('IFBW10Hz;')
    if pa.save_state:
        pa.save_state.write(instr.getStateString())

    if pa.load_state:
        instr.setStateString(pa.load_state.read())

    if pa.open_deembed:
        print("using", pa.open_deembed.name, 'to deembed s11 and s22');
        de=skrf.network.Network(file=pa.open_deembed.name)

    if pa.through_deembed:
        td=skrf.network.Network(file=pa.through_deembed.name)


    if pa.high_frequency_resolution:
        fres=1e6;
        f=instr.frequencies()
        fstart=np.min(f)
        fstop=np.max(f)
        f=np.linspace(fstart, fstop, int((fstop-fstart)/fres)+1)
        flist=f
        instr.write('POIN 1601;')
        ss11=np.array(());
        ss12=np.array(());
        ss21=np.array(());
        ss22=np.array(());
        mf=np.array(());
        while True:
            print("Frequencies remaining", len(flist));
            if len(flist) < 2:
                break
            nel=len(flist)
            if nel > 1601:
                nel=1601;
            fs=flist[0:nel]
            flist=flist[nel:]
            instr.setStartFrequency(np.min(fs))
            instr.setStopFrequency(np.max(fs))
            t11,t12,t21,t22=instr.readSParameters();
            print(t11)
            ss11=np.concatenate([ss11, t11]);
            ss12=np.concatenate([ss12, t12]);
            ss21=np.concatenate([ss21, t21]);
            ss22=np.concatenate([ss22, t22]);
            mf=np.concatenate([mf, instr.frequencies()])
            print(len(ss11))
        f=mf
        instr.setStartFrequency(fstart)
        instr.setStopFrequency(fstop)
    else:
        f=instr.frequencies()
        ss11, ss12, ss21, ss22 = instr.readSParameters()
    instr.continous()
    #for s11, s12, s21, s22 in zip(ss11, ss12, ss21, ss22):
    #    s=np.array([[s11, s12], [s21, s22]])
    #    ss.append(s)
    #sm=np.stack(ss)


    if pa.open_deembed:
        des11=np.squeeze(de.s11.s)
        des22=np.squeeze(de.s22.s)
        ss11=ss11/des11
        ss22=ss22/des22


    if pa.through_deembed:
        des21=np.squeeze(td.s21.s)
        des12=np.squeeze(td.s12.s)
        ss21=ss21/des21
        ss12=ss12/des12


    n = skrf.network.Network(f=f/1e9, s=mergeVectorsToSparam(ss11, ss12, ss21, ss22), z0=[50,50])
    if pa.write_touchstone_file:
        print("Writing s-parameters to ", pa.write_touchstone_file.name)
        n.write_touchstone(pa.write_touchstone_file.name)
    if pa.write_matlab_file:
        sio.savemat(pa.write_matlab_file.name, {'f':f, 'S11':ss11, 'S12':ss12, 'S21':ss21, 'S22':ss22});
    if pa.plot:
        n.plot_s_db()
        #n.plot_s_deg()
        plt.grid()
        plt.show()
    #n.s(np.ones((2,2)))
    #print(dir(n))
    #print(n.s)
    #print(n.s11)
    #data=instr.readSParameters()
    #plt.plot(np.abs(data[1]));
    #plt.show()
