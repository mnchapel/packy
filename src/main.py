import sys
from PyQt6 import QtWidgets, uic

app = QtWidgets.QApplication(sys.argv)

main_window = uic.loadUi("../resources/main_window.ui")
main_window.show()
app.exec()
