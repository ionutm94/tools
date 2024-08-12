from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl, Signal, QObject

import PyPDF2
import tempfile
import shutil

from get_sel_txt import TextGetter

from main_window_ui import Ui_MainWindow

class SignalEmitter(QObject):

    data_signal = Signal(str)
    
    def get_data(self,data):
        self.data_signal.emit(data)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.signal_from_helper = SignalEmitter()
        self.signal_from_helper.data_signal.connect(self.get_helper_data)

        self.web_view =  QWebEngineView()
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PluginsEnabled, True)
        self.web_view.settings().setAttribute(self.web_view.settings().WebAttribute.PdfViewerEnabled, True)

        scroll_layout = QVBoxLayout()
        scroll_layout.addWidget(self.web_view)
        self.scrollArea.setLayout(scroll_layout)

        self.action_Open.triggered.connect(self.load_pdf)
        self.actionStartHelper.triggered.connect(self.start_helper)
        self.actionStopHelper.triggered.connect(self.stop_helper)

    def load_pdf(self):
        file_dialog = QFileDialog()
        filename, _ = file_dialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")

        if filename:
            self.tempdir = tempfile.mkdtemp()
            pdf_save_path = self.tempdir + "\\temp_pdf.pdf"

            with open(filename, 'rb') as pdf_obj:
                pdf = PyPDF2.PdfReader(pdf_obj)
                pdf_out = PyPDF2.PdfWriter()

                for page in pdf.pages:
                    if page.annotations:
                        page.annotations.clear()
                    pdf_out.add_page(page)

                with open(pdf_save_path, 'wb') as out:
                    pdf_out.write(out)

            local_url = QUrl.fromLocalFile(pdf_save_path)
            print(pdf_save_path)
            self.web_view.load(local_url)
    
    def closeEvent(self, event):
        try:
            shutil.rmtree(self.tempdir)
        except AttributeError:
            print("nu este folder de-asta")
        
    def start_helper(self):
        self.getterObj = TextGetter(self.signal_from_helper)
        self.getterObj.start_threads()
    
    def stop_helper(self):
        self.getterObj.on_activate_exit()

        threads_active = True
        while threads_active:
            threads_active = False
            for thread in self.getterObj.threads:
                if thread.is_alive():
                    threads_active = True
                    
        self.getterObj.threads.clear()

    def get_helper_data(self, value):
        value = value.replace(" ", "_")
        value = value.replace("\n","").replace('\r', '')
        if value != "":
            self.extractedTextField.appendPlainText(value)