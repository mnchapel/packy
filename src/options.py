"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

###############################################################################
class Options(QDialog):

	# -------------------------------------------------------------------------
	def __init__(self, parent=None):
		super().__init__(parent)
		loadUi("../resources/options.ui", self)
