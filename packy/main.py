"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import sys

# PyQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QIcon

# PackY
from model.log import messageHandler
from view.main_window import MainWindow
from utils.external_data_access import ExternalData, external_data_path

# -----------------------------------------------------------------------------
def initLog() -> None:
	QtCore.qInstallMessageHandler(messageHandler)
	QtCore.qDebug("Log starts debug")

# -----------------------------------------------------------------------------
app = QtWidgets.QApplication(sys.argv)
icon_path = external_data_path(ExternalData.LOGO)
app.setWindowIcon(QIcon(icon_path))
main_window = MainWindow()
initLog()
sys.exit(app.exec())
