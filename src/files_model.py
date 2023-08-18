# from typing_extensions import override
from PyQt6 import QtCore, QtGui

class FilesModel(QtGui.QFileSystemModel):

	# -------------------------------------------------------------------------
	def __init__(self, parent=None):
		super(FilesModel, self).__init__()
		self._checks = {}
	
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
	def setData(self, index, value, role):		
		if role == QtCore.Qt.ItemDataRole.CheckStateRole and index.column() == 0:
			self._checks[index] = value
			return True
		else:
			return QtGui.QFileSystemModel.setData(self, index, value, role)
			
	# -------------------------------------------------------------------------
	# @override
	def flags(self, index):
		return QtGui.QFileSystemModel.flags(self, index) | QtCore.Qt.ItemFlag.ItemIsUserCheckable
	
	# -------------------------------------------------------------------------
	def checkState(self, index):
		if index in self._checks:
			return self._checks[index]
		else:
			return QtCore.Qt.CheckState.Unchecked
