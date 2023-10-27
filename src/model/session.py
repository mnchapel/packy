"""
author: Marie-Neige Chapel
"""

# Python
import os

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

# PackY
from model.task import Task

###############################################################################
class Session(QtCore.QAbstractTableModel):
    
	# -------------------------------------------------------------------------
	def __init__(self, json_dict = None):
		super(Session, self).__init__()

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__headers = ["", "Status", "Output", "Size"]
		self.__tasks = []

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.jsonInitialization(json_dict)

	# -------------------------------------------------------------------------
	def defaultInitialization(self):
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__name = ""
		self.__dirname = ""
	
	# -------------------------------------------------------------------------
	def jsonInitialization(self, json_dict: dict):
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__name = json_dict["session_name"]
		self.__dirname = json_dict["dirname"]

	###########################################################################
	# GETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def name(self):
		return self.__name
	
    # -------------------------------------------------------------------------
	def dirname(self):
		return self.__dirname

    # -------------------------------------------------------------------------
	def tasks(self):
		return self.__tasks

    # -------------------------------------------------------------------------
	def taskAt(self, row: int)->Task:
		return self.__tasks[row]

    # -------------------------------------------------------------------------
	def nbTasks(self):
		return len(self.__tasks)

    # -------------------------------------------------------------------------
	def nbCheckedTasks(self):
		return sum(1 for task in self.__tasks if task.isChecked())
	
    # -------------------------------------------------------------------------
	def taskRowById(self, id: int):
		for row_num, task in enumerate(self.__tasks):
			if task.id() == id:
				return row_num
		
		return -1

	###########################################################################
	# SETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def setName(self, path: str):
		self.__name = os.path.basename(path)
		self.__dirname = os.path.dirname(path)
	
    # -------------------------------------------------------------------------
	def setTasks(self, tasks):
		self.__tasks = tasks
		for task in self.__tasks:
			task.statusChanged.connect(self.emitDataChanged)

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################
		
    # -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return len(self.__tasks)

    # -------------------------------------------------------------------------
	def columnCount(self, index=None):
		return len(self.__headers)

    # -------------------------------------------------------------------------
	def data(self, index, role):
		if role == Qt.ItemDataRole.DisplayRole:
			task = self.__tasks[index.row()]

			if index.column() == 1:
				return task.statusUnicode()
			elif index.column() == 2:
				return task.name()
		
		elif role == Qt.ItemDataRole.TextAlignmentRole:
			if index.column() == 1:
				return Qt.AlignmentFlag.AlignCenter
			else:
				return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
		
		elif role == Qt.ItemDataRole.CheckStateRole:
			if index.column() == 0:
				task = self.__tasks[index.row()]
				return task.isChecked()
	
    # -------------------------------------------------------------------------
	def setData(self, index, value, role):
		if role == Qt.ItemDataRole.CheckStateRole:
			task = self.__tasks[index.row()]
			task.setChecked(value)
			return True
		
		return False
	
    # -------------------------------------------------------------------------
	def headerData(self, section: int, orientation, role):
		if role == Qt.ItemDataRole.DisplayRole:
			if orientation == Qt.Orientation.Horizontal:
				return self.__headers[section]
	
    # -------------------------------------------------------------------------
	def flags(self, index):
		return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable
	
    # -------------------------------------------------------------------------
	def insertRow(self)->int:
		row = self.rowCount()
		self.rowsAboutToBeInserted.emit(QtCore.QModelIndex(), row, row)
		self.createTask()
		self.rowsInserted.emit(QtCore.QModelIndex(), row, row)
		return row
	
    # -------------------------------------------------------------------------
	def createTask(self):

		task_id = 0
		if len(self.__tasks) > 0:
			task_id = self.__tasks[-1].id() + 1

		task = Task(task_id)
		self.__tasks.append(task)
		task.statusChanged.connect(self.emitDataChanged)

    # -------------------------------------------------------------------------
	def removeRow(self, row: int):
		if self.rowCount() > row and row >= 0:
			self.rowsAboutToBeRemoved.emit(QtCore.QModelIndex(), row, row)
			self.__tasks.pop(row)
			self.rowsRemoved.emit(QtCore.QModelIndex(), row, row)

    # -------------------------------------------------------------------------
	def emitDataChanged(self, task_id: int):
		row_num = self.taskRowById(task_id)

		if row_num != -1:
			self.dataChanged.emit(self.index(row_num, 1), self.index(row_num, 1))

    # -------------------------------------------------------------------------
	def emitTaskDataChanged(self, task_row: int):
		self.dataChanged.emit(self.index(task_row, 0), self.index(task_row, 0))
