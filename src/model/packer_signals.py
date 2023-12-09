"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QObject, pyqtSignal

###############################################################################
class PackerSignals(QObject):

	error = pyqtSignal(str)
	progress = pyqtSignal(int)
	finish = pyqtSignal()
