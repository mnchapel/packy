"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum

#PyQt
from PyQt6 import QtCore

###############################################################################
class PackerTypeData(QtCore.QAbstractListModel):
    
	# -------------------------------------------------------------------------
	def __init__(self, type_index = None):
		super(PackerTypeData, self).__init__()

		self.types = Enum("TypeName", [
			"ZIP",
			"TAR",
			"BZ2",
			"TBZ",
			"GZ",
			"TGZ",
			"LZMA",
			"TLZ",
			"XZ"
		], start = 0)

		if type_index is None:
			self.__type_index = 0
		else:
			self.__type_index = type_index

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def extension(self):
		return self.types(self.__type_index).name.lower()

	# -------------------------------------------------------------------------
	def type(self):
		return self.__type_index

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return len(self.types)
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			if index.row() == self.__type_index:
				return True
			else:
				return False
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			if value is True:
				self.__type_index = index.row()
			return True
		return False