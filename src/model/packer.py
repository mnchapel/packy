"""
author: Marie-Neige Chapel
"""

# Python
import os
import shutil

# PyQt
from PyQt6.QtCore import Qt, QObject, pyqtSignal

# PackY
from model.task import Task, TaskStatus

###############################################################################
class Packer(QObject):

	error = pyqtSignal(tuple)
	progress = pyqtSignal(int)
	finish = pyqtSignal()

    # -------------------------------------------------------------------------
	def __init__(self, task: Task):
		super(Packer, self).__init__()

		self.__task = task

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def run(self):
		try:
			tmp_folder_path = self.tmpFolderPath()

			checked_items = self.__task.filesSelected().checks()
			items_to_pack = self.filterSelectedFiles(checked_items)

			self.progress.emit(33)

			self.copyItemsToTmpFolder(items_to_pack, tmp_folder_path)

			self.progress.emit(66)

			self.packTmpFolder(self.__task, tmp_folder_path)

			self.__task.updateStatus(TaskStatus.SUCCESS)
		except OSError as ex:
			self.__task.updateStatus(TaskStatus.ERROR)
			print(type(ex), ": ", ex)
		finally:
			self.cleanTmpFolder(tmp_folder_path)
			self.progress.emit(100)
			self.finish.emit()

    # -------------------------------------------------------------------------
	def filterSelectedFiles(self, checked_items: dict):
		items_to_pack = []
		
		items_to_pack = {k: v for k, v in checked_items.items() if v == Qt.CheckState.Checked.value}

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
	
    # -------------------------------------------------------------------------
	def tmpFolderPath(self)->str:
		destination_file = self.__task.destFile()
		basename = os.path.basename(destination_file)
		basename_no_ext = os.path.splitext(basename)[0]
		tmp_folder_path = os.path.join("../tmp/", basename_no_ext)

		return tmp_folder_path
	
    # -------------------------------------------------------------------------
	def copyItemsToTmpFolder(self, items: set, tmp_folder_path: str):
		try:
			os.mkdir(tmp_folder_path)

			for item in items:
				shutil.copy(item, tmp_folder_path)
		
		except OSError as ex:
			raise ex
		

    # -------------------------------------------------------------------------
	def cleanTmpFolder(self, tmp_folder_path: str):
		if os.path.exists(tmp_folder_path):
			shutil.rmtree(tmp_folder_path)
