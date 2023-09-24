"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum, auto
import os

# PyQt
from PyQt6.QtCore import QAbstractListModel, QSettings, QModelIndex

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
		self._settings = QSettings(filename, format)

		if not file_exists:
			self.initSettings()

	# -------------------------------------------------------------------------
	def initSettings(self):
		self._settings.beginGroup("general")
		self._settings.setValue("snapshot_retention", 0)
		self._settings.setValue("nb_snapshots", 1)
		self._settings.endGroup()

		self._settings.beginGroup("task")
		self._settings.setValue("suffix", 0)
		self._settings.endGroup()

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
					return self._settings.value("general/snapshot_retention", type = int) == index.row()
				case PreferencesRows.SR_NB_SNAPSHOT.value:
					return self._settings.value("general/snapshot_retention", type = int) == index.row()
				case PreferencesRows.SR_NB.value:
					return self._settings.value("general/nb_snapshots", type = int)
				case PreferencesRows.T_CURR_DATE.value:
					return self._settings.value("task/suffix", type = int) == index.row()
				case PreferencesRows.T_VERSION_NUM.value:
					return self._settings.value("task/suffix", type = int) == index.row()
				case PreferencesRows.T_NOTHING.value:
					return self._settings.value("task/suffix", type = int) == index.row()
		return None
	
	# -------------------------------------------------------------------------
	# @override
	def setData(self, index, value, role):
		if index.isValid():
			match index.row():
				case PreferencesRows.SR_KEEP_ALL.value:
					self._settings.setValue("general/snapshot_retention", index.row())
				case PreferencesRows.SR_NB_SNAPSHOT.value:
					self._settings.setValue("general/snapshot_retention", index.row())
				case PreferencesRows.SR_NB.value:
					self._settings.setValue("general/nb_snapshots", value)
				case PreferencesRows.T_CURR_DATE.value:
					self._settings.setValue("task/suffix", index.row())
				case PreferencesRows.T_VERSION_NUM.value:
					self._settings.setValue("task/suffix", index.row())
				case PreferencesRows.T_NOTHING.value:
					self._settings.setValue("task/suffix", index.row())
		return False
