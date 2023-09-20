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
from task import Task

class Session(QtCore.QAbstractTableModel):
    
	# -------------------------------------------------------------------------
	def __init__(self, data=None):
		super(Session, self).__init__()
        
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._data = [] if data is None else data
		self._headers = ["Status", "Output", "Progress"]
		self._name = ""
		self._dirname = ""

    # -------------------------------------------------------------------------
	def name(self):
		return self._name

    # -------------------------------------------------------------------------
	def setName(self, path: str):
		self._name = os.path.basename(path)
		self._dirname = os.path.dirname(path)

    # -------------------------------------------------------------------------
	def data(self, index, role):
		if role == Qt.ItemDataRole.DisplayRole:
			task = self._data[index.row()]

			value = ""
			if index.column() == 0:
				value = task.status()
			elif index.column() == 1:
				value = task.output()

			return str(value)
	
    # -------------------------------------------------------------------------
	def headerData(self, section: int, orientation, role):
		if role == Qt.ItemDataRole.DisplayRole:
			if orientation == Qt.Orientation.Horizontal:
				return self._headers[section]
		
    # -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return len(self._data)

    # -------------------------------------------------------------------------
	def columnCount(self, index=None):
		return len(self._headers)
	
    # -------------------------------------------------------------------------
	def insertRow(self, data)->int:
		row = self.rowCount()
		self.rowsAboutToBeInserted.emit(QtCore.QModelIndex(), row, row)
		self.createTask()
		self.rowsInserted.emit(QtCore.QModelIndex(), row, row)
		return row
	
    # -------------------------------------------------------------------------
	def createTask(self):
		task = Task()
		self._data.append(task)

    # -------------------------------------------------------------------------
	def removeRow(self, row: int):
		if self.rowCount() > row and row >= 0:
			self.rowsAboutToBeRemoved.emit(QtCore.QModelIndex(), row, row)
			self._data.pop(row)
			self.rowsRemoved.emit(QtCore.QModelIndex(), row, row)

    # -------------------------------------------------------------------------
	def tasks(self):
		return self._data

    # -------------------------------------------------------------------------
	def taskAt(self, row: int)->Task:
		return self._data[row]
    
    # -------------------------------------------------------------------------
	def load(self, filename: str):
		path = filename
		# path = os.path.join(self._dirname, self._name + ".json")
		with open(path, "r") as input_file:
			data = input_file.read()
			print("data = ", data)
			# session = json.load(input_file)
			# d = json.JSONDecoder()
			# dict = d.decode(data)
			# print("")
			# print("dict = ", dict)
			obj = json.loads(data)
			print("")
			print("obj = ", obj)

