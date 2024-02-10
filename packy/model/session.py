"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
from enum import Enum
from typing_extensions import override

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex, QCoreApplication

# PackY
from model.task import Task

###############################################################################
class SessionSerialKeys(Enum):
	NAME = "session_name"
	DIRNAME = "dirname"
	TASKS = "tasks"
	VERSION = "version"

###############################################################################
class Session(QAbstractTableModel):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __headers: 
	# __tasks:
	# __name: 
	# __dirname: 
	###########################################################################

	###########################################################################
	# SPECIAL METHODS
	###########################################################################
    
	# -------------------------------------------------------------------------
	def __init__(self, json_dict = None):
		super(Session, self).__init__()

		self.__headers = ["", "Status", "Output", "Size"]
		self.__tasks = []

		if json_dict is None:
			self.__defaultInitialization()
		else:
			self.__jsonInitialization(json_dict)

	###########################################################################
	# GETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def name(self) -> str:
		return self.__name
	
    # -------------------------------------------------------------------------
	def dirname(self) -> str:
		return self.__dirname
	
    # -------------------------------------------------------------------------
	def outputFile(self) -> str:
		return os.path.join(self.__dirname, self.__name)

    # -------------------------------------------------------------------------
	def tasks(self):
		return self.__tasks

    # -------------------------------------------------------------------------
	def taskAt(self, row: int) -> Task:
		return self.__tasks[row]

    # -------------------------------------------------------------------------
	def nbTasks(self) -> int:
		return len(self.__tasks)

    # -------------------------------------------------------------------------
	def nbCheckedTasks(self) -> int:
		return sum(1 for task in self.__tasks if task.isChecked())
	
    # -------------------------------------------------------------------------
	def taskRowById(self, id: int) -> int:
		for row_num, task in enumerate(self.__tasks):
			if task.id() == id:
				return row_num
		
		return -1

	###########################################################################
	# SETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def setName(self, path: str) -> None:
		raw_basename = os.path.basename(path).removesuffix(".json")
		self.__name = raw_basename + ".json"
		self.__dirname = os.path.dirname(path)
	
    # -------------------------------------------------------------------------
	def setTasks(self, tasks) -> None:
		self.__tasks = tasks
		for task in self.__tasks:
			task.statusChanged.connect(self.emitDataChanged)

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################
		
    # -------------------------------------------------------------------------
	@override
	def rowCount(self, index: QModelIndex = None) -> int:
		return len(self.__tasks)

    # -------------------------------------------------------------------------
	@override
	def columnCount(self, index: QModelIndex = None) -> int:
		return len(self.__headers)

    # -------------------------------------------------------------------------
	@override
	def data(self, index: QModelIndex, role) -> (QModelIndex|None):
		match role:
			case Qt.ItemDataRole.DisplayRole:
				return self.dataDisplayRole(index)
			case Qt.ItemDataRole.TextAlignmentRole:
				return self.dataTextAlignmentRole(index)
			case Qt.ItemDataRole.CheckStateRole:
				return self.dataCheckStateRole(index)
	
    # -------------------------------------------------------------------------
	@override
	def dataDisplayRole(self, index: QModelIndex) -> (QModelIndex|None):
		task = self.__tasks[index.row()]

		match index.column():
			case 1:
				return task.statusUnicode()
			case 2:
				return task.destBasename()
	
    # -------------------------------------------------------------------------
	@override
	def dataTextAlignmentRole(self, index: QModelIndex) -> (QModelIndex|None):
		if index.column() == 1:
			return Qt.AlignmentFlag.AlignCenter
		else:
			return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
		
    # -------------------------------------------------------------------------
	@override
	def dataCheckStateRole(self, index) -> (QModelIndex|None):
		if index.column() == 0:
			task = self.__tasks[index.row()]
			return task.isChecked()
	
    # -------------------------------------------------------------------------
	@override
	def setData(self, index, value, role) -> bool:
		if role == Qt.ItemDataRole.CheckStateRole:
			task = self.__tasks[index.row()]
			task.setChecked(value)
			return True
		
		return False
	
    # -------------------------------------------------------------------------
	@override
	def headerData(self, section: int, orientation, role) -> (str|None):
		if role == Qt.ItemDataRole.DisplayRole:
			if orientation == Qt.Orientation.Horizontal:
				return self.__headers[section]
	
    # -------------------------------------------------------------------------
	@override
	def flags(self, index) -> Qt.ItemFlag:
		return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable
	
    # -------------------------------------------------------------------------
	@override
	def insertRow(self)->int:
		row = self.rowCount()
		self.rowsAboutToBeInserted.emit(QtCore.QModelIndex(), row, row)
		self.createTask()
		self.rowsInserted.emit(QtCore.QModelIndex(), row, row)
		return row
	
    # -------------------------------------------------------------------------
	def createTask(self) -> None:

		task_id = 0
		if len(self.__tasks) > 0:
			task_id = self.__tasks[-1].id() + 1

		task = Task(task_id)
		self.__tasks.append(task)
		task.statusChanged.connect(self.emitDataChanged)

    # -------------------------------------------------------------------------
	def removeRow(self, row: int) -> None:
		if self.rowCount() > row and row >= 0:
			self.rowsAboutToBeRemoved.emit(QtCore.QModelIndex(), row, row)
			self.__tasks.pop(row)
			self.rowsRemoved.emit(QtCore.QModelIndex(), row, row)

    # -------------------------------------------------------------------------
	def serialize(self) -> dict:
		dict = {}

		dict[SessionSerialKeys.NAME.value] = self.__name
		dict[SessionSerialKeys.DIRNAME.value] = self.__dirname
		dict[SessionSerialKeys.TASKS.value] = self.__tasks
		dict[SessionSerialKeys.VERSION.value] = QCoreApplication.applicationVersion()

		return dict

	###########################################################################
	# PUBLIC SLOTS
	###########################################################################

    # -------------------------------------------------------------------------
	def emitDataChanged(self, task_id: int) -> None:
		row = self.taskRowById(task_id)

		if row != -1:
			col = 1
			self.dataChanged.emit(self.index(row, col), self.index(row, col))
	
    # -------------------------------------------------------------------------
	def emitSuffixChanged(self) -> None:
			first_row = 0
			last_row = self.rowCount()
			col = 2
			self.dataChanged.emit(self.index(first_row, col), self.index(last_row, col))

			for task in self.__tasks:
				task.dataChanged.emit(task.index(0, 0), task.index(task.rowCount() - 1, 0))

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __defaultInitialization(self):
		self.__name = ""
		self.__dirname = ""
	
	# -------------------------------------------------------------------------
	def __jsonInitialization(self, json_dict: dict):
		self.__name = json_dict[SessionSerialKeys.NAME.value]
		self.__dirname = json_dict[SessionSerialKeys.DIRNAME.value]
