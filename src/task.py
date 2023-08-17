"""
author: Marie-Neige Chapel
"""

# Python
import json

# PyQt
from PyQt6 import QtCore

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
		self._output_folder = ""
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
		print(int(role))
		if index.isValid():
			if index.row() == 0:
				return self._status
			elif index.row() == 1:
				return self._output_name
			elif index.row() == 2:
				return self._packer
	
	# -------------------------------------------------------------------------
	def setData(self, index, value, role):
		print("set data")
	
	# -------------------------------------------------------------------------
	def rowCount(self, index=None):
		print("[Task] rowCount")
		return 3

	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
