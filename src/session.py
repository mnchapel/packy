"""
author: Marie-Neige Chapel
"""

# Python
import os

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

# PackY
from task import Task

###############################################################################
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

	###########################################################################
	# GETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def name(self):
		return self._name
	
    # -------------------------------------------------------------------------
	def dirname(self):
		return self._dirname

    # -------------------------------------------------------------------------
	def tasks(self):
		return self._tasks

    # -------------------------------------------------------------------------
	def taskAt(self, row: int)->Task:
		return self._tasks[row]

    # -------------------------------------------------------------------------
	def nbTasks(self):
		return len(self._tasks)

	###########################################################################
	# SETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def setName(self, path: str):
		self._name = os.path.basename(path)
		self._dirname = os.path.dirname(path)
	
    # -------------------------------------------------------------------------
	def setTasks(self, tasks):
		self._tasks = tasks

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

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
		elif role == Qt.ItemDataRole.TextAlignmentRole:
			if index.column() == 0:
				return Qt.AlignmentFlag.AlignCenter
			else:
				return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
	
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
	def insertRow(self)->int:
		row = self.rowCount()
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
	def emitTaskDataChanged(self, task_row: int):
		self.dataChanged.emit(self.index(task_row, 0), self.index(task_row, 0))
