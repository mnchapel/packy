"""
author: Marie-Neige Chapel
"""

# Python
import os

# PyQt
from PyQt6.QtCore import QObject, pyqtSignal

# PackY
from model.task import Task

###############################################################################
class Packer(QObject):

	error = pyqtSignal(tuple)
	progress = pyqtSignal(int)
	finish = pyqtSignal()

    # -------------------------------------------------------------------------
	def __init__(self, task: Task, index: int):
		super(Packer, self).__init__()

		self._task = task
		self._index = index

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def run(self):
		checked_items = self._task.filesSelected().checks()
		items_to_pack = self.filterSelectedFiles(checked_items)

		self.progress.emit(50)

		self.packItems(self._task, items_to_pack)
			
		self._task.updateStatus(True)
		self.progress.emit(100)
		self.finish.emit()

    # -------------------------------------------------------------------------
	def filterSelectedFiles(self, checked_items: dict):
		items_to_pack = []
		
		items_to_pack = {k: v for k, v in checked_items.items() if v == 2}
		dir_items = {item for item in items_to_pack if os.path.isdir(item)}
		files_items = {item for item in items_to_pack if os.path.isfile(item)}
		files_to_pack = {item for item in items_to_pack if os.path.isfile(item)}
		
		items_to_pack.clear()
		items_to_pack = dir_items

		for dir in dir_items:
			for file in files_items:
				if dir in file:
					files_to_pack.remove(file)
		
		items_to_pack = dir_items | files_to_pack

		return items_to_pack
