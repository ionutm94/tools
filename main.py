from PySide6.QtWidgets import QApplication
from mainwindow import MainWindow
import sys

app = QApplication(sys.argv)

mainwindow = MainWindow()
mainwindow.show()

app.exec()

