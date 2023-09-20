"""
author: Marie-Neige Chapel
"""

from PyQt6 import QtCore, QtGui

class FilesModel(QtGui.QFileSystemModel):

	# -------------------------------------------------------------------------
	def __init__(self, parent=None):
		super(FilesModel, self).__init__()
		self._checks = {}

	# -------------------------------------------------------------------------
	def checksToStr(self):
		return {str(key): str(value) for key, value in self._checks.items()}
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
		if role != QtCore.Qt.ItemDataRole.CheckStateRole:
			return QtGui.QFileSystemModel.data(self, index, role)
		else:
			if index.column() == 0:
				return self.checkState(index)
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index: QtCore.QModelIndex, value, role):	
		match role:
			case QtCore.Qt.ItemDataRole.CheckStateRole:
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
				return QtGui.QFileSystemModel.setData(self, index, value, role)
			
	# -------------------------------------------------------------------------
	# @override
	def flags(self, index):
		return QtGui.QFileSystemModel.flags(self, index) | QtCore.Qt.ItemFlag.ItemIsUserCheckable
	
	# -------------------------------------------------------------------------
	def checkState(self, index):
		if self.filePath(index) in self._checks:
			return self._checks[self.filePath(index)]
		else:
			return QtCore.Qt.CheckState.Unchecked
