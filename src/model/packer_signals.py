"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QObject, pyqtSignal

###############################################################################
class PackerSignals(QObject):

	progress = pyqtSignal(int)
