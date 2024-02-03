"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import QAbstractListModel

###############################################################################
class Progression(QAbstractListModel):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __nb_task: 
	# __nb_error: 
	# __nb_task_finished: 
	# __global_progress: 
	# __task_progress: 
	###########################################################################

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

    # -------------------------------------------------------------------------
	def __init__(self):
		super(Progression, self).__init__()

		self.__init()

	###########################################################################
	# SETTERS
	###########################################################################

    # -------------------------------------------------------------------------
	def setNbTask(self, nb_task: int):
		self.__nb_task = nb_task

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return 2

    # -------------------------------------------------------------------------
	def data(self, index, role):
		if index.isValid():
			if index.row() == 0:
				return self.__global_progress
			elif index.row() == 1:
				return self.__task_progress
			
    # -------------------------------------------------------------------------
	def report(self) -> str:
		report: str = str(self.__nb_task_finished) + " task(s) processed / " + str(self.__nb_error) + " errors."

		if self.__nb_error > 0:
			report += "\n See the log file for more information."

		return report
	
	###########################################################################
	# PUBLIC SLOTS
	###########################################################################

    # -------------------------------------------------------------------------
	def errorReported(self, msg: str):
		self.__nb_error += 1
		QtCore.qCritical(msg)

    # -------------------------------------------------------------------------
	def updateTaskProgress(self, progress: int):
		self.__task_progress = progress
		self.dataChanged.emit(self.index(1, 0), self.index(1, 0))
	
    # -------------------------------------------------------------------------
	def updateGlobalProgress(self):
		self.__nb_task_finished += 1
		self.__global_progress = (self.__nb_task_finished / self.__nb_task) * 100
		self.dataChanged.emit(self.index(0, 0), self.index(0, 0))

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def __init(self):
		self.__nb_task = 0
		self.__nb_error = 0
		self.__nb_task_finished = 0
		self.__global_progress = 0
		self.__task_progress = 0
