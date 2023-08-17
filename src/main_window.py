"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from ui_main_window import Ui_MainWindow

# PackY
from about import About
from task import Task
from session import Session

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
	# -------------------------------------------------------------------------
	def __init__(self, *args, obj=None, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setupUi(self)

		self.connectFileMenuActions()
		self.connectHelpMenuActions()
		self.connectTaskManagement()
		self.connectTaskRunning()

		self.initTaskView()

		self.save_text = "Save"
		self.edit_text = "Edit"

		self._session = Session()
		self.table_view_session.setModel(self._session)

		self.table_view_session.horizontalHeader().setVisible(True)
		self.table_view_session.selectionModel().selectionChanged.connect(self.mapViewWithTask)

		self.show()
	
	# -------------------------------------------------------------------------
	def initTaskView(self):
		self._task_view_mapper = QtWidgets.QDataWidgetMapper(self)
		self._task_view_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def connectFileMenuActions(self):
		self.action_save.triggered.connect(self.save)
		self.action_options.triggered.connect(self.openOptions)
		self.action_exit.triggered.connect(self.close)
	
	# -------------------------------------------------------------------------
	def save(self, s):
		print("save (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def openOptions(self, s):
		print("openOptions (not implemented yet)")

	# -------------------------------------------------------------------------
	def connectHelpMenuActions(self):
		self.action_documentation.triggered.connect(self.openDocumentation)
		self.action_about.triggered.connect(self.openAbout)

	# -------------------------------------------------------------------------
	def openDocumentation(self, s):
		print("openDocumentation (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def openAbout(self, s):
		dlg = About(self)
		dlg.exec()
	
	# -------------------------------------------------------------------------
	def connectTaskManagement(self):
		self.push_button_create.clicked.connect(self.clickOnCreate)
		self.push_button_remove.clicked.connect(self.clickOnRemove)
		self.push_button_edit.clicked.connect(self.clickOnEdit)
	
	# -------------------------------------------------------------------------
	def clickOnCreate(self):
		model = self.table_view_session.model()
		row_inserted = model.insertRow(["Editing...", "output.zip", "0%"])
		self.table_view_session.selectRow(row_inserted)
		self.enableTaskProperties()
	
	# -------------------------------------------------------------------------
	def clickOnRemove(self):
		model = self.table_view_session.model()
		current_row = self.table_view_session.currentIndex().row()
		model.removeRow(current_row)
	
	# -------------------------------------------------------------------------
	def clickOnEdit(self):
		current_row = self.table_view_session.currentIndex().row()
		
		if current_row >= 0:
			if self.push_button_edit.text() == self.edit_text:
				self.enableTaskProperties()
			else:
				self.disableTaskProperties()
	
	# -------------------------------------------------------------------------
	def connectTaskRunning(self):
		self.push_button_run_all.clicked.connect(self.clickOnRunAll)
		self.push_button_cancel.clicked.connect(self.clickOnCancel)
	
	# -------------------------------------------------------------------------
	def clickOnRunAll(self):
		print("clickOnRunAll (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def clickOnCancel(self):
		print("clickOnCancel (not implemented yet)")

	# -------------------------------------------------------------------------
	def mapViewWithTask(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection):
		selected_row = self.table_view_session.currentIndex().row()
		task = self._session.taskAt(selected_row)
		self._task_view_mapper.setModel(task)
		self._task_view_mapper.addMapping(self.line_edit_destination, 1)
		self._task_view_mapper.toFirst()

	# -------------------------------------------------------------------------
	def enableTaskProperties(self):
		self.group_box_file_selection.setEnabled(True)
		self.group_box_output_properties.setEnabled(True)
		self.group_box_statistics.setEnabled(False)

		self.push_button_create.setEnabled(False)
		self.push_button_remove.setEnabled(False)
		self.push_button_edit.setText(self.save_text)
		self.push_button_run_all.setEnabled(False)
		self.push_button_cancel.setEnabled(False)

	# -------------------------------------------------------------------------
	def disableTaskProperties(self):
		self.group_box_file_selection.setEnabled(False)
		self.group_box_output_properties.setEnabled(False)
		self.group_box_statistics.setEnabled(True)

		self.push_button_create.setEnabled(True)
		self.push_button_remove.setEnabled(True)
		self.push_button_edit.setText(self.edit_text)
		self.push_button_run_all.setEnabled(True)
		self.push_button_cancel.setEnabled(True)

