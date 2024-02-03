"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os

# PyQt
from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

# PackY
from utils.resources_access import resources_path

###############################################################################
class About(QDialog):
	
	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, parent=None):
		super().__init__(parent)
		ui_path = os.path.join(resources_path(), "ui/about.ui")
		loadUi(ui_path, self)
