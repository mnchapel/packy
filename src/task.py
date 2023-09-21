"""
author: Marie-Neige Chapel
"""

# Python
import json
from enum import Enum

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from files_model import FilesModel

# PackY
from packer_data import PackerData

class Task(QtCore.QAbstractListModel):
	
	# -------------------------------------------------------------------------
	def __init__(self):
		super(Task, self).__init__()
		
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.properties = Enum("TaskProperties", [
			"STATUS",
			"OUTPUT_NAME",
			"OUTPUT_FOLDER",
			"PACKER_TYPE"
		])

		self._status = "Nothing"
		self._output_folder = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.DownloadLocation)
		self._name = "output_name"
		self._packer_data = PackerData()
		self._files_selected = FilesModel(self._output_folder)

	# -------------------------------------------------------------------------
	def status(self):
		return self._status

	# -------------------------------------------------------------------------
	def name(self):
		return self._name
	
	# -------------------------------------------------------------------------
	def filesSelected(self):
		return self._files_selected
	
	# -------------------------------------------------------------------------
	def setFilesSelected(self, files_selected):
		self._files_selected = files_selected
	
	# -------------------------------------------------------------------------
	def packerData(self):
		return self._packer_data

	# -------------------------------------------------------------------------
	def data(self, index, role):
		if index.isValid():
			if index.row() == self.properties.STATUS.value:
				return self._status
			elif index.row() == self.properties.OUTPUT_NAME.value:
				return self._name
			elif index.row() == self.properties.OUTPUT_FOLDER.value:
				return self._output_folder
	
	# -------------------------------------------------------------------------
	def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
		if index.isValid() and role == Qt.ItemDataRole.EditRole:
			if index.row() == self.properties.OUTPUT_NAME.value:
				self._name = value
			elif index.row() == self.properties.OUTPUT_FOLDER.value:
				self._output_folder = value
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 4

	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
