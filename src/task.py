"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
from enum import Enum

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QStandardPaths
from files_model import FilesModel

# PackY
from packer_data import PackerData

###############################################################################
class Task(QtCore.QAbstractListModel):
	
	# -------------------------------------------------------------------------
	def __init__(self, json_dict = None):
		super(Task, self).__init__()
		
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.properties = Enum("TaskProperties", [
			"STATUS",
			"OUTPUT_NAME",
			"SOURCE_FOLDER",
			"DESTINATION_FILE",
			"PACKER_TYPE"
		])

		self._u_dash = u'\u2014'
		self._u_check = u'\u2713'
		self._u_cross = u'\u2717'

		self._status = self._u_dash

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.jsonInitialization(json_dict)

	# -------------------------------------------------------------------------
	def defaultInitialization(self):
		qt_folder_location = QStandardPaths.StandardLocation.DownloadLocation
		default_folder = QStandardPaths.writableLocation(qt_folder_location)

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._name = "output_name"
		self._packer_data = PackerData()
		self._files_selected = FilesModel()
		self._files_selected.setRootPath(default_folder)
		self._destination_file = default_folder + "/output." + self._packer_data.extension()
	
	# -------------------------------------------------------------------------
	def jsonInitialization(self, json_dict: dict):
		self._name = "output_name"
		self._destination_file = json_dict["destination_file"]
		self._packer_data = PackerData(json_dict["packer_data"])
		self._files_selected = FilesModel(json_dict["files_model"])

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def status(self):
		return self._status

	# -------------------------------------------------------------------------
	def name(self):
		return self._name

	# -------------------------------------------------------------------------
	def destinationFile(self):
		return self._destination_file
	
	# -------------------------------------------------------------------------
	def filesSelected(self):
		return self._files_selected
	
	# -------------------------------------------------------------------------
	def packerData(self):
		return self._packer_data

	###########################################################################
	# SETTERS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def setFilesSelected(self, files_selected):
		self._files_selected = files_selected
	
	# -------------------------------------------------------------------------
	def setDestinationFile(self, filename):
		self._destination_file = filename

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def data(self, index, role):
		if index.isValid():
			if index.row() == self.properties.STATUS.value:
				return self._status
			elif index.row() == self.properties.OUTPUT_NAME.value:
				return self._name
			elif index.row() == self.properties.SOURCE_FOLDER.value:
				return self._files_selected.rootPath()
			elif index.row() == self.properties.DESTINATION_FILE.value:
				return self._destination_file
	
	# -------------------------------------------------------------------------
	def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
		if index.isValid() and role == Qt.ItemDataRole.EditRole:
			if index.row() == self.properties.OUTPUT_NAME.value:
				self._name = value
			elif index.row() == self.properties.DESTINATION_FILE.value:
				path_no_ext = os.path.splitext(value)[0]
				ext = self._packer_data.extension()
				self._destination_file = path_no_ext + "." + ext
				self.dataChanged.emit(index, index)
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 5

	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
