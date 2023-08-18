"""
author: Marie-Neige Chapel
"""

# Python
import json
import os

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

# PackY
from packer import Packer

class Task(QtCore.QAbstractListModel):
	
	# -------------------------------------------------------------------------
	def __init__(self):
		super(Task, self).__init__()
		
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._status = "Nothing"
		self._output_folder = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.DownloadLocation)

		self._output_name = "output_name"
		self._packer = Packer()

	# -------------------------------------------------------------------------
	def status(self):
		return self._status

	# -------------------------------------------------------------------------
	def output(self):
		return self._output_name
	
	# -------------------------------------------------------------------------
	def data(self, index, role):
		if index.isValid():
			if index.row() == 0:
				return self._status
			elif index.row() == 1:
				return self._output_name
			elif index.row() == 2:
				return self._output_folder
	
	# -------------------------------------------------------------------------
	def setData(self, index, value, role):
		if index.isValid() and role == Qt.ItemDataRole.EditRole:
			if index.row() == 1:
				self._output_name = value
			elif index.row() == 2:
				self._output_folder = value
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 3

	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
