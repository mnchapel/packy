"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum

#PyQt
from PyQt6 import QtCore

# PackY
from packer_type_data import PackerTypeData

###############################################################################
class PackerData(QtCore.QAbstractListModel):
    
	# -------------------------------------------------------------------------
	def __init__(self, dict = None):
		super(PackerData, self).__init__()

		self.data_names = Enum("DataName", [
			"PACKER_TYPE",
			"COMPRESSION_LEVEL",
			"COMPRESSION_METHOD"
		], start = 0)

		self.compression_levels = Enum("CompressionLevelName", [
			"STORE",
			"DEFLATE",
			"OPTIMAL"
		], start = 0)

		self.compression_methods = Enum("CompressionMethodName", [
			"NORMAL",
			"MAXIMUM",
			"FAST",
			"FASTEST"
		], start = 0)

		if dict is None:
			self._packer_type_data = PackerTypeData()
			self._compression_method_index = 0
			self._compression_level_index = 0
		else:			
			self._packer_type_data = PackerTypeData(dict["type"])
			self._compression_method_index = dict["compression_method"]
			self._compression_level_index = dict["compression_level"]

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def packerTypeData(self):
		return self._packer_type_data

	# -------------------------------------------------------------------------
	def type(self):
		return self._packer_type_data.type()
	
	# -------------------------------------------------------------------------
	def compressionMethod(self):
		return self._compression_method_index
	
	# -------------------------------------------------------------------------
	def compressionLevel(self):
		return self._compression_level_index

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return len(self.data_names)
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			if index.row() == self.data_names.PACKER_TYPE.value:
				return None
			elif index.row() == self.data_names.COMPRESSION_LEVEL.value:
				return self._compression_level_index
			else:
				return self._compression_method_index
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			if index.row() == self.data_names.COMPRESSION_LEVEL.value:
				self._compression_level_index = value
			elif index.row() == self.data_names.COMPRESSION_METHOD.value:
				self._compression_method_index = value
		return False