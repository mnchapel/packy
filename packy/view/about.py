"""
author: Marie-Neige Chapel
"""

# Python
import os

# PyQt
from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

# PackY
from utils.resources_access import resources_path

class About(QDialog):

	# -------------------------------------------------------------------------
	def __init__(self, parent=None):
		super().__init__(parent)
		ui_path = os.path.join(resources_path(), "about.ui")
		loadUi(ui_path, self)
