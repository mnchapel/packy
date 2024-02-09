"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os

# PyQt
from PyQt6.QtWidgets import QDialog, QAbstractButton
from PyQt6.uic import loadUi

# PackY
from model.files_model import FilesModel
from model.warnings import Warnings
from utils.external_data_access import ExternalData, external_data_path

###############################################################################
class FixWarnings(QDialog):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __ui : 
	# __model: the model
	###########################################################################

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, files_model: FilesModel, parent=None) -> None:
		super(FixWarnings, self).__init__()

		ui_path = external_data_path(ExternalData.UI_FIX_WARNINGS)
		self.__ui = loadUi(ui_path, self)
		self.__model = files_model
		self.__init()

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################
		
	# -------------------------------------------------------------------------
	def __init(self) -> None:
		warnings = self.__model.warnings()
		self.__initAddedItems(warnings)
		self.__initRemovedItems(warnings)

		self.__initConnect()

	# -------------------------------------------------------------------------
	def __initAddedItems(self, warnings: Warnings) -> None:
		added_items = warnings.addedItems()
		self.added_items.addItems(added_items)

	# -------------------------------------------------------------------------
	def __initRemovedItems(self, warnings: Warnings) -> None:
		removed_items = warnings.removedItems()
		self.removed_items.addItems(removed_items)

	# -------------------------------------------------------------------------
	def __initConnect(self) -> None:
		self.__ui.button_box.clicked.connect(self.__buttonClicked)

	###########################################################################
	# PRIVATE SLOT
	###########################################################################

	# -------------------------------------------------------------------------
	def __buttonClicked(self, button: QAbstractButton) -> None:
		if button.text() == "Apply":
			self.__model.updateModel()
			super().accept()
