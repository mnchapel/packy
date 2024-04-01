"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
import re
import shutil

# PyQt
from PyQt6.QtCore import Qt, QRunnable, QStandardPaths

# PackY
from model.preferences import PreferencesGeneral, PreferencesKeys, PreferencesTask
from model.task import Task, TaskStatus
from model.packer_signals import PackerSignals
from utils.settings_access import packySettings

# Python debug
# import debugpy

###############################################################################
class Packer(QRunnable):

	###########################################################################
	# PUBLIC MEMBER VARIABLES
	#
	# signals: 
	###########################################################################

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	#
	# __task: 
	###########################################################################

	###########################################################################
	# SIGNALS
	###########################################################################

    # -------------------------------------------------------------------------
	def __init__(self, task: Task):
		super(Packer, self).__init__()

		self.signals = PackerSignals()
		self.__task = task

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def run(self):
		try:
			# debugpy.debug_this_thread()
			self.__sendStartLog()
			tmp_folder_path = self.__tmpFolderPath()

			items_to_pack = self.__filterSelectedFiles()
			self.signals.progress.emit(25)

			self.__copyItemsToTmpFolder(items_to_pack, tmp_folder_path)
			self.signals.progress.emit(50)

			self.packTmpFolder(self.__task, tmp_folder_path)
			self.signals.progress.emit(75)

			self.__applySnapshotRetention()
			self.__task.updateStatus(TaskStatus.SUCCESS)
		except OSError as ex:
			self.__task.updateStatus(TaskStatus.ERROR)
			error_msg = type(ex).__name__ + ": " + str(ex)
			self.signals.error.emit(error_msg)
		finally:
			self.__cleanTmpFolder(tmp_folder_path)
			self.signals.progress.emit(100)
			self.signals.finish.emit()

	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################
			
    # -------------------------------------------------------------------------
	def __sendStartLog(self)->None:
		info_msg = f"<b>Run task {self.__task.rawDestFile()}</b>"
		self.signals.info.emit(info_msg)
	
    # -------------------------------------------------------------------------
	def __tmpFolderPath(self)->str:
		destination_file = self.__task.destFile()
		basename = os.path.basename(destination_file)
		basename_no_ext = os.path.splitext(basename)[0]
		
		tmp_location = QStandardPaths.StandardLocation.TempLocation
		tmp_path = QStandardPaths.writableLocation(tmp_location)
		packy_tmp_path = os.path.join(tmp_path, "packy_tmp")
		tmp_task_path = os.path.join(packy_tmp_path, basename_no_ext)

		return tmp_task_path

    # -------------------------------------------------------------------------
	def __filterSelectedFiles(self):
		checked_items = self.__task.filesSelected().checks()
		items_to_pack = [k for k, v in checked_items.items() if v == Qt.CheckState.Checked.value]

		return items_to_pack
	
    # -------------------------------------------------------------------------
	def __copyItemsToTmpFolder(self, items: set, tmp_folder_path: str):
		try:
			root_path = self.__task.filesSelected().rootPath()
			os.makedirs(tmp_folder_path)

			for item in items:
				tmp_item_path = item.replace(root_path, tmp_folder_path)

				if os.path.isfile(item):
					parent_folders = os.path.dirname(tmp_item_path)
					if not os.path.exists(parent_folders):
						os.makedirs(parent_folders)
					shutil.copy2(item, tmp_item_path)
				else:
					shutil.copytree(item, tmp_item_path, dirs_exist_ok=True)
				
				info_msg = f"Copy \"{item}\" to \"{tmp_folder_path}\""
				self.signals.info.emit(info_msg)
		
		except OSError as ex:
			raise ex
	
    # -------------------------------------------------------------------------
	def __applySnapshotRetention(self):
		settings = packySettings()
		snapshot_retention = settings.value(PreferencesKeys.GENERAL_SR.value, type = int)

		if snapshot_retention == PreferencesGeneral.SR_NB_SNAPSHOT.value:
			snapshots = self.__findSnapshots()
			self.__removeSnapshots(snapshots)
	
    # -------------------------------------------------------------------------
	def __findSnapshots(self):
		raw_dest_file = self.__task.rawDestFile()
		suffix_pattern = self.__snapshotSuffixPattern()
		file_ext = self.__task.destExtension()

		file_pattern = os.path.basename(raw_dest_file) + suffix_pattern + "." + file_ext
		dirname = os.path.dirname(raw_dest_file)

		snapshots = [f for f in filter(re.compile(file_pattern).match, os.listdir(dirname))]

		return snapshots
	
    # -------------------------------------------------------------------------
	def __removeSnapshots(self, snapshots):
		settings = packySettings()
		nb_snapshot = settings.value(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, type = int)
		
		raw_dest_file = self.__task.rawDestFile()
		dirname = os.path.dirname(raw_dest_file)

		if len(snapshots) > nb_snapshot:
			snapshots = sorted(snapshots, reverse=True)
			for snapshot_path in snapshots[nb_snapshot:]:
				os.remove(os.path.join(dirname, snapshot_path))

				info_msg = f"Remove {snapshot_path}"
				self.signals.info.emit(info_msg)

    # -------------------------------------------------------------------------
	def __snapshotSuffixPattern(self) -> str:
		settings = packySettings()
		task_suffix = settings.value(PreferencesKeys.TASK_SUFFIX.value, type = int)
		
		suffix_pattern = ""
		match task_suffix:
			case PreferencesTask.SUFFIX_CURR_DATE.value:
				suffix_pattern = "_[0-9]{4}_[0-9]{2}_[0-9]{2}"
			case PreferencesTask.SUFFIX_VERSION_NUM.value:
				suffix_pattern = "_[0-9]+"
		
		return suffix_pattern

    # -------------------------------------------------------------------------
	def __cleanTmpFolder(self, tmp_folder_path: str):
		if os.path.exists(tmp_folder_path):
			shutil.rmtree(tmp_folder_path)
