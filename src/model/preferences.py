"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum, auto
import os

# PyQt
from PyQt6.QtCore import QAbstractListModel, QSettings

###############################################################################
class PreferencesRows(Enum):
	# "General"
	SR_KEEP_ALL = 0			# "Snapshot retention": "Keep all snapshots"
	SR_NB_SNAPSHOT = auto()	# "Snapshot retention": "Number of latest snapshots to keep"
	SR_NB = auto()			# "Snapshot retention": spin_box_nb_snapshots
	# "Task"
	T_CURR_DATE = auto()	# "Output format": "Add the current date"
	T_VERSION_NUM = auto()	# "Output format": "Add version numbers"
	T_NOTHING = auto()		# "Output format": "Add nothing"


###############################################################################
class Preferences(QAbstractListModel):

	# -------------------------------------------------------------------------
	def __init__(self):
		super(Preferences, self).__init__()

		filename = "preferences.ini"
		format = QSettings.Format.IniFormat

		file_exists = os.path.exists(filename)

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__settings = QSettings(filename, format)

		if not file_exists:
			self.initSettings()

	# -------------------------------------------------------------------------
	def initSettings(self):
		self.__settings.beginGroup("general")
		self.__settings.setValue("snapshot_retention", 0)
		self.__settings.setValue("nb_snapshots", 1)
		self.__settings.endGroup()

		self.__settings.beginGroup("task")
		self.__settings.setValue("suffix", 0)
		self.__settings.endGroup()

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################
	
	# -------------------------------------------------------------------------
	# @override
	def rowCount(self, index=None):
		return 6
	
	# -------------------------------------------------------------------------
	# @override
	def data(self, index, role):
		if index.isValid():
			match index.row():
				case PreferencesRows.SR_KEEP_ALL.value:
					return self.__settings.value("general/snapshot_retention", type = int) == index.row()
				case PreferencesRows.SR_NB_SNAPSHOT.value:
					return self.__settings.value("general/snapshot_retention", type = int) == index.row()
				case PreferencesRows.SR_NB.value:
					return self.__settings.value("general/nb_snapshots", type = int)
				case PreferencesRows.T_CURR_DATE.value:
					return self.__settings.value("task/suffix", type = int) == index.row()
				case PreferencesRows.T_VERSION_NUM.value:
					return self.__settings.value("task/suffix", type = int) == index.row()
				case PreferencesRows.T_NOTHING.value:
					return self.__settings.value("task/suffix", type = int) == index.row()
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			match index.row():
				case PreferencesRows.SR_KEEP_ALL.value:
					self.__settings.setValue("general/snapshot_retention", index.row())
				case PreferencesRows.SR_NB_SNAPSHOT.value:
					self.__settings.setValue("general/snapshot_retention", index.row())
				case PreferencesRows.SR_NB.value:
					self.__settings.setValue("general/nb_snapshots", value)
				case PreferencesRows.T_CURR_DATE.value:
					self.__settings.setValue("task/suffix", index.row())
				case PreferencesRows.T_VERSION_NUM.value:
					self.__settings.setValue("task/suffix", index.row())
				case PreferencesRows.T_NOTHING.value:
					self.__settings.setValue("task/suffix", index.row())
		return False
