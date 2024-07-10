import sys

from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog)
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
        self.signal_emitter.new_text_signal.connect(self.update_text_field)
        self.getterObj = None

    def connectSignalsSlots(self):
        self.startTextGetterButton.clicked.connect(self.start_my_thread)
        self.stopTextGetterButton.clicked.connect(self.stop_my_thread)

    def start_my_thread(self):
        self.getterObj = TextGetter(self.signal_emitter.new_text_signal)
        self.getterObj.start_threads()

    def stop_my_thread(self):
        self.getterObj.on_activate_exit()
        #self.filename, _ = QFileDialog.getOpenFileName()
        print(self.filename)

        threads_active = True
        while threads_active:
            threads_active = False
            for thread in self.getterObj.threads:
                if thread.is_alive():
                    threads_active = True
                    
        self.getterObj.threads.clear()

        
    def update_text_field(self,value):
        self.textGetterTextField.insertPlainText(value + "\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())