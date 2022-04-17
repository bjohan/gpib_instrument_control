#!/usr/bin/python3
import my_gpib

class Hp3438A(my_gpib.MyGpib):
    def __init__(self, addr=2):
        my_gpib.MyGpib.__init__(self, addr);

    def readValue(self):
        data=''
        while True:
            c= self.read(readSz=1)
            data+=c.decode('utf-8')
            if c == b'\n':
                break
        if '++' in data:
            data=data.replace('++', '+')
        if len(data) < 4:
            return readValue();
        data = data.split(',')[0]
        return float(data)


if __name__ == "__main__":
    m=Hp3438A()
    print("Read value:", m.readValue())
