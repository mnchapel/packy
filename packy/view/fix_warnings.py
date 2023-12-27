"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtWidgets import QDialog, QAbstractButton
from PyQt6.uic import loadUi

# PackY
from model.files_model import FilesModel
from model.warnings import Warnings

###############################################################################
class FixWarnings(QDialog):

	###########################################################################
	# MEMBER VARIABLES
	#
	# __ui : 
	# __model: the model
	###########################################################################

	###########################################################################
	# CONSTRUCTOR
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, files_model: FilesModel, parent=None) -> None:
		super(FixWarnings, self).__init__()

		self.__ui = loadUi("../resources/fix_warnings.ui", self)
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
		self.__ui.button_box.clicked.connect(self.buttonClicked)

	# -------------------------------------------------------------------------
	def buttonClicked(self, button: QAbstractButton) -> None:
		if button.text() == "Apply":
			self.__model.updateModel()
			super().accept()
