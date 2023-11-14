"""
author: Marie-Neige Chapel
"""

# Python
from enum import Enum, auto

###############################################################################
class PreferencesGeneral(Enum):
	SR_KEEP_ALL = 0			# "Snapshot retention": "Keep all snapshots"
	SR_NB_SNAPSHOT = auto()	# "Snapshot retention": "Number of latest snapshots to keep"
	SR_NB = auto()			# "Snapshot retention": spin_box_nb_snapshots

###############################################################################
class PreferencesTask(Enum):
	SUFFIX_CURR_DATE = 0	# "Output format": "Add the current date"
	SUFFIX_VERSION_NUM = auto()	# "Output format": "Add version numbers"
	SUFFIX_NOTHING = auto()		# "Output format": "Add nothing"

###############################################################################
class PreferencesKeys(Enum):
	GENERAL_SR = "general/snapshot_retention"
	GENERAL_NB_SNAPSHOT = "general/nb_snapshots"
	TASK_SUFFIX = "task/suffix"
