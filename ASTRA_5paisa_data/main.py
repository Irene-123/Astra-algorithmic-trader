import sys
import ASTRA.settings as settings

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

from lib.ui.live_graph_widget import LiveGraphWidget
from lib.ui.raw.main_window import Ui_MainWindow

class Window(Ui_MainWindow, QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        
        self.timer = QTimer()   # Timer for the program, to display dynamic changing graphs
        
        self.graph = LiveGraphWidget(self.timer)     # Widget for live graphs
        self.horizontalLayout_Main.addWidget(self.graph)
        self.graph.show()
        
        self.connectSignalSlots()
        
    def connectSignalSlots(self):
        self.pushButton_Main.clicked.connect(self.switch_timer)
        
    def switch_timer(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(settings.APPLICATION_REFRESH_TIME)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())