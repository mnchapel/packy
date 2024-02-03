"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
from enum import Enum

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QModelIndex, QDir
from PyQt6.QtGui import QFileSystemModel

# PackY
from model.warnings import Warnings

###############################################################################
class FilesModelSerialKeys(Enum):
	ROOT_PATH = "root_path"
	CHECK = "check"

###############################################################################
class FilesModel(QFileSystemModel):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __check_state_items: a dict with the check state for files and
	#                      directories. If an item is not in the dict,
	#                      its value is Qt.CheckState.Unchecked.value by
	#                      default.
	# __warnings: an object which contains the modifications (added/removed
	#             items) between the model and the current selection.
	###########################################################################

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, json_dict: dict = None, parent=None):
		super(FilesModel, self).__init__()

		self.__init(json_dict)

	# -------------------------------------------------------------------------
	def __repr__(self) -> str:
		return f"files_model: root_path = {self.rootPath()}, check = {{{self.__checksToStr()}}}"
	
	# -------------------------------------------------------------------------
	def __eq__(self, other):
		return self.rootPath() == other.rootPath() and \
		self.__check_state_items == other.__check_state_items

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def checks(self):
		return self.__check_state_items
	
	# -------------------------------------------------------------------------
	def warnings(self):
		return self.__warnings

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	# @override
	def data(self, index: QModelIndex, role = Qt.ItemDataRole.DisplayRole):
		match role:
			case Qt.ItemDataRole.CheckStateRole:
				if index.column() == 0:
					return self.__checkState(index)
			case _:
				return QFileSystemModel.data(self, index, role)
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index: QModelIndex, value, role: Qt.ItemDataRole):
		match role:
			case Qt.ItemDataRole.CheckStateRole:
				if index.column() == 0:
					self.__check_state_items[self.filePath(index)] = value
					self.dataChanged.emit(index, index)

					self.__updateChildFiles(index, value, role)
					self.__updateParentFiles(index, value)

					return True
				else:
					QtCore.qDebug(f"Wrong index.column() = {index.column()}. Index column should be equal to 0.")
					return False
			case _:
				return QFileSystemModel.setData(self, index, value, role)
			
	# -------------------------------------------------------------------------
	# @override
	def flags(self, index):
		return QFileSystemModel.flags(self, index) | Qt.ItemFlag.ItemIsUserCheckable
	
	# -------------------------------------------------------------------------
	# @override
	def setRootPath(self, path: str) -> QModelIndex:
		self.__check_state_items.clear()
		self.__warnings.clear()

		return QFileSystemModel.setRootPath(self, path)
	
	# -------------------------------------------------------------------------
	def listNewItems(self, dir_path: str):
		for root, dirs, files in os.walk(dir_path):
			for name in files:
				item = os.path.join(root, name).replace("\\","/")
				if item not in self.__check_state_items:
					self.__warnings.addAddedItem(item)

	# -------------------------------------------------------------------------
	def serialize(self):
		dict = {}

		dict[FilesModelSerialKeys.ROOT_PATH.value] = self.rootPath()
		dict[FilesModelSerialKeys.CHECK.value] = self.__checksToStr()

		return dict

	# -------------------------------------------------------------------------
	def checkIntegrity(self):
		for item in self.__check_state_items:
			if self.__isItemChecked(item):
				# Removed item?
				if not self.__doesExists(item):
					self.__warnings.addRemovedItem(item)
				# Added item?
				elif os.path.isdir(item):
					self.listNewItems(item)
				elif self.__warnings.isInAddedCandidateItems(item):
					self.__warnings.addAddedItem(item)
	
	# -------------------------------------------------------------------------
	def updateModel(self):
		removed_items = self.__warnings.removedItems()
		for item in removed_items:
			del self.__check_state_items[item]

		added_items = self.__warnings.addedItems()
		for item in added_items:
			self.__check_state_items[item] = Qt.CheckState.Checked.value
		
		self.__warnings.clear()

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init(self, json_dict: dict):

		self.__defaultInit()

		if json_dict is not None:
			self.__jsonInit(json_dict)

		self.__initFilter()
		self.rowsInserted.connect(self.__checkIfAddedItems)

	# -------------------------------------------------------------------------
	def __defaultInit(self):
		self.__check_state_items = {}
		self.__warnings = Warnings()
	
	# -------------------------------------------------------------------------
	def __jsonInit(self, json_dict: dict):
		self.setRootPath(json_dict[FilesModelSerialKeys.ROOT_PATH.value])
		self.__check_state_items = json_dict[FilesModelSerialKeys.CHECK.value]
		self.checkIntegrity()

	# -------------------------------------------------------------------------
	def __initFilter(self):
		filter = self.filter()
		self.setFilter(filter | QDir.Filter.Hidden)	
	
	# -------------------------------------------------------------------------
	def __updateChildFiles(self, index: QModelIndex, value, role: Qt.ItemDataRole):
		if value != Qt.CheckState.PartiallyChecked.value:
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

		if index_parent == QModelIndex():
			return
		if self.filePath(index_parent) == self.rootPath():
			return

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
	def __isItemChecked(self, item) -> bool:
		if self.__checkState(item) == Qt.CheckState.Checked.value:
			return True

		return False

	# -------------------------------------------------------------------------
	def __isItemPartiallyChecked(self, item) -> bool:
		if self.__checkState(item) == Qt.CheckState.PartiallyChecked.value:
			return True

		return False

	# -------------------------------------------------------------------------
	def __isItemUnchecked(self, item) -> bool:
		if self.__checkState(item) == Qt.CheckState.Unchecked.value:
			return True

		return False

	# -------------------------------------------------------------------------
	def __checkState(self, item) -> int:
		if isinstance(item, QModelIndex):
			return self.__checkStateIndex(item)
		elif isinstance(item, str):
			return self.__checkStatePath(item)

	# -------------------------------------------------------------------------
	def __checkStateIndex(self, index: QModelIndex) -> int:
		return self.__checkStatePath(self.filePath(index))
	
	# -------------------------------------------------------------------------
	def __checkStatePath(self, item_path: str) -> int:
		if item_path in self.__check_state_items:
			return self.__check_state_items[item_path]
		else:
			return Qt.CheckState.Unchecked.value
		
	# -------------------------------------------------------------------------
	def __updateCheckState(self, index: QModelIndex, check_state: Qt.CheckState) -> None:
		self.__check_state_items[self.filePath(index)] = check_state.value
		self.dataChanged.emit(index, index)

	# -------------------------------------------------------------------------
	def __checksToStr(self):
		return {str(key): value for key, value in self.__check_state_items.items()}
	
	# -------------------------------------------------------------------------
	def __doesExists(self, item_path: str) -> bool:
		if os.path.exists(item_path):
			return True
		
		return False

	# -------------------------------------------------------------------------
	def __checkIfAddedItems(self, parent: QModelIndex, first: int, last: int):
		for i in range(first, last + 1):
			child = self.index(i, 0, parent)
			if self.__isItemUnchecked(child):
				self.__warnings.addCandidateAddedItem(self.filePath(child))
