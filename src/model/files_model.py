"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QModelIndex, QDir
from PyQt6.QtGui import QFileSystemModel

###############################################################################
class FilesModel(QFileSystemModel):

	# -------------------------------------------------------------------------
	def __init__(self, json_dict: dict = None, parent=None):
		super(FilesModel, self).__init__()

		filter = self.filter()
		self.setFilter(filter | QDir.Filter.Hidden)

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.jsonInitialization(json_dict)

	# -------------------------------------------------------------------------
	def defaultInitialization(self):
		self.__checks = {}
	
	# -------------------------------------------------------------------------
	def jsonInitialization(self, json_dict: dict):
		self.setRootPath(json_dict["root_path"])
		self.__checks = json_dict["check"]

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def checks(self):
		return self.__checks

	###########################################################################
	# SETTERS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def setChecks(self, checks):
		self.__checks = checks

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
				return self.__checkState(index)
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
		match role:
			case Qt.ItemDataRole.CheckStateRole:
				if index.column() == 0:
					self.__checks[self.filePath(index)] = value
					self.dataChanged.emit(index, index)

					self.__updateChildFiles(index, value, role)
					self.__updateParentFiles(index, value)

					return True
				else:
					QtCore.qDebug(f"Wrong index.column() = {index.column()}")
					return False
			case _:
				return QFileSystemModel.setData(self, index, value, role)
	
	# -------------------------------------------------------------------------
	def __updateChildFiles(self, index: QModelIndex, value, role: Qt.ItemDataRole):
		for i in range(self.rowCount(index)):
			child_index = self.index(i, 0, index)
			self.setData(child_index, value, role)

	# -------------------------------------------------------------------------
	def __updateParentFiles(self, index: QModelIndex, value):
		match value:
			case Qt.CheckState.Checked.value:
				self.__propagateCheckToParents(index)
			case Qt.CheckState.Unchecked.value:
				self.__propagateUncheckToParents(index)
			case _:
				QtCore.qDebug(f"The Qt.CheckState value {value} should not appear in this function.")
			
	# -------------------------------------------------------------------------
	def __propagateCheckToParents(self, index: QModelIndex):
		index_parent = index.parent()
		if index_parent != QModelIndex():
			
			all_siblings_checked = True
			for i in range(self.rowCount(index_parent)):
				index_sibling = self.index(i, 0, index_parent)
				if self.__checkState(index_sibling) != Qt.CheckState.Checked.value:
					all_siblings_checked = False
			
			if all_siblings_checked:
				self.__updateCheckState(index_parent, Qt.CheckState.Checked)
				self.__propagateCheckToParents(index_parent)
			elif self.__checkState(index_parent) == Qt.CheckState.Unchecked.value:
				self.__updateCheckState(index_parent, Qt.CheckState.PartiallyChecked)
				self.__propagateCheckToParents(index_parent)
	
	# -------------------------------------------------------------------------
	def __propagateUncheckToParents(self, index: QModelIndex) -> None:
		index_parent = index.parent()

		if self.__checkState(index_parent) == Qt.CheckState.Unchecked.value:
			return
		
		at_least_one_selected_child: bool = False

		for i in range(self.rowCount(index_parent)):
			index_child = self.index(i, 0, index_parent)
			if self.__checkState(index_child) != Qt.CheckState.Unchecked.value:
				at_least_one_selected_child = True
				break

		new_check_state = Qt.CheckState.Unchecked
		if at_least_one_selected_child:
			new_check_state = Qt.CheckState.PartiallyChecked

		self.__updateCheckState(index_parent, new_check_state)
		self.__propagateUncheckToParents(index_parent)
			
	# -------------------------------------------------------------------------
	# @override
	def flags(self, index):
		return QFileSystemModel.flags(self, index) | Qt.ItemFlag.ItemIsUserCheckable
	
	# -------------------------------------------------------------------------
	def __checkState(self, index) -> int:
		if self.filePath(index) in self.__checks:
			return self.__checks[self.filePath(index)]
		else:
			return Qt.CheckState.Unchecked.value
		
	# -------------------------------------------------------------------------
	def __updateCheckState(self, index: QModelIndex, check_state: Qt.CheckState) -> None:
		self.__checks[self.filePath(index)] = check_state.value
		self.dataChanged.emit(index, index)
		
	# -------------------------------------------------------------------------
	def serialize(self):
		dict = {}

		dict["root_path"] = self.rootPath()
		dict["check"] = self.__checksToStr()

		return dict

	# -------------------------------------------------------------------------
	def __checksToStr(self):
		return {str(key): value for key, value in self.__checks.items()}
