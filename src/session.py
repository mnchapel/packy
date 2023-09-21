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
		self._tasks = [] if data is None else data
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
			task = self._tasks[index.row()]

			value = ""
			if index.column() == 0:
				value = task.status()
			elif index.column() == 1:
				value = task.name()

			return str(value)
	
    # -------------------------------------------------------------------------
	def headerData(self, section: int, orientation, role):
		if role == Qt.ItemDataRole.DisplayRole:
			if orientation == Qt.Orientation.Horizontal:
				return self._headers[section]
		
    # -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return len(self._tasks)

    # -------------------------------------------------------------------------
	def columnCount(self, index=None):
		return len(self._headers)
	
    # -------------------------------------------------------------------------
	def insertRow(self, data)->int:
		row = self.rowCount()
		print("[insertRow] row = ", row)
		self.rowsAboutToBeInserted.emit(QtCore.QModelIndex(), row, row)
		self.createTask()
		self.rowsInserted.emit(QtCore.QModelIndex(), row, row)
		return row
	
    # -------------------------------------------------------------------------
	def createTask(self):
		task = Task()
		self._tasks.append(task)

    # -------------------------------------------------------------------------
	def removeRow(self, row: int):
		if self.rowCount() > row and row >= 0:
			self.rowsAboutToBeRemoved.emit(QtCore.QModelIndex(), row, row)
			self._tasks.pop(row)
			self.rowsRemoved.emit(QtCore.QModelIndex(), row, row)

    # -------------------------------------------------------------------------
	def tasks(self):
		return self._tasks

    # -------------------------------------------------------------------------
	def taskAt(self, row: int)->Task:
		return self._tasks[row]
	
    # -------------------------------------------------------------------------
	def setTasks(self, tasks):
		row = len(tasks) - 1
		print("[setTasks] row = ", row)
		self.rowsAboutToBeInserted.emit(QtCore.QModelIndex(), 0, row)
		self._tasks = tasks
		self.rowsInserted.emit(QtCore.QModelIndex(), 0, row)

    # -------------------------------------------------------------------------
	def nbTasks(self):
		return len(self._tasks)
