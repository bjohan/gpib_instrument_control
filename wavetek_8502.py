#!/usr/bin/python3
import scipy.interpolate 
import scipy.io as sio
import my_gpib

class Wavetek8502(my_gpib.MyGpib):
    def __init__(self, addr=4):
        my_gpib.MyGpib.__init__(self, addr, verbose=False)
        self.checkIdn()
        

    def checkIdn(self):
        idnRef = b"WMI,8502,0,VER07.11\r\n"
        idn = self.getIdn();
        if idnRef == idn:
            return
        if b"WMI,8502" in idn:
            print("INFO: IDN seems to match, however FW might differ")
            return
        if b"8502" in idn:
            print("WARNING: only model number found in IDN string")
        raise Exception("Expected IDN string %s but instrument said %s"%(idnRef, idn))

    def getIdn(self):
        return self.query('*IDN?')

    def calibrateChannelA(self):
        self.write('CALA')

    def calibrateChannelB(self):
        self.write('CALB')

    def zeroChannelA(self):
        self.write('ZERA')

    def zeroChannelB(self):
        self.write('ZERB')

    def readChannel(self, frequency, ch=b'A'):
        self.write(b'CWP%s'%(ch))
        self.write(b"FREQ %0.2f"%(frequency/1e9))
        self.write(b'UPDT')
        data=self.query(b'UPDN')

        expectedStart = b"DBM%s"%(ch)
        if data[0:4] != expectedStart:
            raise Exception("%s does not start with %s"%(data, expectedStart)) 
        return float(data[4:].strip())

    def readChannelA(self, frequency):
        return self.readChannel(frequency, ch=b'A')

    def readChannelB(self, frequency):
        return self.readChannel(frequency, ch=b'B')

    def calibrationTemperatureDifference(self):
        data = self.query("DTMP").strip()
        parts = data.split(b',');
        temps=[]
        for p,c in zip(parts, [b'A', b'B']):
            expectedStart =  b'DTP'+c
            if p[0:4] != expectedStart:
                raise Exception("When parsing response %s the substring %s does not start with %s"%(data, p, expectedStart))
            temps.append(float(p[4:]))
        return temps




if __name__ == "__main__":
    import argparse
    parser=argparse.ArgumentParser(description='Interface for Wavetek 8502 peak power meter')
    parser.add_argument('-g', '--gpib', help="Gpib address", type=int)
    parser.add_argument('-ra', '--read-channel-a', help="Read power on channel a, ", metavar='FREQ', type=float)
    parser.add_argument('-rb', '--read-channel-b', help="Read power on channel b", metavar='FREQ', type=float)
    parser.add_argument('-ca', '--calibrate-channel-a', help="Calibrate channel A", action='store_true')
    parser.add_argument('-cb', '--calibrate-channel-b', help="Calibrate channel B", action='store_true')
    parser.add_argument('-za', '--zero-channel-a', help="Zero channel A", action='store_true')
    parser.add_argument('-zb', '--zero-channel-b', help="Zero channel B", action='store_true')
    parser.add_argument('-td', '--temperature-difference', help='Query instrument for temperature difference on probes since calibration', action='store_true')
    args = parser.parse_args()
    gpibAddr=4
    if args.gpib is not None:
        gpibAddr = args.gpib
    instr = Wavetek8502(addr=gpibAddr)

    if args.calibrate_channel_a:
        print("Starting calibration for channel A")
        instr.calibrateChannelA()

    if args.calibrate_channel_b:
        print("Starting calibration for channel B")
        instr.calibrateChannelB()

    if args.zero_channel_a:
        print("Starting zeroing for channel A")
        instr.zeroChannelA()

    if args.zero_channel_b:
        print("Starting zeroing for channel B")
        instr.zeroChannelB()

    if args.temperature_difference:
        a,b=instr.calibrationTemperatureDifference()
        print("Temperature difference relative to time of calibration. Channel A: %.1fK, channel B %.1fK"%(a, b))
 
    if args.read_channel_a is not None:
        print(instr.readChannelA(args.read_channel_a), "dBm")

    if args.read_channel_b is not None:
        print(instr.readChannelB(args.read_channel_b), "dBm")
