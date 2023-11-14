"""
author: Marie-Neige Chapel
"""

# PyQt
from asyncio import Task
from PyQt6.QtCore import QSettings, pyqtSignal
from PyQt6.QtWidgets import QDialog, QAbstractButton
from PyQt6.uic import loadUi

# PackY
from model.preferences import PreferencesKeys, PreferencesTask
from model.task import Task

###############################################################################
class Options(QDialog):

	taskSuffixChanged = pyqtSignal()

	# -------------------------------------------------------------------------
	def __init__(self, parent=None):
		super(Options, self).__init__()

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__ui = loadUi("../resources/options.ui", self)
		self.__settings = QSettings()

		self.initGeneralSection()
		self.initTaskSection()
		self.initConnect()

		if self.__ui.r_button_nb_snapshots.isChecked():
			self.__ui.spin_box_nb_snapshots.setEnabled(True)
	
	# -------------------------------------------------------------------------
	def initGeneralSection(self):
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
	def initTaskSection(self):
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
	def initConnect(self):
		self.__ui.b_group_snapshot_retention.buttonClicked.connect(self.updateGui)

	# -------------------------------------------------------------------------
	def updateGui(self, button: QAbstractButton):
		if button.objectName() == "r_button_nb_snapshots":
			self.__ui.spin_box_nb_snapshots.setEnabled(True)
		else:
			self.__ui.spin_box_nb_snapshots.setEnabled(False)

	# -------------------------------------------------------------------------
	def accept(self):
		print("[Options][accept]")

		self.updateGeneralSettings()
		self.updateTaskSettings()
		
		super().accept()

	# -------------------------------------------------------------------------
	def updateGeneralSettings(self):
		general_sr = 0
		if self.__ui.r_button_nb_snapshots.isChecked() :
			general_sr = 1

		self.__settings.setValue(PreferencesKeys.GENERAL_SR.value, general_sr)

		nb_snapshots = self.__ui.spin_box_nb_snapshots.value()
		self.__settings.setValue(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, nb_snapshots)

	# -------------------------------------------------------------------------
	def updateTaskSettings(self):
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
