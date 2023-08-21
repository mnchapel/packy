"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog
from ui_main_window import Ui_MainWindow

# PackY
from about import About
from files_model import FilesModel
from task import Task
from packer_data import PackerData
from session import Session

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
	# -------------------------------------------------------------------------
	def __init__(self, *args, obj=None, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setupUi(self)

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._save_text = "Save"
		self._edit_text = "Edit"

		self.initConnects()
		self.initSessionView()
		self.initTaskView()
		self.initFilesView()

		self.show()

	# -------------------------------------------------------------------------
	def initConnects(self):
		self.connectFileMenuActions()
		self.connectHelpMenuActions()
		self.connectTaskManagement()
		self.connectTaskRunning()
		self.connectTaskProperties()

	# -------------------------------------------------------------------------
	def connectFileMenuActions(self):
		self.action_save.triggered.connect(self.onSave)
		self.action_options.triggered.connect(self.openOptions)
		self.action_exit.triggered.connect(self.close)

	# -------------------------------------------------------------------------
	def connectHelpMenuActions(self):
		self.action_documentation.triggered.connect(self.openDocumentation)
		self.action_about.triggered.connect(self.openAbout)
	
	# -------------------------------------------------------------------------
	def connectTaskManagement(self):
		self.push_button_create.clicked.connect(self.clickOnCreate)
		self.push_button_remove.clicked.connect(self.clickOnRemove)
		self.push_button_edit.clicked.connect(self.clickOnEdit)
	
	# -------------------------------------------------------------------------
	def connectTaskRunning(self):
		self.push_button_run_all.clicked.connect(self.clickOnRunAll)
		self.push_button_cancel.clicked.connect(self.clickOnCancel)

	# -------------------------------------------------------------------------
	def connectTaskProperties(self):
		self.connectFilesSelection()
		self.button_group_packer_type.buttonClicked.connect(self.updatePackerType)

	# -------------------------------------------------------------------------
	def updatePackerType(self, button: QtWidgets.QAbstractButton):
		self._packer_type_mapper.submit()
		
	# -------------------------------------------------------------------------
	def connectFilesSelection(self):
		self.push_button_source.clicked.connect(self.selectFolder)
	
	# -------------------------------------------------------------------------
	def initSessionView(self):
		self._session = Session()
		self.table_view_session.setModel(self._session)
		self.table_view_session.horizontalHeader().setVisible(True)
		self.table_view_session.selectionModel().selectionChanged.connect(self.mapViewWithTask)

	# -------------------------------------------------------------------------
	def initTaskView(self):
		self.createTaskMapper()
		self.createPackerMapper()
	
	# -------------------------------------------------------------------------
	def createTaskMapper(self):
		self._task_view_mapper = QtWidgets.QDataWidgetMapper(self)
		self._task_view_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def createPackerMapper(self):
		self._packer_mapper = QtWidgets.QDataWidgetMapper(self)
		self._packer_mapper.setOrientation(Qt.Orientation.Vertical)

		self.createPackerTypeMapper()

	# -------------------------------------------------------------------------
	def createPackerTypeMapper(self):
		self._packer_type_mapper = QtWidgets.QDataWidgetMapper(self)
		self._packer_type_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def initFilesView(self):
		self._files_model = FilesModel()
		self._files_model.setRootPath("")
	
	# -------------------------------------------------------------------------
	def selectFolder(self):
		QFileDialog.getExistingDirectory(self, "Select folder", self.line_edit_source.text(), QFileDialog.Option.ShowDirsOnly)
	
	# -------------------------------------------------------------------------
	def onSave(self, s):
		print("onSave (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def openOptions(self, s):
		print("openOptions (not implemented yet)")

	# -------------------------------------------------------------------------
	def openDocumentation(self, s):
		print("openDocumentation (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def openAbout(self, s):
		dlg = About(self)
		dlg.exec()
	
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
			if self.push_button_edit.text() == self._edit_text:
				self.enableTaskProperties()
			else:
				self.disableTaskProperties()
	
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

		self.updateTaskViewMapper(task)
		self.updatePackerViewMapper(task)
		self.updateFilesSelection()
	
	# -------------------------------------------------------------------------
	def updateTaskViewMapper(self, task):
		self._task_view_mapper.setModel(task)
		self._task_view_mapper.addMapping(self.line_edit_destination, task.properties.OUTPUT_NAME.value)
		self._task_view_mapper.addMapping(self.line_edit_source, task.properties.OUTPUT_FOLDER.value)
		self._task_view_mapper.toFirst()
	
	# -------------------------------------------------------------------------
	def updateFilesSelection(self):
		if self.tree_view_source.model() is None:
			self.tree_view_source.setModel(self._files_model)

		self.tree_view_source.setRootIndex(self._files_model.index(self.line_edit_source.text()))
		
		for col_index in range(1, self._files_model.columnCount()):
			self.tree_view_source.setColumnHidden(col_index, True)
	
	# -------------------------------------------------------------------------
	def updatePackerViewMapper(self, task: Task):
		packer_data = task.packerData()

		self._packer_mapper.setModel(packer_data)
		self._packer_mapper.addMapping(self.cbox_compression_level, 1, b"currentIndex")
		self._packer_mapper.addMapping(self.cbox_compression_method, 2, b"currentIndex")
		self._packer_mapper.toFirst()

		self.updatePackerTypeViewMapper(packer_data)
	
	# -------------------------------------------------------------------------
	def updatePackerTypeViewMapper(self, packer_data: PackerData):

		packer_type_data = packer_data.packerTypeData()

		self._packer_type_mapper.setModel(packer_type_data)
		self._packer_type_mapper.addMapping(self.rbutton_zip, 0)
		self._packer_type_mapper.addMapping(self.rbutton_tar, 1)
		self._packer_type_mapper.addMapping(self.rbutton_bz2, 2)
		self._packer_type_mapper.addMapping(self.rbutton_tbz, 3)
		self._packer_type_mapper.addMapping(self.rbutton_gz, 4)
		self._packer_type_mapper.addMapping(self.rbutton_tgz, 5)
		self._packer_type_mapper.addMapping(self.rbutton_lzma, 6)
		self._packer_type_mapper.addMapping(self.rbutton_tlz, 7)
		self._packer_type_mapper.addMapping(self.rbutton_xz, 8)
		self._packer_type_mapper.toFirst()

	# -------------------------------------------------------------------------
	def enableTaskProperties(self):
		self.group_box_file_selection.setEnabled(True)
		self.group_box_output_properties.setEnabled(True)
		self.group_box_statistics.setEnabled(False)

		self.push_button_create.setEnabled(False)
		self.push_button_remove.setEnabled(False)
		self.push_button_edit.setEnabled(True)
		self.push_button_edit.setText(self._save_text)
		self.push_button_run_all.setEnabled(False)
		self.push_button_cancel.setEnabled(False)

		self.table_view_session.setEnabled(False)

	# -------------------------------------------------------------------------
	def disableTaskProperties(self):
		self.group_box_file_selection.setEnabled(False)
		self.group_box_output_properties.setEnabled(False)
		self.group_box_statistics.setEnabled(True)

		self.push_button_create.setEnabled(True)
		self.push_button_remove.setEnabled(True)
		self.push_button_edit.setText(self._edit_text)
		self.push_button_run_all.setEnabled(True)
		self.push_button_cancel.setEnabled(True)

		self.table_view_session.setEnabled(True)
