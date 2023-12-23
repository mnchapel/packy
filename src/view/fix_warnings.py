"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

# PackY
from model.warnings import Warnings

###############################################################################
class FixWarnings(QDialog):

	###########################################################################
	# MEMBER VARIABLES
	#
	# - __warnings: the model
	###########################################################################

	###########################################################################
	# CONSTRUCTOR
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, warnings: Warnings, parent=None) -> None:
		super(FixWarnings, self).__init__()

		self.__ui = loadUi("../resources/fix_warnings.ui", self)
		self.__init(warnings)

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################
		
	# -------------------------------------------------------------------------
	def __init(self, warnings: Warnings) -> None:
		self.__initAddedItems(warnings)
		self.__initRemovedItems(warnings)

	# -------------------------------------------------------------------------
	def __initAddedItems(self, warnings: Warnings) -> None:
		added_items = warnings.addedItems()
		self.added_items.addItems(added_items)

	# -------------------------------------------------------------------------
	def __initRemovedItems(self, warnings: Warnings) -> None:
		removed_items = warnings.removedItems()
		self.removed_items.addItems(removed_items)
