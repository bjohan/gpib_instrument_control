#!/usr/bin/python3
import my_gpib
import gpib
import time
import numpy as np
import struct
import matplotlib.pyplot as plt

class Hp8569B(my_gpib.MyGpib):
    def __init__(self, addr=2):
        my_gpib.MyGpib.__init__(self, addr);

    def getCenterFrequency(self): 
        d=self.query('CF')[:-1].decode('UTF-8')
        return int(d)

    def getSpan(self): 
        d=self.query('SP')[:-1].decode('UTF-8')
        return int(d)

    def getFrequencies(self):
        cf=self.getCenterFrequency()
        sp=self.getSpan()
        if sp == -2:
            return np.linspace(1.7e9,22e9, 481);
        if sp == -1:
            if cf < 1.7e9:
                return np.linspace(-25e6,1.8e9, 481);
            if cf < 4.1e9:
                return np.linspace(1.7e9,4.1e9, 481);
            if cf < 8.5e9:
                return np.linspace(3.8e9,8.5e9, 481);
            if cf < 12.9e9:
                return np.linspace(5.8e9,12.9e9, 481);
            if cf < 18e9:
                return np.linspace(8.5e9,18e9, 481);
            return np.linspace(10.5e9,22e9, 481);
        fstart=cf-5*sp;
        fstop=cf+5*sp;
        return np.linspace(fstart, fstop, 481)
                
    def readTrace(self, num='A'):
        if num not in ['A', 'B']:
            raise ValueError('argument num must be either A or B')
        rl=self.referenceLevel()
        d=str(self.query('T'+num))
        a=[]
        for i in str(d[2:-3]).split(','):
            v=int(i.rstrip())
            db=rl+(v-800.0)/10
            a.append(db)
        return self.getFrequencies(), self.deGlitch(a)

    def deGlitch(self, t):
        for i in range(1, len(t)-1):
            s=(t[i-1]+t[i+1])/2;
            if t[i] < (s-8):
                t[i]=s
        return t

    def referenceLevel(self):
        d=self.query('RL')[:-1].decode('UTF-8')
        return int(d)

    def updateTrace(self):
        self.write('SF')
        while True:
            s=ord(self.query('MS').decode('UTF-8'))
            if s == 0:
                break



if __name__ == '__main__':
    sa=Hp8569B()
    hist=None
    fref=None
    stdDev=None
    mean=None
    ax1 = plt.subplot(3,1,1)
    ax2 = plt.subplot(3,1,2)
    ax3 = plt.subplot(3,1,3)
    while True:
        sa.updateTrace()
        f, t=sa.readTrace();
        t=np.array(t)
        if hist is None:
            hist=t
        else:
            hist=np.vstack((hist, t))
        if fref is None:
            fref = f
        else:
            fd=np.max(fref-f)
            if fd > 1e6:
                print(fd)
                print("frequency changed");
                break
        #plt.figure(1)
        ax1.clear()
        ax1.plot(f, t)
        if mean is not None:
            ax1.plot(f, mean)
            ax1.plot(f, mean+5*std)
            ax1.plot(f, np.max(hist, axis=0))
            ax1.legend(['t', 'm', '7s', 'max'])
            
            #ax1.plot(f, mean-5*std)
            over=np.where(np.abs(mean-t)>5*std)[0]
            if len(over) > 1:
                print('\a')

        ax1.grid(True)
        if hist.ndim > 1:
            #plt.figure(2)
            ax2.clear()
            if mean is None:
                ax2.imshow(hist)
            else:
                delta=hist-mean;
                if delta.shape[1] > 50:
                    ax2.imshow(delta[-50:, :])
                else:
                    ax2.imshow(delta)
            mean=np.mean(hist, axis=0)
            std=np.std(hist, axis=0)
            while hist.shape[0] > 100:
                hist=np.delete(hist, (0), axis=0)
            ax3.clear()
            ax3.plot(f, std);
            ax3.grid(True)
        plt.pause(0.02)
        sa.updateTrace()
    plt.show()
