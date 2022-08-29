import skrf as rf

class VnaFixture:
    def __init__(self, vna, calKit, fstart, fstop, fstep, prefix, refPrefix, suffix='.s2p', refSuffix='.s2p', forceMeasure=False):
        self.vna=vna
        self.calKit=calKit
        self.fstart=fstart
        self.fstop=fstop
        self.fstep=fstep
        self.shortFn=prefix+'short'+suffix
        self.openFn=prefix+'open'+suffix
        self.loadFn=prefix+'load'+suffix
        self.throughFn=prefix+'through'+suffix
        self.forceMeasure=forceMeasure

        self.shortRef=rf.Network(refPrefix+'short'+refSuffix)
        self.openRef=rf.Network(refPrefix+'open'+refSuffix)
        self.loadRef=rf.Network(refPrefix+'load'+refSuffix)
        self.throughRef=rf.Network(refPrefix+'through'+refSuffix)

        self.acquireShort()
        self.acquireOpen()
        self.acquireLoad()
        self.acquireThrough()

        self.ideals=[self.shortRef, self.openRef, self.loadRef, self.throughRef]
        self.measured=[self.shortData, self.openData, self.loadData, self.throughData]

        self.cal=rf.TwelveTerm(ideals=self.ideals, measured=self.measured, n_thrus=1)
        self.cal.run()

    def measure(self):
        return self.vna.getHighResolutionNetwork(self.fstart, self.fstop, fres=self.fstep)

    def measureShort(self):
        self.calKit.s()
        return self.measure()
        
    def measureOpen(self):
        self.calKit.o()
        return self.measure()
        
    def measureLoad(self):
        self.calKit.l()
        return self.measure()
        
    def measureThrough(self):
        self.calKit.t()
        return self.measure()

    def updateShortFile(self):
        self.shortData=self.measureShort();
        self.shortData.write_touchstone(self.shortFn)
        
    def updateOpenFile(self):
        self.openData=self.measureOpen();
        self.openData.write_touchstone(self.openFn)
        
    def updateLoadFile(self):
        self.loadData=self.measureLoad();
        self.loadData.write_touchstone(self.loadFn)
        
    def updateThroughFile(self):
        self.throughData=self.measureThrough();
        self.throughData.write_touchstone(self.throughFn)
        
    def acquireShort(self):
        if self.forceMeasure:
            self.updateShortFile()
        try:
            self.shortData=rf.Network(self.shortFn)
        except FileNotFoundError:
            self.updateShortFile();

    def acquireOpen(self):
        if self.forceMeasure:
            self.updateOpenFile()
        try:
            self.openData=rf.Network(self.openFn)
        except FileNotFoundError:
            self.updateOpenFile();

    def acquireLoad(self):
        if self.forceMeasure:
            self.updateLoadFile()
        try:
            self.loadData=rf.Network(self.loadFn)
        except FileNotFoundError:
            self.updateLoadFile();

    def acquireThrough(self):
        if self.forceMeasure:
            self.updateThroughFile()
        try:
            self.throughData=rf.Network(self.throughFn)
        except FileNotFoundError:
            self.updateThroughFile();

    def calibratedMeasure(self):
        return self.cal.apply_cal(self.measure())

