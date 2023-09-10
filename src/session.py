"""
author: Marie-Neige Chapel
"""

# Python
import json
from typing import Self

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

# PackY
from task import Task
from task_encoder import TaskEncoder

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
	def taskAt(self, row: int)->Task:
		return self._data[row]
    
    # -------------------------------------------------------------------------
	def save(self):
		with open("test.json", "w") as output_file:
			json.dump(self._data[0], output_file, cls=TaskEncoder)
    
    # -------------------------------------------------------------------------
	#def load():
