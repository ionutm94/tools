import threading
from pynput import keyboard
import win32clipboard
import time
import pywintypes

class TextGetter(object):
    instance = None
    #make sure that only one instance of a this type is created at a time
    def __new__(cls,*args,**kwargs):
        if not cls.instance:
            cls.instance = super().__new__(cls)
            cls.instance.initialized = False
        return cls.instance

    def __init__(self,external_signal):
        if not self.initialized:
            self.threads_running = False
            self.stop_bg_task = False
            self.new_data_event = threading.Event()
            self.initialized = True
            self.signal = external_signal

    def start_threads(self):
        if not self.threads_running:

            self.seq_nr = win32clipboard.GetClipboardSequenceNumber()
            self.last_seq_nr = self.seq_nr

            try:
                self.threads.clear()
            except AttributeError:
                self.threads = []
            
            self.threads.append(threading.Thread(target=self.wait_for_info, daemon=True))
            self.threads.append(keyboard.GlobalHotKeys({'<ctrl>+c': self.on_activate_copy}))

            self.threads[0].start()
            self.threads[1].start()

            self.threads_running = True
            
    def on_activate_copy(self):
        self.new_data_event.set()

    def on_activate_exit(self):
        self.stop_bg_task = True
        self.new_data_event.set()
        self.threads[1].stop()

    def wait_for_info(self):
        while not self.stop_bg_task:

            self.new_data_event.wait()

            while not self.stop_bg_task:

                self.seq_nr = win32clipboard.GetClipboardSequenceNumber()
                if self.seq_nr == self.last_seq_nr:
                    continue

                try:
                    data_found = True
                    win32clipboard.OpenClipboard()
                    try:
                        data = win32clipboard.GetClipboardData()
                    except TypeError:
                        data_found = False

                    win32clipboard.CloseClipboard()

                    if data_found:
                        self.signal.emit(data)
                    self.last_seq_nr = self.seq_nr
                    
                    break

                except pywintypes.error:
                    time.sleep(0.1)

        self.new_data_event.clear()

        if self.stop_bg_task:            
            self.threads_running = False
            self.stop_bg_task = False

if __name__ == "__main__":
    try:
        text_obj = TextGetter()
        text_obj.start_threads()

    except KeyboardInterrupt:
        print('Program closed normally.')
