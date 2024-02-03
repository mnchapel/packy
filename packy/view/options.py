"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# PyQt
import os
from asyncio import Task
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QAbstractButton
from PyQt6.uic import loadUi

# PackY
from model.preferences import PreferencesKeys, PreferencesTask
from model.task import Task
from utils.resources_access import resources_path
from utils.settings_access import packySettings

###############################################################################
class Options(QDialog):

	###########################################################################
	# SIGNALS
	###########################################################################

	taskSuffixChanged = pyqtSignal()

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, parent=None) -> None:
		super(Options, self).__init__()

		ui_path = os.path.join(resources_path(), "ui/options.ui")
		self.__ui = loadUi(ui_path, self)
		self.__settings = packySettings()

		self.__initGeneralSection()
		self.__initTaskSection()
		self.__initConnect()

		if self.__ui.r_button_nb_snapshots.isChecked():
			self.__ui.spin_box_nb_snapshots.setEnabled(True)
	
	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def accept(self) -> None:
		self.__updateGeneralSettings()
		self.__updateTaskSettings()
		
		super().accept()
	
	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def __initGeneralSection(self) -> None:
		general_sr = self.__settings.value(PreferencesKeys.GENERAL_SR.value, type=int)

		match general_sr:
			case 0:
				self.__ui.r_button_keep_all.setChecked(True)
			case 1:
				self.__ui.r_button_nb_snapshots.setChecked(True)
			case _:
				raise Exception("[initGeneralSection] The preference GENERAL_SR unknown.")
		
		nb_snapshots = self.__settings.value(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, type = int)
		self.__ui.spin_box_nb_snapshots.setValue(nb_snapshots)

	# -------------------------------------------------------------------------
	def __initTaskSection(self) -> None:
		task_suffix = self.__settings.value(PreferencesKeys.TASK_SUFFIX.value, type = int)

		match task_suffix:
			case 0:
				self.__ui.r_button_current_date.setChecked(True)
			case 1:
				self.__ui.r_button_version_num.setChecked(True)
			case 2:
				self.__ui.r_button_nothing.setChecked(True)
			case _:
				raise Exception("[initTaskSection] The preference TASK_SUFFIX unknown.")
	
	# -------------------------------------------------------------------------
	def __initConnect(self) -> None:
		self.__ui.b_group_snapshot_retention.buttonClicked.connect(self.__updateGui)

	# -------------------------------------------------------------------------
	def __updateGeneralSettings(self) -> None:
		general_sr = 0
		if self.__ui.r_button_nb_snapshots.isChecked() :
			general_sr = 1

		self.__settings.setValue(PreferencesKeys.GENERAL_SR.value, general_sr)

		nb_snapshots = self.__ui.spin_box_nb_snapshots.value()
		self.__settings.setValue(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, nb_snapshots)

	# -------------------------------------------------------------------------
	def __updateTaskSettings(self) -> None:
		old_task_suffix = self.__settings.value(PreferencesKeys.TASK_SUFFIX.value)

		task_suffix = 0

		if self.__ui.r_button_version_num.isChecked():
			task_suffix = 1
		elif self.__ui.r_button_nothing.isChecked():
			task_suffix = 2

		if old_task_suffix != task_suffix:
			self.__settings.setValue(PreferencesKeys.TASK_SUFFIX.value, task_suffix)
			Task.updateDestSuffix(PreferencesTask(task_suffix))
			self.taskSuffixChanged.emit()

	###########################################################################
	# PRIVATE SLOTS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def __updateGui(self, button: QAbstractButton) -> None:
		if button.objectName() == "r_button_nb_snapshots":
			self.__ui.spin_box_nb_snapshots.setEnabled(True)
		else:
			self.__ui.spin_box_nb_snapshots.setEnabled(False)
