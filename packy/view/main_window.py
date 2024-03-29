"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

#Python
import json
import os
import shutil
import yaml

# PyQt
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, QCoreApplication, QItemSelection, QThreadPool, QStandardPaths, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog, QPlainTextEdit, QMessageBox

# PackY
from model.packer_data import DataName, PackerData
from model.packer_factory import createPacker
from model.progression import Progression
from model.task import Task
from model.task import TaskProperties
from model.session import Session
from model.session_encoder import SessionEncoder
from model.session_decoder import SessionDecoder
from utils.external_data_access import ExternalData, external_data_path
from view.about import About
from view.options import Options
from view.fix_warnings import FixWarnings
from view.ui_main_window import Ui_MainWindow

###############################################################################
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

	###########################################################################
	# PRIVATE MEMBER VARIABLES
	# 
	# __thread_pool: 
	# __session: the current opened session.
	# __selected_task: the current selected task.
	# __progression: the progression model.
	# __progression_mapper: 
	# __task_view_mapper:
	# __packer_mapper: 
	# __packer_type_mapper: 
	# __is_canceled: 
	###########################################################################
    
	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, *args, obj=None, **kwargs) -> None:
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setupUi(self)

		self.__initApplication()
		self.__initLog()

		self.__thread_pool = QThreadPool()
		self.__thread_pool.setMaxThreadCount(1)
		self.__is_canceled = False

		self.__initConnects()
		self.__initSessionView()
		self.__initTaskView()
		self.__initProgressionView()
		self.__setTitle()

		self.show()
    
	###########################################################################
	# PRIVATE MEMBER METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __initApplication(self) -> None:
		metadata_path = external_data_path(ExternalData.METADATA)
		with open(metadata_path, "r") as metadata_file:
			metadata = yaml.safe_load(metadata_file)
			QCoreApplication.setOrganizationName(metadata["CompanyName"])
			QCoreApplication.setApplicationName(metadata["ProductName"])
			QCoreApplication.setOrganizationDomain("packy.fr")
			QCoreApplication.setApplicationVersion(metadata["Version"])

	# -------------------------------------------------------------------------
	def __initLog(self) -> None:
		if not hasattr(MainWindow, "log_panel"):
			MainWindow.log_panel: QPlainTextEdit = self.log_panel
		
		if not hasattr(MainWindow, "log_file_path"):
			app_data_location = QStandardPaths.StandardLocation.AppDataLocation
			folder_path = QStandardPaths.writableLocation(app_data_location)
			MainWindow.log_file_path: str = folder_path + "/log.txt"

			if not os.path.exists(MainWindow.log_file_path):
				os.makedirs(os.path.dirname(MainWindow.log_file_path))
			
			self.__cleanPreviousSessionLog()
	
	# -------------------------------------------------------------------------
	def __cleanPreviousSessionLog(self) -> None:
			open(MainWindow.log_file_path, "w").close()

	# -------------------------------------------------------------------------
	def __initConnects(self) -> None:
		self.__connectFileMenuActions()
		self.__connectHelpMenuActions()
		self.__connectTaskManagement()
		self.__connectTaskRunning()
		self.__connectTaskProperties()
	
	# -------------------------------------------------------------------------
	def __initSessionView(self) -> None:
		self.__session = Session()
		self.table_view_session.horizontalHeader().setVisible(True)
		self.__updateSessionViewModel()

	# -------------------------------------------------------------------------
	def __updateSessionViewModel(self) -> None:
		self.table_view_session.setModel(self.__session)
		self.table_view_session.selectionModel().selectionChanged.connect(self.__mapViewWithTask)

	# -------------------------------------------------------------------------
	def __initTaskView(self) -> None:
		self.__createTaskMapper()
		self.__createPackerMapper()
	
	# -------------------------------------------------------------------------
	def __initProgressionView(self) -> None:
		self.__progression = Progression()
		
		self.__progression_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__progression_mapper.setOrientation(Qt.Orientation.Vertical)
		self.__progression_mapper.setModel(self.__progression)
		self.__progression_mapper.addMapping(self.pbar_global_progress, 0, b"value")
		self.__progression_mapper.addMapping(self.pbar_task_progress, 1, b"value")
		self.__progression_mapper.toFirst()
	
	# -------------------------------------------------------------------------
	def __createTaskMapper(self) -> None:
		self.__task_view_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__task_view_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def __createPackerMapper(self) -> None:
		self.__packer_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__packer_mapper.setOrientation(Qt.Orientation.Vertical)

		self.__createPackerTypeMapper()

	# -------------------------------------------------------------------------
	def __createPackerTypeMapper(self) -> None:
		self.__packer_type_mapper = QtWidgets.QDataWidgetMapper(self)
		self.__packer_type_mapper.setOrientation(Qt.Orientation.Vertical)

	# -------------------------------------------------------------------------
	def __setTitle(self, session_name=None) -> None:
		title = "PackY - "

		if session_name is None:
			title = title + "Untitled session"
		else:
			title = title + session_name

		self.setWindowTitle(title)

	# -------------------------------------------------------------------------
	def __initTasksStatus(self) -> None:
		tasks = self.__session.tasks()
		for task in tasks:
			task.initStatus()
	
	# -------------------------------------------------------------------------
	def __updateTaskViewMapper(self) -> None:
		task: Task = self.__selected_task
		self.__task_view_mapper.setModel(task)
		self.__task_view_mapper.addMapping(self.line_edit_source, TaskProperties.SRC_FOLDER.value, b"text")
		self.__task_view_mapper.addMapping(self.line_edit_destination, TaskProperties.DST_FILE.value, b"text")
		self.__task_view_mapper.toFirst()
	
	# -------------------------------------------------------------------------
	def __updateFilesSelection(self) -> None:
		files_model = self.__selected_task.filesSelected()

		self.tree_view_source.setModel(files_model)
		self.tree_view_source.setRootIndex(files_model.index(files_model.rootPath()))
		
		for col_index in range(1, files_model.columnCount()):
			self.tree_view_source.setColumnHidden(col_index, True)

		files_model.directoryLoaded.connect(self.__updateTreeChildren)
	
	# -------------------------------------------------------------------------
	def __updateTreeChildren(self, path: str) -> None:
		files_model = self.__selected_task.filesSelected()
		index = files_model.index(path)

		if files_model.filePath(index) != self.line_edit_source.text():
			parent_check_state = files_model.data(index, Qt.ItemDataRole.CheckStateRole)
			files_model.setData(index, parent_check_state, Qt.ItemDataRole.CheckStateRole)
	
	# -------------------------------------------------------------------------
	def __updatePackerViewMapper(self) -> None:
		packer_data = self.__selected_task.packerData()

		self.__updateCompressionMethod()
		
		self.__packer_mapper.setModel(packer_data)
		self.__packer_mapper.addMapping(self.cbox_compression_method, DataName.COMPRESSION_METHOD.value, b"currentIndex")
		self.__packer_mapper.toFirst()

		self.__updateCompressionLevel()
		
		self.__packer_mapper.addMapping(self.cbox_compression_level, DataName.COMPRESSION_LEVEL.value, b"currentIndex")
		self.__packer_mapper.toFirst()

		self.__updatePackerTypeViewMapper(packer_data)
	
	# -------------------------------------------------------------------------
	def __updatePackerTypeViewMapper(self, packer_data: PackerData) -> None:

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
	# ENABLE / DISABLE GUI
	# -------------------------------------------------------------------------

	# -------------------------------------------------------------------------
	def __enableTaskProperties(self) -> None:
		self.group_box_file_selection.setEnabled(True)
		self.group_box_output_properties.setEnabled(True)
		self.group_box_statistics.setEnabled(False)
		self.__disableUnavailablePackerType()

		self.push_button_create.setEnabled(False)
		self.push_button_remove.setEnabled(False)
		self.push_button_edit.setEnabled(True)
		self.push_button_edit.setText("Save")
		self.push_button_run_all.setEnabled(False)

		self.table_view_session.setEnabled(False)
	
	# -------------------------------------------------------------------------
	def __disableUnavailablePackerType(self) -> None:
		self.rbutton_tar.setEnabled(False)
		self.rbutton_bz2.setEnabled(False)
		self.rbutton_tbz.setEnabled(False)
		self.rbutton_gz.setEnabled(False)
		self.rbutton_tgz.setEnabled(False)
		self.rbutton_tlz.setEnabled(False)
		self.rbutton_xz.setEnabled(False)

	# -------------------------------------------------------------------------
	def __disableTaskProperties(self) -> None:
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
	def __disableTask(self) -> None:
		self.push_button_create.setEnabled(False)
		self.push_button_remove.setEnabled(False)
		self.push_button_edit.setEnabled(False)
		self.push_button_run_all.setEnabled(False)
		self.push_button_cancel.setEnabled(True)

	# -------------------------------------------------------------------------
	def __enableTask(self) -> None:
		self.push_button_create.setEnabled(True)
		self.push_button_remove.setEnabled(True)
		self.push_button_edit.setEnabled(True)
		self.push_button_run_all.setEnabled(True)
		self.push_button_cancel.setEnabled(False)

	# -------------------------------------------------------------------------
	def __clearTaskProperties(self) -> None:
		self.line_edit_source.setText("")
		self.line_edit_destination.setText("")
		self.cbox_compression_method.clear()
		self.cbox_compression_level.clear()
		self.tree_view_source.setModel(None)

		checked_button = self.button_group_packer_type.checkedButton()
		if checked_button:
			self.button_group_packer_type.setExclusive(False)
			checked_button.setChecked(False)
			self.button_group_packer_type.setExclusive(True)
		
	# -------------------------------------------------------------------------
	# CONNECT SIGNALS TO SLOTS
	# -------------------------------------------------------------------------

	# -------------------------------------------------------------------------
	def __connectFileMenuActions(self) -> None:
		self.action_new_session.triggered.connect(self.__createNewSession)
		self.action_save.triggered.connect(self.__saveSession)
		self.action_save_as.triggered.connect(self.__saveSessionAs)
		self.action_open.triggered.connect(self.__openSession)
		self.action_options.triggered.connect(self.__openOptions)
		self.action_exit.triggered.connect(self.close)

	# -------------------------------------------------------------------------
	def __connectHelpMenuActions(self) -> None:
		self.action_github_repo.triggered.connect(self.__openGitHubRepo)
		self.action_about.triggered.connect(self.__openAbout)
	
	# -------------------------------------------------------------------------
	def __connectTaskManagement(self) -> None:
		self.push_button_create.clicked.connect(self.__createNewTask)
		self.push_button_remove.clicked.connect(self.__removeTask)
		self.push_button_edit.clicked.connect(self.__editTask)
	
	# -------------------------------------------------------------------------
	def __connectTaskRunning(self) -> None:
		self.push_button_run_all.clicked.connect(self.__runAll)
		self.push_button_cancel.clicked.connect(self.__cancelRun)

	# -------------------------------------------------------------------------
	def __connectTaskProperties(self) -> None:
		self.push_button_check_integrity.clicked.connect(self.__checkIntegrity)
		self.push_button_source.clicked.connect(self.__selectSourceFolder)
		self.push_button_destination.clicked.connect(self.__selectDestinationFile)
		self.button_group_packer_type.buttonClicked.connect(self.__updatePackerType)
		self.cbox_compression_method.activated.connect(self.__updateCompressionLevel)

	###########################################################################
	# PRIVATE SLOTS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def __createNewSession(self) -> None:
		self.__session = Session()
		self.__updateSessionViewModel()
		self.push_button_remove.setEnabled(False)
		self.push_button_edit.setEnabled(False)
		self.push_button_run_all.setEnabled(False)
		self.__clearTaskProperties()
		self.pbar_global_progress.setFormat("%p%")
		self.pbar_task_progress.setFormat("%p%")
		self.__progression.init()
		self.__setTitle()
	
	# -------------------------------------------------------------------------
	def __openSession(self, s) -> None:
		[filename, _] = QFileDialog.getOpenFileName(self, "Open session", "", "JSON (*.json)")
		if filename:
			with open(filename, "r") as file:
				self.__session = json.load(file, cls=SessionDecoder)
				if self.__session is not None:
					self.__updateSessionViewModel()
					self.__setTitle(self.__session.name())
					if self.__session.nbTasks() > 0:
						self.__selected_task = self.__session.taskAt(0)
						self.table_view_session.selectRow(0)
						self.__disableTaskProperties()
		
	# -------------------------------------------------------------------------
	def __saveSession(self, s) -> None:
		if not self.__session.name():
			self.__saveSessionAs(s)
		else:
			dst_file_path = self.__session.outputFile()
			tmp_dst_file_path = dst_file_path + "~"
			
			try:
				output_file = open(tmp_dst_file_path, "w")
				json.dump(self.__session, output_file, cls=SessionEncoder, indent=4)
				output_file.close()
			except (IOError, shutil.SameFileError) as ex:
				error_msg = type(ex).__name__ + ": " + str(ex)
				QtCore.qCritical(error_msg)
			else:
				shutil.copy(tmp_dst_file_path, dst_file_path)
			finally:
				os.remove(tmp_dst_file_path)

	# -------------------------------------------------------------------------
	def __saveSessionAs(self, s) -> None:
		[filename, _] = QFileDialog.getSaveFileName(self, "Save As", "", "JSON (*.json)")
		if filename:
			self.__session.setName(filename)
			self.__setTitle(self.__session.name())
			dst_file_path = self.__session.outputFile()
			with open(dst_file_path, "w") as output_file:
				json.dump(self.__session, output_file, cls=SessionEncoder, indent=4)
	
	# -------------------------------------------------------------------------
	def __createNewTask(self) -> None:
		row_inserted = self.__session.insertRow()

		self.__selected_task = self.__session.taskAt(row_inserted)
		self.table_view_session.selectRow(row_inserted)

		self.__enableTaskProperties()
		self.__updateCompressionMethod()
		self.__updateCompressionLevel()
	
	# -------------------------------------------------------------------------
	def __removeTask(self) -> None:
		model = self.table_view_session.model()
		current_row = self.table_view_session.currentIndex().row()
		model.removeRow(current_row)
		
		if self.__session.nbTasks() == 0:
			self.push_button_remove.setEnabled(False)
			self.push_button_edit.setEnabled(False)
			self.push_button_run_all.setEnabled(False)
			self.__clearTaskProperties()
			return
		elif current_row > self.__session.nbTasks():
			current_row -= 1
		
		self.table_view_session.selectRow(current_row)
	
	# -------------------------------------------------------------------------
	def __editTask(self) -> None:
		current_row = self.table_view_session.currentIndex().row()
		
		if current_row >= 0:
			if self.push_button_edit.text() == "Edit":
				self.__enableTaskProperties()
			else:
				self.__disableTaskProperties()
	
	# -------------------------------------------------------------------------
	def __openOptions(self, s):
		dlg = Options(self)
		dlg.taskSuffixChanged.connect(self.__session.emitSuffixChanged)
		dlg.exec()

	# -------------------------------------------------------------------------
	def __openGitHubRepo(self, s) -> None:
		QDesktopServices.openUrl(QUrl("https://github.com/mnchapel/packy"))
	
	# -------------------------------------------------------------------------
	def __openAbout(self, s):
		dlg = About(self)
		dlg.exec()

	# -------------------------------------------------------------------------
	def __checkIntegrity(self):
		self.__selected_task.checkIntegrity()

		dlg = FixWarnings(self.__selected_task.filesSelected(), self)
		dlg.exec()
	
	# -------------------------------------------------------------------------
	def __selectSourceFolder(self):
		files_model = self.__selected_task.filesSelected()
		folder_selected = QFileDialog.getExistingDirectory(self, "Select folder", self.line_edit_source.text(), QFileDialog.Option.ShowDirsOnly)

		if folder_selected:
			self.line_edit_source.setText(folder_selected)
			files_model.setRootPath(folder_selected)
			self.tree_view_source.setRootIndex(files_model.index(folder_selected))
	
	# -------------------------------------------------------------------------
	def __selectDestinationFile(self):
		raw_dest_file = self.__selected_task.rawDestFile()
		[raw_basename, _] = QFileDialog.getSaveFileName(self, "Select file", raw_dest_file)

		if raw_basename:
			self.__selected_task.setRawDstFile(raw_basename)

	# -------------------------------------------------------------------------
	def __updatePackerType(self, button: QtWidgets.QAbstractButton):
		self.__packer_type_mapper.submit()
		self.__task_view_mapper.submit()

		self.cbox_compression_method.setCurrentIndex(0)
		self.cbox_compression_level.setCurrentIndex(0)
		self.__updateCompressionMethod()

	# -------------------------------------------------------------------------
	def __updateCompressionMethod(self):
		curr_index = self.cbox_compression_method.currentIndex()
		
		packer_data = self.__selected_task.packerData()
		info = packer_data.methodsInfo()
		self.cbox_compression_method.clear()
		for method in info:
			self.cbox_compression_method.addItem(method)
		
		self.cbox_compression_method.setCurrentIndex(curr_index)
		
		curr_index = self.cbox_compression_method.currentIndex()

		self.__updateCompressionLevel()

	# -------------------------------------------------------------------------
	def __updateCompressionLevel(self):
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
	def __mapViewWithTask(self, selected: QItemSelection, deselected: QItemSelection) -> None:
		selected_row = self.table_view_session.currentIndex().row()
		self.__selected_task = self.__session.taskAt(selected_row)

		self.__updateTaskViewMapper()
		self.__updatePackerViewMapper()
		self.__updateFilesSelection()
	
	# -------------------------------------------------------------------------
	def __runAll(self) -> None:
		nb_checked_tasks = self.__session.nbCheckedTasks()

		if nb_checked_tasks == 0:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Icon.Warning)
			msg.setText("Nothing to run!")
			msg.setInformativeText("Please select at least one task.")
			msg.setWindowTitle("Warning")
			msg.exec()
		else:
			self.__initTasksStatus()
			self.__disableTask()

			self.__progression.init()
			self.__progression.setNbTask(self.__session.nbCheckedTasks())
			
			self.pbar_global_progress.setFormat("%p%")
			self.pbar_task_progress.setFormat("%p%")

			tasks = self.__session.tasks()

			for task in tasks:
				if task.isChecked() == Qt.CheckState.Checked.value:
					packer = createPacker(task)
					packer.signals.info.connect(lambda msg: QtCore.qInfo(msg))
					packer.signals.error.connect(self.__progression.errorReported)
					packer.signals.progress.connect(self.__progression.updateTaskProgress)
					packer.signals.finish.connect(self.__progression.updateGlobalProgress)
					self.__thread_pool.start(packer)
					packer.signals.finish.connect(self.__runAllFinished)
	
	# -------------------------------------------------------------------------
	def __cancelRun(self) -> None:
		self.__thread_pool.clear()
		QtCore.qInfo("<b>Cancel. Waiting for the current task to finish.<b>")

		self.pbar_global_progress.setFormat("Stopping...")
		self.pbar_task_progress.setFormat("Stopping...")
		self.__is_canceled = True

	# -------------------------------------------------------------------------
	def __runAllFinished(self):
		if self.__thread_pool.activeThreadCount() == 0:
			
			if self.__is_canceled:
				self.pbar_global_progress.setFormat("Stopped")
				self.pbar_task_progress.setFormat("Stopped")
				self.__is_canceled = False

			self.__enableTask()

			report = f"<b>{self.__progression.report()}</b>"
			QtCore.qInfo(report)
