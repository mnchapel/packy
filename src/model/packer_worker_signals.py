"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QObject, pyqtSignal

###############################################################################
class PackerWorkerSignals(QObject):
	
	runTaskId = pyqtSignal(int)
