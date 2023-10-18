"""
author: Marie-Neige Chapel
"""

import sys
from PyQt6 import QtWidgets
from view.main_window import MainWindow

app = QtWidgets.QApplication(sys.argv)
main_window = MainWindow()
sys.exit(app.exec())
