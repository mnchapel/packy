"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PyQt
from PyQt6.QtCore import QObject, pyqtSignal


###############################################################################
class PackerSignals(QObject):
    ###########################################################################
    # SIGNALS
    ###########################################################################
    info = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    finish = pyqtSignal()
