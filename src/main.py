"""
author: Marie-Neige Chapel
"""

# Python
import sys

# PyQt
from PyQt6 import QtCore, QtWidgets

# PackY
from model.log import messageHandler
from view.main_window import MainWindow

# -----------------------------------------------------------------------------
def initLog() -> None:
	QtCore.qInstallMessageHandler(messageHandler)
	QtCore.qInfo("log starts")

# -----------------------------------------------------------------------------
app = QtWidgets.QApplication(sys.argv)
main_window = MainWindow()
initLog()
sys.exit(app.exec())
