import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow)
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal, QObject

from main_window_ui import Ui_MainWindow

from get_sel_txt import TextGetter

class SignalEmitter(QObject):
    new_text_signal = pyqtSignal(str)

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.connectSignalsSlots()
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.new_text_signal.connect(self.my_func)
        self.getterObj = None

    def connectSignalsSlots(self):
        self.pushButton.clicked.connect(self.start_my_thread)
        self.pushButton_2.clicked.connect(self.stop_my_thread)

    def start_my_thread(self):
        self.getterObj = TextGetter(self.signal_emitter.new_text_signal)
        self.getterObj.start_threads()

    def stop_my_thread(self):
        #self.getterObj.threads.clear()
        self.getterObj.on_activate_exit()

        threads_active = True
        while threads_active:
            threads_active = False
            for thread in self.getterObj.threads:
                if thread.is_alive():
                    threads_active = True
                    
        self.getterObj.threads.clear()

        
    def my_func(self,value):
        print(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())