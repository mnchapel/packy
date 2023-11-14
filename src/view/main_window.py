"""
author: Marie-Neige Chapel
"""

#Python
import json
import os

# PyQt
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QCoreApplication, QItemSelection, QThreadPool
from PyQt6.QtWidgets import QFileDialog

# PackY
from model.packer_data import DataName, PackerData
from model.packer_worker import PackerWorker
from model.progression import Progression
from model.task import Task
from model.task import TaskProperties
from model.session import Session
from model.session_encoder import SessionEncoder
from model.session_decoder import SessionDecoder
from view.about import About
from view.options import Options
from view.ui_main_window import Ui_MainWindow

###############################################################################
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
	# -------------------------------------------------------------------------
	def __init__(self, *args, obj=None, **kwargs) -> None:
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setupUi(self)

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self.__thread_pool = QThreadPool()

		self.initApplication()
		self.initConnects()
		self.initSessionView()
		self.initTaskView()
		self.initProgressionView()
		self.initTitle()

		self.show()

	# -------------------------------------------------------------------------
	def initApplication(self) -> None:
		QCoreApplication.setOrganizationName("PackYCorp")
		QCoreApplication.setOrganizationDomain("packy.com")
		QCoreApplication.setApplicationName("PackY")

	# -------------------------------------------------------------------------
	def initConnects(self) -> None:
		self.connectFileMenuActions()
		self.connectHelpMenuActions()
		self.connectTaskManagement()
		self.connectTaskRunning()
		self.connectTaskProperties()
	
	# -------------------------------------------------------------------------
	def initSessionView(self) -> None:
		self.__session = Session()
		self.table_view_session.horizontalHeader().setVisible(True)
		self.updateSessionViewModel()

	# -------------------------------------------------------------------------
	def updateSessionViewModel(self) -> None:
		self.table_view_session.setModel(self.__session)
		self.table_view_session.selectionModel().selectionChanged.connect(self.mapViewWithTask)

	# -------------------------------------------------------------------------
	def initTaskView(self) -> None:
		self.createTaskMapper()
		self.createPackerMapper()
	
	# -------------------------------------------------------------------------
	def initProgressionView(self) -> None:
		self.__progression = Progression()
		
		self.__progression_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__progression_mapper.setOrientation(Qt.Orientation.Vertical)
		self.__progression_mapper.setModel(self.__progression)
		self.__progression_mapper.addMapping(self.pbar_global_progress, 0, b"value")
		self.__progression_mapper.addMapping(self.pbar_task_progress, 1, b"value")
		self.__progression_mapper.toFirst()
	
	# -------------------------------------------------------------------------
	def createTaskMapper(self) -> None:
		self.__task_view_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__task_view_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def createPackerMapper(self) -> None:
		self.__packer_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__packer_mapper.setOrientation(Qt.Orientation.Vertical)

		self.createPackerTypeMapper()

	# -------------------------------------------------------------------------
	def createPackerTypeMapper(self) -> None:
		self.__packer_type_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__packer_type_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def initTitle(self) -> None:
		self.setWindowTitle("PackY - Untitled session")
	
	# -------------------------------------------------------------------------
	def onNewSession(self) -> None:
		self.__session = Session()

	# -------------------------------------------------------------------------
	def onSave(self, s) -> None:
		if not self.__session.name():
			self.onSaveAs(s)
		else:
			dst_file_path = self.__session.outputFile()
			with open(dst_file_path, "w") as output_file:
				json.dump(self.__session, output_file, cls=SessionEncoder, indent=4)

	# -------------------------------------------------------------------------
	def onSaveAs(self, s) -> None:
		[filename, _] = QFileDialog.getSaveFileName(self, "Save As", "")
		if filename:
			self.__session.setName(filename)
			dst_file_path = self.__session.outputFile()
			with open(dst_file_path, "w") as output_file:
				json.dump(self.__session, output_file, cls=SessionEncoder, indent=4)
	
	# -------------------------------------------------------------------------
	def onOpen(self, s) -> None:
		[filename, _] = QFileDialog.getOpenFileName(self, "Open session", "")
		if filename:
			with open(filename, "r") as file:
				self.__session = json.load(file, cls=SessionDecoder)
				self.updateSessionViewModel()
				if self.__session.nbTasks() > 0:
					self.__selected_task = self.__session.taskAt(0)
					self.table_view_session.selectRow(0)
					self.disableTaskProperties()

	# -------------------------------------------------------------------------
	def openDocumentation(self, s) -> None:
		print("openDocumentation (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def clickOnCreate(self) -> None:
		row_inserted = self.__session.insertRow()

		self.__selected_task = self.__session.taskAt(row_inserted)
		self.table_view_session.selectRow(row_inserted)

		self.enableTaskProperties()
		self.updateCompressionMethod()
		self.updateCompressionLevel()
	
	# -------------------------------------------------------------------------
	def clickOnRemove(self) -> None:
		model = self.table_view_session.model()
		current_row = self.table_view_session.currentIndex().row()
		model.removeRow(current_row)
		
		if self.__session.nbTasks() == 0:
			self.push_button_remove.setEnabled(False)
			self.push_button_edit.setEnabled(False)
			self.push_button_run_all.setEnabled(False)
			self.clearTaskProperties()
			return
		elif current_row > self.__session.nbTasks():
			current_row -= 1
		
		self.table_view_session.selectRow(current_row)
	
	# -------------------------------------------------------------------------
	def clickOnEdit(self) -> None:
		current_row = self.table_view_session.currentIndex().row()
		
		if current_row >= 0:
			if self.push_button_edit.text() == "Edit":
				self.enableTaskProperties()
			else:
				self.disableTaskProperties()
	
	# -------------------------------------------------------------------------
	def clickOnRunAll(self) -> None:
		self.initTasksStatus()

		self.__progression.init()
		self.__progression.setNbTask(self.__session.nbCheckedTasks())

		packer_worker = PackerWorker(self.__session, self.__progression)
		packer_worker.signals.runTaskId.connect(self.selectTask)
		self.__thread_pool.start(packer_worker)

	# -------------------------------------------------------------------------
	def initTasksStatus(self) -> None:
		tasks = self.__session.tasks()
		for task in tasks:
			task.initStatus()
	
	# -------------------------------------------------------------------------
	def clickOnCancel(self) -> None:
		print("clickOnCancel (not implemented yet)")

	# -------------------------------------------------------------------------
	def mapViewWithTask(self, selected: QItemSelection, deselected: QItemSelection) -> None:
		selected_row = self.table_view_session.currentIndex().row()
		self.__selected_task = self.__session.taskAt(selected_row)

		self.updateTaskViewMapper()
		self.updatePackerViewMapper()
		self.updateFilesSelection()
	
	# -------------------------------------------------------------------------
	def updateTaskViewMapper(self) -> None:
		task: Task = self.__selected_task
		self.__task_view_mapper.setModel(task)
		self.__task_view_mapper.addMapping(self.line_edit_source, TaskProperties.SRC_FOLDER.value, b"text")
		self.__task_view_mapper.addMapping(self.line_edit_destination, TaskProperties.DST_FILE.value, b"text")
		self.__task_view_mapper.toFirst()
	
	# -------------------------------------------------------------------------
	def updateFilesSelection(self) -> None:
		files_model = self.__selected_task.filesSelected()

		self.tree_view_source.setModel(files_model)
		self.tree_view_source.setRootIndex(files_model.index(files_model.rootPath()))
		
		for col_index in range(1, files_model.columnCount()):
			self.tree_view_source.setColumnHidden(col_index, True)

		files_model.directoryLoaded.connect(self.updateTreeChildren)
	
	# -------------------------------------------------------------------------
	def updateTreeChildren(self, path: str) -> None:
		files_model = self.__selected_task.filesSelected()
		index = files_model.index(path)

		if files_model.filePath(index) != self.line_edit_source.text():
			parent_check_state = files_model.data(index, Qt.ItemDataRole.CheckStateRole)
			files_model.setData(index, parent_check_state, Qt.ItemDataRole.CheckStateRole)
	
	# -------------------------------------------------------------------------
	def updatePackerViewMapper(self) -> None:
		packer_data = self.__selected_task.packerData()

		self.updateCompressionMethod()
		
		self.__packer_mapper.setModel(packer_data)
		self.__packer_mapper.addMapping(self.cbox_compression_method, DataName.COMPRESSION_METHOD.value, b"currentIndex")
		self.__packer_mapper.toFirst()

		self.updateCompressionLevel()
		
		self.__packer_mapper.addMapping(self.cbox_compression_level, DataName.COMPRESSION_LEVEL.value, b"currentIndex")
		self.__packer_mapper.toFirst()

		self.updatePackerTypeViewMapper(packer_data)
	
	# -------------------------------------------------------------------------
	def updatePackerTypeViewMapper(self, packer_data: PackerData) -> None:

		packer_type_data = packer_data.packerTypeData()

		self.__packer_type_mapper.setModel(packer_type_data)
		self.__packer_type_mapper.addMapping(self.rbutton_zip, 0)
		self.__packer_type_mapper.addMapping(self.rbutton_tar, 1)
		self.__packer_type_mapper.addMapping(self.rbutton_bz2, 2)
		self.__packer_type_mapper.addMapping(self.rbutton_tbz, 3)
		self.__packer_type_mapper.addMapping(self.rbutton_gz, 4)
		self.__packer_type_mapper.addMapping(self.rbutton_tgz, 5)
		self.__packer_type_mapper.addMapping(self.rbutton_lzma, 6)
		self.__packer_type_mapper.addMapping(self.rbutton_tlz, 7)
		self.__packer_type_mapper.addMapping(self.rbutton_xz, 8)
		self.__packer_type_mapper.toFirst()

	# -------------------------------------------------------------------------
	def enableTaskProperties(self) -> None:
		self.group_box_file_selection.setEnabled(True)
		self.group_box_output_properties.setEnabled(True)
		self.group_box_statistics.setEnabled(False)
		self.disableUnavailablePackerType()

		self.push_button_create.setEnabled(False)
		self.push_button_remove.setEnabled(False)
		self.push_button_edit.setEnabled(True)
		self.push_button_edit.setText("Save")
		self.push_button_run_all.setEnabled(False)

		self.table_view_session.setEnabled(False)
	
	# -------------------------------------------------------------------------
	def disableUnavailablePackerType(self) -> None:
		self.rbutton_tar.setEnabled(False)
		self.rbutton_bz2.setEnabled(False)
		self.rbutton_tbz.setEnabled(False)
		self.rbutton_gz.setEnabled(False)
		self.rbutton_tgz.setEnabled(False)
		self.rbutton_tlz.setEnabled(False)
		self.rbutton_xz.setEnabled(False)

	# -------------------------------------------------------------------------
	def disableTaskProperties(self) -> None:
		self.group_box_file_selection.setEnabled(False)
		self.group_box_output_properties.setEnabled(False)
		self.group_box_statistics.setEnabled(True)

		self.push_button_create.setEnabled(True)
		self.push_button_remove.setEnabled(True)
		self.push_button_edit.setEnabled(True)
		self.push_button_edit.setText("Edit")
		self.push_button_run_all.setEnabled(True)

		self.table_view_session.setEnabled(True)

	# -------------------------------------------------------------------------
	def clearTaskProperties(self) -> None:
		self.line_edit_source.setText("")
		self.line_edit_destination.setText("")
		self.cbox_compression_method.clear()
		self.cbox_compression_level.clear()
		self.tree_view_source.setModel(None)

		checked_button = self.button_group_packer_type.checkedButton()
		self.button_group_packer_type.setExclusive(False)
		checked_button.setChecked(False)
		self.button_group_packer_type.setExclusive(True)

		
	###########################################################################
	# CONNECT SLOTS TO SIGNALS
	###########################################################################

	# -------------------------------------------------------------------------
	def connectFileMenuActions(self) -> None:
		self.action_new_session.triggered.connect(self.onNewSession)
		self.action_save.triggered.connect(self.onSave)
		self.action_save_as.triggered.connect(self.onSaveAs)
		self.action_open.triggered.connect(self.onOpen)
		self.action_options.triggered.connect(self.openOptions)
		self.action_exit.triggered.connect(self.close)

	# -------------------------------------------------------------------------
	def connectHelpMenuActions(self) -> None:
		self.action_documentation.triggered.connect(self.openDocumentation)
		self.action_about.triggered.connect(self.openAbout)
	
	# -------------------------------------------------------------------------
	def connectTaskManagement(self) -> None:
		self.push_button_create.clicked.connect(self.clickOnCreate)
		self.push_button_remove.clicked.connect(self.clickOnRemove)
		self.push_button_edit.clicked.connect(self.clickOnEdit)
	
	# -------------------------------------------------------------------------
	def connectTaskRunning(self) -> None:
		self.push_button_run_all.clicked.connect(self.clickOnRunAll)
		self.push_button_cancel.clicked.connect(self.clickOnCancel)

	# -------------------------------------------------------------------------
	def connectTaskProperties(self) -> None:
		self.push_button_source.clicked.connect(self.selectSourceFolder)
		self.push_button_destination.clicked.connect(self.selectDestinationFile)
		self.button_group_packer_type.buttonClicked.connect(self.updatePackerType)
		self.cbox_compression_method.activated.connect(self.updateCompressionLevel)

	###########################################################################
	# SLOTS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def openOptions(self, s):
		dlg = Options(self)
		dlg.taskSuffixChanged.connect(self.__session.emitSuffixChanged)
		dlg.exec()
	
	# -------------------------------------------------------------------------
	def openAbout(self, s):
		dlg = About(self)
		dlg.exec()
	
	# -------------------------------------------------------------------------
	def selectSourceFolder(self):
		files_model = self.__selected_task.filesSelected()
		folder_selected = QFileDialog.getExistingDirectory(self, "Select folder", self.line_edit_source.text(), QFileDialog.Option.ShowDirsOnly)

		if folder_selected:
			self.line_edit_source.setText(folder_selected)
			files_model.setRootPath(folder_selected)
			self.tree_view_source.setRootIndex(files_model.index(folder_selected))
	
	# -------------------------------------------------------------------------
	def selectDestinationFile(self):
		raw_dest_file = self.__selected_task.rawDestFile()
		[raw_basename, _] = QFileDialog.getSaveFileName(self, "Select file", raw_dest_file)

		if raw_basename:
			self.__selected_task.setRawDstFile(raw_basename)
			# self.__task_view_mapper.submit()

	# -------------------------------------------------------------------------
	def updatePackerType(self, button: QtWidgets.QAbstractButton):
		print("[MainWindow][updatePackerType]")
		self.__packer_type_mapper.submit()
		self.__task_view_mapper.submit()

		self.cbox_compression_method.setCurrentIndex(0)
		self.cbox_compression_level.setCurrentIndex(0)
		self.updateCompressionMethod()

	# -------------------------------------------------------------------------
	def updateCompressionMethod(self):
		curr_index = self.cbox_compression_method.currentIndex()
		
		packer_data = self.__selected_task.packerData()
		info = packer_data.methodsInfo()
		self.cbox_compression_method.clear()
		for method in info:
			self.cbox_compression_method.addItem(method)
		
		self.cbox_compression_method.setCurrentIndex(curr_index)
		
		curr_index = self.cbox_compression_method.currentIndex()

		self.updateCompressionLevel()

	# -------------------------------------------------------------------------
	def updateCompressionLevel(self):
		curr_index = self.cbox_compression_level.currentIndex()
		c_method_curr_index = self.cbox_compression_method.currentIndex()

		packer_data = self.__selected_task.packerData()
		info = packer_data.levelsInfo()
		self.cbox_compression_level.clear()
		for level in info[c_method_curr_index]:
			self.cbox_compression_level.addItem(level)
		
		if self.cbox_compression_level.count() > curr_index:
			self.cbox_compression_level.setCurrentIndex(curr_index)
		else:
			self.cbox_compression_level.setCurrentIndex(0)
	
	# -------------------------------------------------------------------------
	def selectTask(self, row_num: int):
		self.table_view_session.selectRow(row_num)