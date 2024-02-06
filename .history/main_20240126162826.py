import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from main_ui import Ui_MainWindow

class MainApplication(Ui_MainWindow):
    def __init__(self):
        super(self,QMainWindow).__init__()
        






app = QApplication(sys.argv)
win = MainApplication() # Change to class name
win.show()
app.exec()