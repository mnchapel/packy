"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# Python
import sys

# PyQt
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon

# PackY
from models.log import messageHandler
from views.main_window import MainWindow
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
