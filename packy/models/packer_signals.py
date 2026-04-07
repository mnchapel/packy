"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PyQt
from PySide6.QtCore import QObject, Signal


###############################################################################
class PackerSignals(QObject):
    ###########################################################################
    # SIGNALS
    ###########################################################################
    info = Signal(str)
    error = Signal(str)
    progress = Signal(int)
    finish = Signal()
