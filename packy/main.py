"""
author: Marie-Neige Chapel
"""

# Python
import os
import sys

# PyQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIcon

# PackY
from model.log import messageHandler
from view.main_window import MainWindow
from utils.resources_access import resources_path

# -----------------------------------------------------------------------------
def initLog() -> None:
	QtCore.qInstallMessageHandler(messageHandler)
	QtCore.qDebug("Log starts debug")

# -----------------------------------------------------------------------------
app = QtWidgets.QApplication(sys.argv)
icon_path = os.path.join(resources_path(), "img/logo.ico")
app.setWindowIcon(QIcon(icon_path))
main_window = MainWindow()
initLog()
sys.exit(app.exec())
