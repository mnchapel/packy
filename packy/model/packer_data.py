"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
from enum import Enum

#PyQt
from PyQt6.QtCore import QAbstractListModel

# PackY
from model.packer_type_data import PackerTypeData
from utils.resources_access import resources_path

###############################################################################
class DataName(Enum):
	PACKER_TYPE = 0
	COMPRESSION_LEVEL = 1
	COMPRESSION_METHOD = 2

###############################################################################
class PackerData(QAbstractListModel):
    
	# -------------------------------------------------------------------------
	def __init__(self, json_dict: dict = None):
		super(PackerData, self).__init__()

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.jsonInitialization(json_dict)
			
		self.loadPackerInfo()

	# -------------------------------------------------------------------------
	def loadPackerInfo(self):
		file_path = os.path.join(resources_path(), "json/packer_info.json")
		with open(file_path, "r") as file:
			self.__info = json.load(file)

	# -------------------------------------------------------------------------
	def defaultInitialization(self):
		self.__packer_type_data = PackerTypeData()
		self.__compression_method_index = 0
		self.__compression_level_index = 0
	
	# -------------------------------------------------------------------------
	def jsonInitialization(self, json_dict: dict):
		self.__packer_type_data = PackerTypeData(json_dict["type"])
		self.__compression_method_index = json_dict["compression_method"]
		self.__compression_level_index = json_dict["compression_level"]

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def extension(self):
		return self.__packer_type_data.extension()

	# -------------------------------------------------------------------------
	def packerTypeData(self):
		return self.__packer_type_data

	# -------------------------------------------------------------------------
	def type(self):
		return self.__packer_type_data.type()
	
	# -------------------------------------------------------------------------
	def compressionMethod(self):
		return self.__compression_method_index
	
	# -------------------------------------------------------------------------
	def compressionLevel(self):
		return self.__compression_level_index

    # -------------------------------------------------------------------------
	def methodsInfo(self):
		packer_type = self.extension()
		packer_info = self.__info[packer_type]
		return packer_info["methods"]

    # -------------------------------------------------------------------------
	def levelsInfo(self):
		packer_type = self.extension()
		packer_info = self.__info[packer_type]
		return packer_info["levels"]

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return len(DataName)
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			if index.row() == DataName.PACKER_TYPE.value:
				return None
			elif index.row() == DataName.COMPRESSION_LEVEL.value:
				return self.__compression_level_index
			else:
				return self.__compression_method_index
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			if index.row() == DataName.COMPRESSION_LEVEL.value:
				self.__compression_level_index = value
			elif index.row() == DataName.COMPRESSION_METHOD.value:
				self.__compression_method_index = value
		return False

    # -------------------------------------------------------------------------
	def serialize(self) -> dict:
		dict = {}

		dict["type"] = self.type()
		dict["compression_method"] = self.__compression_method_index
		dict["compression_level"] = self.__compression_level_index

		return dict