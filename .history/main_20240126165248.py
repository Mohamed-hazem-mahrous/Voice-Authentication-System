import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from main_ui import Ui_MainWindow

class MainApplication(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainApplication, self).__init__()
        self.setupUi(self)
        
        self.state_labels = {
            "processing" :self.label_state_processing,
            "idle": self.label_state_Idle,
            "denied": self.label_state_denied,
            "granted":self.label_state_granted}
        self.set_state("idle")
        
        self.btn_record.clicked.connect(lambda: self.set_state("granted"))
        
        
    ############### Accessory Functions ###############
    
    def set_state(self, state: str):
        for state_label in self.state_labels.values():
            state_label.setVisible(False)
        self.state_labels[state].setVisible(True)
        
        






app = QApplication(sys.argv)
win = MainApplication() # Change to class name
win.show()
app.exec()