import matplotlib.pyplot as plt


def checkParam(param, validParams, message):
    if param not in validParams:

        raise ValueError("%s. %s not in [%s]"%(message, str(param), str(validParams)))

class Trace:
    def __init__(self, x, y, xunit, yunit, name = None):
        self.x = x
        self.y = y
        self.xunit = xunit
        self.yunit = yunit
        self.name = name

    def draw(self):
        plt.plot(self.x, self.y, label=self.name)
        plt.xlabel(self.xunit)
        plt.ylabel(self.yunit)

    def show(self):
        plt.legend()
        plt.show()

    def plot(self):
        self.draw()
        self.show()
