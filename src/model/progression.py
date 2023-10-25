"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QAbstractListModel

###############################################################################
class Progression(QAbstractListModel):

    # -------------------------------------------------------------------------
	def __init__(self):
		super(Progression, self).__init__()

		self.__nb_task = 0
		self.__nb_task_finished = 0
		self._global_progress = 0
		self._task_progress = 0

	###########################################################################
	# SETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def setNbTask(self, nb_task: int):
		self.__nb_task = nb_task

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 2

    # -------------------------------------------------------------------------
	def data(self, index, role):
		if index.isValid():
			if index.row() == 0:
				return self._global_progress
			elif index.row() == 1:
				return self._task_progress
	
	###########################################################################
	# SLOTS
	###########################################################################

    # -------------------------------------------------------------------------
	def updateTaskProgress(self, progress: int):
		self._task_progress = progress
		self.dataChanged.emit(self.index(1, 0), self.index(1, 0))
	
    # -------------------------------------------------------------------------
	def updateGlobalProgress(self):
		self.__nb_task_finished += 1
		self._global_progress = (self.__nb_task_finished / self.__nb_task) * 100
		self.dataChanged.emit(self.index(0, 0), self.index(0, 0))
