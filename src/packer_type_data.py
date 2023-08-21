"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum

#PyQt
from PyQt6 import QtCore

class PackerTypeData(QtCore.QAbstractListModel):
    
	# -------------------------------------------------------------------------
	def __init__(self):
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

		self._type_index = 0
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return len(self.types)
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			if index.row() == self._type_index:
				return True
			else:
				return False
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			if value is True:
				self._type_index = index.row()
			return True
		return False