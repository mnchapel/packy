"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
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
