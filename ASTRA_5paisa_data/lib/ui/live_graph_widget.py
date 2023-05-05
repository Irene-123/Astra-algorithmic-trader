import numpy as np
from pyqtgraph import GraphicsLayoutWidget


class LiveGraphWidget(GraphicsLayoutWidget):
    def __init__(self, program_timer, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('pyqtgraph example: Scrolling Plots')
 
        self.p3 = self.addPlot()
        self.p4 = self.addPlot()
        # Use automatic downsampling and clipping to reduce the drawing load
        # self.p3.setDownsampling(mode='peak')
        # self.p4.setDownsampling(mode='peak')
        
        self.p3.setClipToView(True)
        self.p4.setClipToView(True)
        self.p3.setRange(xRange=[-100, 0])
        self.p3.setLimits(xMax=0)
        self.curve3 = self.p3.plot()
        self.curve4 = self.p4.plot()

        self.data3 = np.empty(100)
        self.ptr3 = 0

        program_timer.timeout.connect(self.update)

    def update(self):
        self.data3[self.ptr3] = np.random.normal()
        self.ptr3 += 1
        if self.ptr3 >= self.data3.shape[0]:
            tmp = self.data3
            self.data3 = np.empty(self.data3.shape[0] * 2)
            self.data3[:tmp.shape[0]] = tmp
        self.curve3.setData(self.data3[:self.ptr3])
        self.curve3.setPos(-self.ptr3, 0)
        self.curve4.setData(self.data3[:self.ptr3])

