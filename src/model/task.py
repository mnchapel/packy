"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
from enum import Enum

# PyQt
from PyQt6.QtCore import Qt, QStandardPaths, QAbstractListModel, pyqtSignal

# PackY
from model.files_model import FilesModel
from model.packer_data import PackerData

###############################################################################
class TaskProperties(Enum):
	STATUS = 0
	OUTPUT_NAME = 1
	SOURCE_FOLDER = 2
	DESTINATION_FILE = 3
	PACKER_TYPE = 4

###############################################################################
class TaskStatus(Enum):
	WAITING = 0
	SUCCESS = 1
	ERROR = 2

###############################################################################
class Task(QAbstractListModel):
		
	statusChanged = pyqtSignal(int)
	
	# -------------------------------------------------------------------------
	def __init__(self, id:int, json_dict = None):
		super(Task, self).__init__()
		
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__u_dash = u'\u2014'
		self.__u_check = u'\u2713'
		self.__u_cross = u'\u2715'

		self.__id = id
		self.__status = TaskStatus.WAITING

		if json_dict is None:
			self.defaultInitialization()
		else:
			self.jsonInitialization(json_dict)

	# -------------------------------------------------------------------------
	def defaultInitialization(self):
		qt_folder_location = QStandardPaths.StandardLocation.DownloadLocation
		default_folder = QStandardPaths.writableLocation(qt_folder_location)

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__checked = Qt.CheckState.Checked
		self.__packer_data = PackerData()
		self.__files_selected = FilesModel()
		self.__files_selected.setRootPath(default_folder)
		self.__destination_file = default_folder + "/output." + self.__packer_data.extension()
	
	# -------------------------------------------------------------------------
	def jsonInitialization(self, json_dict: dict):
		self.__id = json_dict["id"]
		self.__checked = json_dict["checked"]
		self.__destination_file = json_dict["destination_file"]
		self.__packer_data = PackerData(json_dict["packer_data"])
		self.__files_selected = FilesModel(json_dict["files_model"])

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def id(self):
		return self.__id

	# -------------------------------------------------------------------------
	def name(self)->str:
		return os.path.basename(self.__destination_file)

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
	def destinationFile(self):
		return self.__destination_file
	
	# -------------------------------------------------------------------------
	def filesSelected(self):
		return self.__files_selected
	
	# -------------------------------------------------------------------------
	def packerData(self):
		return self.__packer_data
	
	# -------------------------------------------------------------------------
	def isChecked(self)->Qt.CheckState:
		return self.__checked

	###########################################################################
	# SETTERS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def setFilesSelected(self, files_selected):
		self.__files_selected = files_selected
	
	# -------------------------------------------------------------------------
	def setDestinationFile(self, filename):
		self.__destination_file = filename
	
	# -------------------------------------------------------------------------
	def setChecked(self, value:Qt.CheckState):
		self.__checked = value

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def data(self, index, role):
		if index.isValid():
			if index.row() == TaskProperties.STATUS.value:
				return self.statusUnicode()
			elif index.row() == TaskProperties.OUTPUT_NAME.value:
				return os.path.basename(self.__destination_file)
			elif index.row() == TaskProperties.SOURCE_FOLDER.value:
				return self.__files_selected.rootPath()
			elif index.row() == TaskProperties.DESTINATION_FILE.value:
				return self.__destination_file
	
	# -------------------------------------------------------------------------
	def setData(self, index, value, role = Qt.ItemDataRole.EditRole):
		if index.isValid() and role == Qt.ItemDataRole.EditRole:
			if index.row() == TaskProperties.OUTPUT_NAME.value:
				self.__name = value
			elif index.row() == TaskProperties.DESTINATION_FILE.value:
				path_no_ext = os.path.splitext(value)[0]
				ext = self.__packer_data.extension()
				self.__destination_file = path_no_ext + "." + ext
			return True
		else:
			return False
	
	# -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 5
	
	# -------------------------------------------------------------------------
	def initStatus(self):
		self.__status = TaskStatus.WAITING
		self.statusChanged.emit(self.__id)

	# -------------------------------------------------------------------------
	def updateStatus(self, status: TaskStatus):
		self.__status = status
		self.statusChanged.emit(self.__id)

	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
