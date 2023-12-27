"""
author: Marie-Neige Chapel
"""

# Python
import os
import re
from datetime import date
from enum import Enum, auto

# PyQt
from PyQt6.QtCore import Qt, QSettings, QStandardPaths, QAbstractListModel, pyqtSignal

# PackY
from model.files_model import FilesModel
from model.packer_data import PackerData
from model.preferences import PreferencesTask, PreferencesKeys

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
		
	statusChanged = pyqtSignal(int)

	# -------------------------------------------------------------------------
	def __init__(self, id:int, json_dict = None) -> None:
		super(Task, self).__init__()
		
		# ----------------
		# MEMBER VARIABLES
		# ----------------
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

	# # -------------------------------------------------------------------------
	def initStaticMembers(self) -> None:
		if not hasattr(Task, "funcDstSuffix"):
			settings: QSettings = QSettings()
			suffix_value = settings.value(PreferencesKeys.TASK_SUFFIX.value, type = int)
			self.updateDestSuffix(PreferencesTask(suffix_value))
			

	# -------------------------------------------------------------------------
	def defaultInitialization(self) -> None:
		qt_folder_location = QStandardPaths.StandardLocation.DownloadLocation

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__checked = Qt.CheckState.Checked
		self.__packer_data = PackerData()
		self.__files_selected = FilesModel()
		self.__dest_raw_basename = "output"
		self.__dest_folder = QStandardPaths.writableLocation(qt_folder_location)
		self.__files_selected.setRootPath(self.__dest_folder)
	
	# -------------------------------------------------------------------------
	def deserialization(self, json_dict: dict) -> None:
		self.__id = json_dict["id"]
		self.__checked = json_dict["checked"]
		self.__packer_data = PackerData(json_dict["packer_data"])
		self.__files_selected = FilesModel(json_dict["files_model"])
		self.__dest_raw_basename = json_dict["dst_raw_basename"]
		self.__dest_folder = json_dict["dst_folder"]

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
				print("[Task][updateDestSuffix] value not recognized.")
		
		Task.funcDstSuffix = func_dst_suffix

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
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
	def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
		if index.isValid() and role == Qt.ItemDataRole.EditRole:
			match index.row():
				case TaskProperties.DST_BASENAME.value:
					self.dataChanged.emit(index, index)
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
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

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __suffixId(self) -> str:
		# return "_id"
	
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

	# -------------------------------------------------------------------------
	def serialize(self) -> dict:
		dict = {}

		dict["id"] = self.__id
		dict["checked"] = self.__checked
		dict["files_model"] = self.__files_selected
		dict["packer_data"] = self.__packer_data
		dict["dst_raw_basename"] = self.__dest_raw_basename
		dict["dst_folder"] = self.__dest_folder

		return dict
