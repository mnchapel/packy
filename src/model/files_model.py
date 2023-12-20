"""
author: Marie-Neige Chapel
"""

# Python
import os

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QModelIndex, QDir
from PyQt6.QtGui import QFileSystemModel

###############################################################################
class FilesModel(QFileSystemModel):

	###########################################################################
	# MEMBER VARIABLES
	#
	# * __check_state_items: a dict . If an item is not in the dict, its value is
	#   Qt.CheckState.Unchecked.value by default.
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, json_dict: dict = None, parent=None):
		super(FilesModel, self).__init__()

		self.__init(json_dict)

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def checks(self):
		return self.__check_state_items

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
	def listNewItems(self, dir_path: str):
		for root, dirs, files in os.walk(dir_path):
			for name in files:
				item = os.path.join(root, name).replace("\\","/")
				if item not in self.__check_state_items:
					print(f"[FilesModel][checkIntegrity] the item {item} has been added.")
			# for name in dirs:
			# 	item = os.path.join(root, name)
			# 	print(f"[FilesModel][checkIntegrity] the dir {item}")
			# 	if item not in self.__check_state_items:
			# 		print(f"[FilesModel][checkIntegrity] the item {item} has been added.")

	# -------------------------------------------------------------------------
	def serialize(self):
		dict = {}

		dict["root_path"] = self.rootPath()
		dict["check"] = self.__checksToStr()

		return dict

	# -------------------------------------------------------------------------
	def checkIntegrity(self):
		print("[FilesModel][checkIntegrity] starts")
		for item in self.__check_state_items:
			if self.__isItemChecked(item):
				# Removed item?
				if not self.__doesExists(item):
					print(f"[FilesModel][checkIntegrity] the item {item} doesn't exist anymore.")
				# Added item?
				elif os.path.isdir(item):
					self.listNewItems(item)
				elif item in self.__added_items:
					print(f"[FilesModel][checkIntegrity] the item {item} has been checked automatically.")
		print("[FilesModel][checkIntegrity] ends")

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init(self, json_dict: dict):

		self.__added_items = []

		if json_dict is None:
			self.__defaultInit()
		else:
			self.__jsonInit(json_dict)

		self.__initFilter()
		self.rowsInserted.connect(self.__checkIfAddedItems)

	# -------------------------------------------------------------------------
	def __initFilter(self):
		filter = self.filter()
		self.setFilter(filter | QDir.Filter.Hidden)

	# -------------------------------------------------------------------------
	def __defaultInit(self):
		self.__check_state_items = {}
	
	# -------------------------------------------------------------------------
	def __jsonInit(self, json_dict: dict):
		self.setRootPath(json_dict["root_path"])
		self.__check_state_items = json_dict["check"]
		
		self.checkIntegrity()			
	
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
	
	# PRIVATE SLOTS

	# -------------------------------------------------------------------------
	def __checkIfAddedItems(self, parent: QModelIndex, first: int, last: int):
		for i in range(first, last + 1):
			child = self.index(i, 0, parent)
			if self.__isItemUnchecked(child):
				print(f"[__checkIfAddedItems] the item {self.filePath(child)} is new for the model.")
				self.__added_items.append(self.filePath(child))
			# print(f"[__checkIfAddedItems] new item {self.filePath(child)} and is checked? {self.__isItemChecked(child)}")
