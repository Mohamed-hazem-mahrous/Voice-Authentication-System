from PyQt5.QtWidgets import QApplication
from main import 






app = QApplication(sys.argv)
win = mainWindow() # Change to class name
win.show()
app.exec()