"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
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
class PackerDataSerialKeys(Enum):
	TYPE = "type"
	COMPRESSION_METHOD = "compression_method"
	COMPRESSION_LEVEL = "compression_level"

###############################################################################
class DataName(Enum):
	PACKER_TYPE = 0
	COMPRESSION_LEVEL = 1
	COMPRESSION_METHOD = 2

###############################################################################
class PackerData(QAbstractListModel):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __packer_type_data: 
	# __compression_method_index: 
	# __compression_level_index: 
	# __info: 
	###########################################################################
    
	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, json_dict: dict = None):
		super(PackerData, self).__init__()

		if json_dict is None:
			self.__defaultInitialization()
		else:
			self.__jsonInitialization(json_dict)
			
		self.__loadPackerInfo()

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

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __loadPackerInfo(self):
		file_path = os.path.join(resources_path(), "json/packer_info.json")
		with open(file_path, "r") as file:
			self.__info = json.load(file)

	# -------------------------------------------------------------------------
	def __defaultInitialization(self):
		self.__packer_type_data = PackerTypeData()
		self.__compression_method_index = 0
		self.__compression_level_index = 0
	
	# -------------------------------------------------------------------------
	def __jsonInitialization(self, json_dict: dict):
		self.__packer_type_data = PackerTypeData(json_dict[PackerDataSerialKeys.TYPE.value])
		self.__compression_method_index = json_dict[PackerDataSerialKeys.COMPRESSION_METHOD.value]
		self.__compression_level_index = json_dict[PackerDataSerialKeys.COMPRESSION_LEVEL.value]