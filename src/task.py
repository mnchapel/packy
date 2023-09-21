"""
author: Marie-Neige Chapel
"""

# Python
import json
from enum import Enum
import os

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QStandardPaths
from files_model import FilesModel

# PackY
from packer_data import PackerData

###############################################################################
class Task(QtCore.QAbstractListModel):
	
	# -------------------------------------------------------------------------
	def __init__(self, packer_data = None):
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

		self._status = "Nothing"
		self._name = "output_name"

		if packer_data is None:
			self._packer_data = PackerData()
		else:
			self._packer_data = packer_data

		qt_folder_location = QStandardPaths.StandardLocation.DownloadLocation
		default_folder = QStandardPaths.writableLocation(qt_folder_location)
		self._files_selected = FilesModel(default_folder)
		self._destination_file = default_folder + "/output"

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
				self._destination_file = value
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 5

	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
