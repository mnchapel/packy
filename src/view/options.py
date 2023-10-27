"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QDataWidgetMapper, QAbstractButton
from PyQt6.uic import loadUi

# PackY
from model.preferences import Preferences, PreferencesRows

###############################################################################
class Options(QDialog):

	# -------------------------------------------------------------------------
	def __init__(self, preferences: Preferences, parent=None):
		super(Options, self).__init__()

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__ui = loadUi("../resources/options.ui", self)

		self.__general_mapper = QDataWidgetMapper(self)
		self.__general_mapper.setOrientation(Qt.Orientation.Vertical)

		self.__task_mapper = QDataWidgetMapper(self)
		self.__task_mapper.setOrientation(Qt.Orientation.Vertical)
		self.__preferences = preferences

		self.initGeneralMapper()
		self.initTaskMapper()
		self.initConnect()

		if self.__ui.r_button_nb_snapshots.isChecked():
			self.__ui.spin_box_nb_snapshots.setEnabled(True)
	
	# -------------------------------------------------------------------------
	def initGeneralMapper(self):
		self.__general_mapper.setModel(self.__preferences)
		self.__general_mapper.addMapping(self.__ui.r_button_keep_all, PreferencesRows.SR_KEEP_ALL.value)
		self.__general_mapper.addMapping(self.__ui.r_button_nb_snapshots, PreferencesRows.SR_NB_SNAPSHOT.value)
		self.__general_mapper.addMapping(self.__ui.spin_box_nb_snapshots, PreferencesRows.SR_NB.value)
		self.__general_mapper.toFirst()

	# -------------------------------------------------------------------------
	def initTaskMapper(self):
		self.__task_mapper.setModel(self.__preferences)
		self.__task_mapper.addMapping(self.__ui.r_button_current_date, PreferencesRows.T_CURR_DATE.value)
		self.__task_mapper.addMapping(self.__ui.r_button_version_num, PreferencesRows.T_VERSION_NUM.value)
		self.__task_mapper.addMapping(self.__ui.r_button_nothing, PreferencesRows.T_NOTHING.value)
		self.__task_mapper.toFirst()
	
	# -------------------------------------------------------------------------
	def initConnect(self):
		self.__ui.b_group_snapshot_retention.buttonClicked.connect(self.updateGui)

	# -------------------------------------------------------------------------
	def updateGui(self, button: QAbstractButton):
		if button.objectName() == "r_button_nb_snapshots":
			self.__ui.spin_box_nb_snapshots.setEnabled(True)
		else:
			self.__ui.spin_box_nb_snapshots.setEnabled(False)
