"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum

#PyQt
from PyQt6 import QtCore

class PackerType(QtCore.QAbstractListModel):
    
	# -------------------------------------------------------------------------
	def __init__(self):
		super(PackerType, self).__init__()

		self.properties = Enum("TypeName", [
			"ZIP",
			"TAR",
			"BZ2",
			"TBZ",
			"GZ",
			"TGZ",
			"LZMA",
			"TLZ",
			"XZ"
		])

		self._type = 0
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return len(self.properties)
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			if index.row() == self._type:
				return True
			else:
				return False
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			if value is True:
				self._type = index.row()
			return True
		return False