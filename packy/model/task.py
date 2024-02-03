"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
import re
from datetime import date
from enum import Enum, auto

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QStandardPaths, QAbstractListModel, pyqtSignal

# PackY
from model.files_model import FilesModel
from model.packer_data import PackerData
from model.preferences import PreferencesTask, PreferencesKeys
from utils.settings_access import packySettings

###############################################################################
class TaskSerialKeys(Enum):
	ID = "id"
	CHECKED = "checked"
	PACKER_DATA = "packer_data"
	FILES_SELECTED = "files_model"
	DEST_RAW_BASENAME = "dst_raw_basename"
	DEST_FOLDER = "dst_folder"

###############################################################################
class TaskProperties(Enum):
	STATUS = 0
	SRC_FOLDER = auto()
	DST_BASENAME = auto()
	DST_FILE = auto()
	PACKER_TYPE = auto()

###############################################################################
class TaskStatus(Enum):
	WAITING = 0
	SUCCESS = auto()
	ERROR = auto()

###############################################################################
class Task(QAbstractListModel):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __u_dash: dash unicode character to represent the waiting status.
	# __u_check: check unicode character to represent the success status.
	# __u_cross: cross unicode charater to represent the failed status.
	# __id: an integer.
	# __status: the current status of the task.
	# __checked: a flag indicating if the task is selected for running.
	# __packer_data: info about the packer.
	# __files_selected: items selected to be packed.
	# __dest_raw_basename: the output filename chosen by the user.
	# __dest_folder: the destination folder of the archive.
	# __files_selected:
	###########################################################################
		
	###########################################################################
	# SIGNALS
	###########################################################################

	statusChanged = pyqtSignal(int)

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, id:int, json_dict = None) -> None:
		super(Task, self).__init__()
		
		self.__u_dash = u'\u2014'
		self.__u_check = u'\u2713'
		self.__u_cross = u'\u2715'

		self.__id = id
		self.__status = TaskStatus.WAITING

		self.initStaticMembers()

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.deserialization(json_dict)

	# -------------------------------------------------------------------------
	def initStaticMembers(self) -> None:
		if not hasattr(Task, "funcDstSuffix"):
			settings = packySettings()
			suffix_value = settings.value(PreferencesKeys.TASK_SUFFIX.value, type = int)
			self.updateDestSuffix(PreferencesTask(suffix_value))
			
	# -------------------------------------------------------------------------
	def defaultInitialization(self) -> None:
		qt_folder_location = QStandardPaths.StandardLocation.DownloadLocation

		self.__checked = Qt.CheckState.Checked
		self.__packer_data = PackerData()
		self.__files_selected = FilesModel()
		self.__dest_raw_basename = "output"
		self.__dest_folder = QStandardPaths.writableLocation(qt_folder_location)
		self.__files_selected.setRootPath(self.__dest_folder)
	
	# -------------------------------------------------------------------------
	def deserialization(self, json_dict: dict) -> None:
		self.__id = json_dict[TaskSerialKeys.ID.value]
		self.__checked = json_dict[TaskSerialKeys.CHECKED.value]
		self.__packer_data = PackerData(json_dict[TaskSerialKeys.PACKER_DATA.value])
		self.__files_selected = FilesModel(json_dict[TaskSerialKeys.FILES_SELECTED.value])
		self.__dest_raw_basename = json_dict[TaskSerialKeys.DEST_RAW_BASENAME.value]
		self.__dest_folder = json_dict[TaskSerialKeys.DEST_FOLDER.value]

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def id(self) -> int:
		return self.__id

	# -------------------------------------------------------------------------
	def statusUnicode(self)->str:
		match self.__status:
			case TaskStatus.WAITING:
				return self.__u_dash
			case TaskStatus.SUCCESS:
				return self.__u_check
			case TaskStatus.ERROR:
				return self.__u_cross
			
	# -------------------------------------------------------------------------
	def destFile(self) -> str:
		dst_basename = self.destBasename()
		return os.path.join(self.__dest_folder, dst_basename)
			
	# -------------------------------------------------------------------------
	def rawDestFile(self) -> str:
		return os.path.join(self.__dest_folder, self.__dest_raw_basename)
	
	# -------------------------------------------------------------------------
	def destBasename(self) -> str:
		dst_suffix = Task.funcDstSuffix(self)
		extension = self.__packer_data.extension()
		return self.__dest_raw_basename + dst_suffix + "." + extension
	
	# -------------------------------------------------------------------------
	def destExtension(self) -> str:
		return self.__packer_data.extension()
	
	# -------------------------------------------------------------------------
	def filesSelected(self):
		return self.__files_selected
	
	# -------------------------------------------------------------------------
	def packerData(self):
		return self.__packer_data
	
	# -------------------------------------------------------------------------
	def isChecked(self) -> Qt.CheckState:
		return self.__checked
	
	# -------------------------------------------------------------------------
	def warnings(self):
		return self.__files_selected.warnings()

	###########################################################################
	# SETTERS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def setRawDstFile(self, value: str) -> None:
		self.__dest_folder = os.path.dirname(value)
		self.__dest_raw_basename = os.path.basename(value)
		
		first_row = 0
		last_row = self.rowCount() - 1
		self.dataChanged.emit(self.index(first_row, 0), self.index(last_row, 0))

	# -------------------------------------------------------------------------
	def setFilesSelected(self, files_selected):
		self.__files_selected = files_selected
	
	# -------------------------------------------------------------------------
	def setChecked(self, value:Qt.CheckState):
		self.__checked = value

	# -------------------------------------------------------------------------
	@staticmethod
	def updateDestSuffix(value):
		func_dst_suffix = Task.__suffixTimeStamp

		match value:
			case PreferencesTask.SUFFIX_CURR_DATE:
				func_dst_suffix = Task.__suffixTimeStamp
			case PreferencesTask.SUFFIX_VERSION_NUM:
				func_dst_suffix = Task.__suffixId
			case PreferencesTask.SUFFIX_NOTHING:
				func_dst_suffix = Task.__suffixNothing
			case _:
				msg = "value not recognized."
				QtCore.qWarning(msg)
		
		Task.funcDstSuffix = func_dst_suffix

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			match index.row():
				case TaskProperties.STATUS.value:
					return self.statusUnicode()
				case TaskProperties.SRC_FOLDER.value:
					return self.__files_selected.rootPath()
				case TaskProperties.DST_BASENAME.value:
					return self.destBasename()
				case TaskProperties.DST_FILE.value:
					return self.destFile()
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
		if index.isValid() and role == Qt.ItemDataRole.EditRole:
			match index.row():
				case TaskProperties.DST_BASENAME.value:
					self.dataChanged.emit(index, index)
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return len(TaskProperties)
	
	# -------------------------------------------------------------------------
	def initStatus(self):
		self.__status = TaskStatus.WAITING
		self.statusChanged.emit(self.__id)

	# -------------------------------------------------------------------------
	def updateStatus(self, status: TaskStatus):
		self.__status = status
		self.statusChanged.emit(self.__id)

	# -------------------------------------------------------------------------
	def checkIntegrity(self):
		self.__files_selected.checkIntegrity()

	# -------------------------------------------------------------------------
	def serialize(self) -> dict:
		dict = {}

		dict[TaskSerialKeys.ID.value] = self.__id
		dict[TaskSerialKeys.CHECKED.value] = self.__checked.value
		dict[TaskSerialKeys.FILES_SELECTED.value] = self.__files_selected
		dict[TaskSerialKeys.PACKER_DATA.value] = self.__packer_data
		dict[TaskSerialKeys.DEST_RAW_BASENAME.value] = self.__dest_raw_basename
		dict[TaskSerialKeys.DEST_FOLDER.value] = self.__dest_folder

		return dict

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __suffixId(self) -> str:
		last_id = self.__findLastSuffixId()
		suffix = "_" + str(last_id + 1)

		return suffix

	# -------------------------------------------------------------------------
	def __findLastSuffixId(self) -> int:
		regex = self.__dest_raw_basename + "_\d+." + self.__packer_data.extension()

		last_id = -1
		for filename in os.listdir(self.__dest_folder):
			if re.search(regex, filename):
				basename_no_ext = os.path.splitext(filename)[0]
				id = basename_no_ext.rsplit("_", 1)[1]
				last_id = int(id) if last_id < int(id) else last_id
		
		return last_id
	
	# -------------------------------------------------------------------------
	def __suffixTimeStamp(self) -> str:
		return date.today().strftime("%Y_%m_%d")
	
	# -------------------------------------------------------------------------
	def __suffixNothing(self) -> str:
		return ""
