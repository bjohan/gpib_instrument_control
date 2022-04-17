#!/usr/bin/python3

import scipy.interpolate 
import scipy.io as sio

class ChannelCalculator:
    def __init__(self, meter, dbdiv=10, refline=0, offset=0, centeroffs=0.002):
        self.dbdiv=dbdiv
        self.refline=refline
        self.offset=offset
        self.centeroffs=centeroffs
        self.meter=meter

    def refline(self, refline):
        self.ref

    def read(self):
        return self.voltageToDbm(self.meter.readValue())

    def voltageToDbm(self, voltage):
        v=voltage-self.centeroffs
        div=v/0.1-self.refline
        db=div*self.dbdiv
        dbm=db+self.offset
        return dbm



class ProbeCorrector:
    def __init__(self, fn=None):
        self.corrector=self.loadCorrectionFactor(fn)

    def unityCorrection(x):
        return 0

    def loadMatFile(self, fn):
        return sio.loadmat(fn)

    def loadTable(self, f, yname, xname=None):
        if f is None:
            return ProbeCorrector.unityCorrection
        if xname is None:
            xname=yname+'_freq'
        d=self.loadMatFile(f)
        return scipy.interpolate.interp1d(d[xname][0], d[yname][0])

    def loadCorrectionFactor(self, f):
        return self.loadTable(f, 'correctionFactor', 'frequencies')

    def correct(self, value, f):
        #print("value %.2f, corr %.2f"%(value,self.corrector(f)));
        return value+self.corrector(f);


class Pm1038:
    def __init__(self, aChannelMeter, bChannelMeter, aChannelProbeCorrectionFileName=None, bChannelProbeCorrectionFileName=None):
        self.channelCalculatorA=ChannelCalculator(aChannelMeter)
        self.channelCalculatorB=ChannelCalculator(bChannelMeter)
        self.channelCorrectorA=ProbeCorrector(aChannelProbeCorrectionFileName)
        self.channelCorrectorB=ProbeCorrector(bChannelProbeCorrectionFileName)

    def readChannelA(self, frequency):
        return self.channelCorrectorA.correct(self.channelCalculatorA.read(), frequency)

    def readChannelB(self, frequency):
        return self.channelCorrectorB.correct(self.channelCalculatorB.read(), frequency)


if __name__=="__main__":
    import racal_dana_6000
    import hp_3438a
    pm = Pm1038(racal_dana_6000.RacalDana6000(), hp_3438a.Hp3438A(), "pm_b1391_correctionFactors.mat",  "pm11-0674_correctionFactors.mat")
    print("a", pm.readChannelA(50e6), "b", pm.readChannelB(50e6))
