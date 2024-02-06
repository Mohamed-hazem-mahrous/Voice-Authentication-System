from PyQt5.QtWidgets import QApplication







app = QApplication(sys.argv)
win = mainWindow() # Change to class name
win.show()
app.exec()