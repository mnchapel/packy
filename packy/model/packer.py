"""
author: Marie-Neige Chapel
"""

# Python
from genericpath import isfile
import glob
import os
import shutil

# Python debug
import debugpy

# PyQt
from PyQt6.QtCore import Qt, QRunnable, QSettings

# PackY
from model.preferences import PreferencesGeneral, PreferencesKeys, PreferencesTask
from model.task import Task, TaskStatus
from model.packer_signals import PackerSignals

###############################################################################
class Packer(QRunnable):

    # -------------------------------------------------------------------------
	def __init__(self, task: Task):
		super(Packer, self).__init__()

		self.signals = PackerSignals()
		self.__task = task

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def run(self):
		try:
			debugpy.debug_this_thread()
			tmp_folder_path = self.tmpFolderPath()

			checked_items = self.__task.filesSelected().checks()
			items_to_pack = self.filterSelectedFiles(checked_items)
			self.signals.progress.emit(25)

			self.copyItemsToTmpFolder(items_to_pack, tmp_folder_path)
			self.signals.progress.emit(50)

			self.packTmpFolder(self.__task, tmp_folder_path)
			self.signals.progress.emit(75)

			self.__applySnapshotRetention()
			self.__task.updateStatus(TaskStatus.SUCCESS)
		except OSError as ex:
			self.__task.updateStatus(TaskStatus.ERROR)
			error_msg: str = type(ex).__name__ + ": " + str(ex)
			self.signals.error.emit(error_msg)
		finally:
			self.cleanTmpFolder(tmp_folder_path)
			self.signals.progress.emit(100)
			self.signals.finish.emit()

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
				if os.path.isfile(item):
					shutil.copy(item, tmp_folder_path)
				else:
					dir_basename = os.path.basename(os.path.normpath(item))
					tmp_sub_folder_path = os.path.join(tmp_folder_path, dir_basename)
					shutil.copytree(item, tmp_sub_folder_path)
				
				info_msg = f"Copy \"{item}\" to \"{tmp_folder_path}\""
				self.signals.info.emit(info_msg)
		
		except OSError as ex:
			raise ex
	
    # -------------------------------------------------------------------------
	def __applySnapshotRetention(self):
		settings: QSettings = QSettings()
		snapshot_retention = settings.value(PreferencesKeys.GENERAL_SR.value, type = int)

		if snapshot_retention == PreferencesGeneral.SR_NB_SNAPSHOT.value:
			nb_snapshot = settings.value(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, type = int)
			self.__findOldestSnapshot()
	
    # -------------------------------------------------------------------------
	def __findOldestSnapshot(self):
		raw_dest_file = self.__task.rawDestFile()
		suffix_pattern = self.__snapshotSuffixPattern()
		file_ext = self.__task.destExtension()

		file_pattern = raw_dest_file + suffix_pattern + "." + file_ext
		matches = glob.glob(file_pattern)
		matches = sorted(matches)

		print(f"matches = {matches}")

		# for match in matches:
			

    # -------------------------------------------------------------------------
	def __snapshotSuffixPattern(self) -> str:
		settings: QSettings = QSettings()
		task_suffix = settings.value(PreferencesKeys.TASK_SUFFIX.value, type = int)
		
		suffix_pattern = ""
		match task_suffix:
			case PreferencesTask.SUFFIX_CURR_DATE:
				suffix_pattern = "[0-9]{4}_[0-9]{2}_[0-9]{2}"
			case PreferencesTask.SUFFIX_VERSION_NUM:
				suffix_pattern = "[0-9]+"
		
		return suffix_pattern

    # -------------------------------------------------------------------------
	def cleanTmpFolder(self, tmp_folder_path: str):
		if os.path.exists(tmp_folder_path):
			shutil.rmtree(tmp_folder_path)
