#!/usr/bin/python3
import my_gpib
import gpib
import time
import numpy as np
import struct
import matplotlib.pyplot as plt
import skrf.network

class Hp8753A(my_gpib.MyGpib):
    def __init__(self, addr=16):
        my_gpib.MyGpib.__init__(self, addr);
        idStr=self.query("*IDN?")
        refStr=b'HEWLETT PACKARD,8753A,0,1.00\n'
        if idStr!=refStr:
            if "8753" not in idStr:
                raise Exception("Instrument att address {addr} does not seem to be a 8753")
            else:
                print("Warning, IDN response does not completely match")

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
        self.write('LINM')
        return np.array(real)*np.exp(np.array(imag)*1j*np.pi/180.0)


    def readSParameter(self, param):
        print("Measuring", param)
        self.write(param+';')
        self.query('OPC?;SING;')
        return self.readComplexTraceData()


    def readSParameters(self):
        s11=self.readSParameter('S11')
        s21=self.readSParameter('S21')
        s12=self.readSParameter('S12')
        s22=self.readSParameter('S22')
        return s11, s12, s21, s22

    def startFrequency(self):
        return float(self.query("STAR?;"))

    def stopFrequency(self):
        return float(self.query("STOP?;"))

    def frequencyPoints(self):
        return int(float(self.query("POIN?;")))

    def frequencies(self):
        return np.linspace(self.startFrequency(), self.stopFrequency(), self.frequencyPoints())

    def __delete__(self):
        pass

def mergeVectorsToSparam(vs11, vs12, vs21, vs22):
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
    parser.add_argument('-od', '--open-deembed', type=argparse.FileType('rb'), help='Use s11/2 and s22/2 from specified touchstone file to deembed s11 and s22 measurements');
    parser.add_argument('-td', '--through-deembed', type=argparse.FileType('rb'), help='Use s21 and s12 from specified touchstone file to deembed s12 and s21 measurements');
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
        de=skrf.network.Network(file=pa.open_deembed.name)

    if pa.through_deembed:
        td=skrf.network.Network(file=pa.through_deembed.name)


    f=instr.frequencies()
    ss11, ss12, ss21, ss22 = instr.readSParameters()
    ss = []
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


    n = skrf.network.Network(f=f, s=mergeVectorsToSparam(ss11, ss12, ss21, ss22), z0=[50,50])
    if pa.write_touchstone_file:
        print(dir(pa.write_touchstone_file))
        n.write_touchstone(pa.write_touchstone_file.name)
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
