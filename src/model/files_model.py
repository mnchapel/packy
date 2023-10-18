"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QFileSystemModel

###############################################################################
class FilesModel(QFileSystemModel):

	# -------------------------------------------------------------------------
	def __init__(self, json_dict: dict = None, parent=None):
		super(FilesModel, self).__init__()

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.jsonInitialization(json_dict)

	# -------------------------------------------------------------------------
	def defaultInitialization(self):
		self._checks = {}
	
	# -------------------------------------------------------------------------
	def jsonInitialization(self, json_dict: dict):
		self.setRootPath(json_dict["root_path"])
		self._checks = json_dict["check"]

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def checks(self):
		return self._checks

	# -------------------------------------------------------------------------
	def checksToStr(self):
		return {str(key): value for key, value in self._checks.items()}

	###########################################################################
	# SETTERS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def setChecks(self, checks):
		self._checks = checks

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role = Qt.ItemDataRole.DisplayRole):
		if role != Qt.ItemDataRole.CheckStateRole:
			return QFileSystemModel.data(self, index, role)
		else:
			if index.column() == 0:
				return self.checkState(index)
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index: QModelIndex, value, role):
		match role:
			case Qt.ItemDataRole.CheckStateRole:
				if index.column() == 0:
					self._checks[self.filePath(index)] = value

					for i in range(self.rowCount(index)):
						child_index = self.index(i, 0, index)
						self.setData(child_index, value, role)
					
					self.dataChanged.emit(index, index)
					return True
				else:
					print("[FilesModel] wrong index.column()")
					return False
			case _:
				print("[FilesModel] default case")
				return QFileSystemModel.setData(self, index, value, role)
			
	# -------------------------------------------------------------------------
	# @override
	def flags(self, index):
		return QFileSystemModel.flags(self, index) | Qt.ItemFlag.ItemIsUserCheckable
	
	# -------------------------------------------------------------------------
	def checkState(self, index):
		if self.filePath(index) in self._checks:
			return self._checks[self.filePath(index)]
		else:
			return 0
