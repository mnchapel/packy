"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# Python
import json
import os
from pathlib import Path
import shutil
import yaml

# PyQt
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QLibraryInfo, QLocale, QModelIndex, QTranslator, Qt, QCoreApplication, QItemSelection, QThreadPool, QStandardPaths, QUrl, Slot, qDebug
from PySide6.QtGui import QCloseEvent, QDesktopServices, QIcon
from PySide6.QtWidgets import QAbstractItemDelegate, QButtonGroup, QDataWidgetMapper, QFileDialog, QMainWindow, QPlainTextEdit, QMessageBox, QRadioButton, QWidget

# PackY
from packy.core.app_config import AppConfig
from packy.core.ui_strings import UIStrings
# from packy.models.archiver_config_model import ArchiveFormat, CompressionLevel, CompressionMethod, DataName, ArchiverConfigModel
from packy.models.archiver_config_model import ArchiveFormat, ArchiverConfigModel, CompressionLevel, CompressionMethod
from packy.models.packer_factory import createPacker
from packy.core.settings import Settings
from packy.models.progression import Progression
from packy.models.tasks_model import TasksModel
from packy.models.tasks_model import TaskProperties
from packy.models.session import Session
from packy.models.session_encoder import SessionEncoder
from packy.models.session_decoder import SessionDecoder
from packy.ui.radio_group_binder import RadioGroupBinder
from packy.views.messages_widget import MessagesWidget, MsgType
from packy.views.tree_view_proxy_model import TreeViewProxyModel
from packy.utils.external_data_access import ExternalData, external_data_path
from packy.views.about_dialog import AboutDialog
from packy.views.options_dialog import OptionsDialog
from packy.views.fix_warnings import FixWarnings
from packy.ui.ui_main_window import Ui_MainWindow
from typing import Any, override

###############################################################################
class MainWindow(QMainWindow):
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
    def __init__(self, config: AppConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.__log_folder_path = Path(config.LOG_FILE_PATH).parent
        self.__settings: Settings = Settings(self)
        self.__settings.setObjectName("settings")
        self.__archiver_model = ArchiverConfigModel(self)
        self.__archiver_model.setObjectName("archiver_model")
        self.__current_lang: str = "en-US"
        self.__translator: QTranslator = QTranslator()
        self.__qt_translator: QTranslator = QTranslator()
        self.__setup_ui()
        self.__setup_toolbar()
        self.__setup_menu_bar()
        self.__setup_widgets()
        self.__read_settings()
        self.__setup_connections()
        self.__initApplication()

        self.__thread_pool = QThreadPool()
        self.__thread_pool.setMaxThreadCount(1)
        self.__is_canceled = False

        self.__initConnects()
        # self.__initSessionView()
        # self.__initTaskView()
        # self.__initProgressionView()
        self.__setTitle()

        self.show()

    # -------------------------------------------------------------------------
    def __setup_ui(self) -> None:
        self.__ui: Ui_MainWindow = Ui_MainWindow()
        self.__ui.setupUi(self)
        icon = QIcon(":/img/logo")
        self.setWindowIcon(icon)

    # -------------------------------------------------------------------------
    def __setup_toolbar(self) -> None:
        pass

    # -------------------------------------------------------------------------
    def __setup_menu_bar(self) -> None:
        pass

    # -------------------------------------------------------------------------
    def __setup_widgets(self) -> None:
        # Messages widgets
        self.messages_view = MessagesWidget()

        # Archiver configuration widgets
        self.__formats_button_group = QButtonGroup(self)
        self.__formats_button_group.setObjectName("formats_button_group")
        for i, (archiver_format) in enumerate(ArchiveFormat.__members__.values()):
            format_radio = QRadioButton(self.__ui.output_group)
            format_radio.setText(self.tr(archiver_format.label))
            format_radio.setObjectName(f"{archiver_format.id}_format_radio")
            self.__formats_button_group.addButton(format_radio, archiver_format.id)
            column, row = divmod(i, 3)
            self.__ui.formats_grid_layout.addWidget(format_radio, row, column, 1, 1)

        for method in CompressionMethod.__members__.values():
            self.__ui.compression_method_combo.addItem(method.label, method)

        for level in CompressionLevel.__members__.values():
            self.__ui.compression_level_combo.addItem(level.label, level)

    # -------------------------------------------------------------------------
    def __read_settings(self) -> None:
        self.__settings.restore_layout_geometry(self)
        self.__settings.restore_main_window_state(self)

    # -------------------------------------------------------------------------
    def __write_settings(self) -> None:
        self.__settings.save_layout_geometry_for(self)
        self.__settings.save_main_window_state(self)

    # -------------------------------------------------------------------------
    def __setup_connections(self) -> None:
        self.__connect_file_menu_actions()
        self.__connect_help_menu_actions()
        self.__connect_archiver_config_widgets()

    # -------------------------------------------------------------------------
    def __connect_archiver_config_widgets(self) -> None:
        self.__archiver_widget_mapper = QDataWidgetMapper(self)
        self.__archiver_widget_mapper.setSubmitPolicy(QDataWidgetMapper.SubmitPolicy.AutoSubmit)
        self.__archiver_widget_mapper.setObjectName("archiver_widget_mapper")
        self.__archiver_widget_mapper.setOrientation(Qt.Orientation.Vertical)
        self.__archiver_widget_mapper.setModel(self.__archiver_model)
        self.__formats_button_binder = RadioGroupBinder(self.__formats_button_group, self)
        self.__formats_button_binder.setObjectName("formats_button_binder")
        self.__archiver_widget_mapper.addMapping(
            self.__formats_button_binder,
            ArchiverConfigModel.Column.FORMAT,
            b"selected_button",
        )
        self.__archiver_widget_mapper.addMapping(
            self.__ui.compression_method_combo,
            ArchiverConfigModel.Column.COMPRESSION,
            b"currentIndex",
        )
        self.__archiver_widget_mapper.addMapping(
            self.__ui.compression_level_combo,
            ArchiverConfigModel.Column.COMPRESSION_LEVEL,
            b"currentIndex",
        )
        self.__archiver_widget_mapper.toFirst()

    # -------------------------------------------------------------------------
    def __connect_file_menu_actions(self) -> None:
        # self.__ui.action_new_session.triggered.connect(self.__createNewSession)
        # self.__ui.action_save.triggered.connect(self.__saveSession)
        # self.__ui.action_save_as.triggered.connect(self.__saveSessionAs)
        # self.__ui.action_open.triggered.connect(self.__openSession)
        self.__ui.action_options.triggered.connect(self.__open_options_dialog)
        self.__ui.action_exit.triggered.connect(self.close)

    # -------------------------------------------------------------------------
    def __connect_help_menu_actions(self) -> None:
        self.__ui.action_open_log_folder.triggered.connect(self.__open_log_folder)
        self.__ui.action_github_repo.triggered.connect(self.__open_github_repo)
        self.__ui.action_about.triggered.connect(self.__open_about_dialog)

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __open_options_dialog(self) -> None:
        dialog = OptionsDialog(self.__settings, self)
        dialog.exec()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __open_log_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.__log_folder_path))

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __open_github_repo(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/mnchapel/packy"))

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __open_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    # -------------------------------------------------------------------------
    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        close_button = QMessageBox.question(
            self, self.windowTitle(), "Are you sure?\n",
            QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.Yes,
        )
        if close_button == QMessageBox.StandardButton.Yes:
            super().closeEvent(event)
            self.__write_settings()
            event.accept()
        else:
            event.ignore()

    # -------------------------------------------------------------------------
    @Slot(str, result=None)
    def __load_language(self, language_code: str) -> None:
         if(self.__current_lang != language_code):
            locale = QLocale(language_code)
            QLocale.setDefault(locale)
            QCoreApplication.removeTranslator(self.__qt_translator)
            QCoreApplication.removeTranslator(self.__translator)
            path = QLibraryInfo.location(QLibraryInfo.LibraryPath.TranslationsPath)
            if self.__qt_translator.load(locale, "qtbase", "_", path):
                QCoreApplication.installTranslator(self.__qt_translator)
            else:
                QtCore.qDebug(f"Translations for qtbase not loaded: {path} not found")
            path = f":/i18n/{language_code}"
            if self.__qt_translator.load(locale, path):
                QCoreApplication.installTranslator(self.__translator)
            else:
                QtCore.qDebug(f"Translations for {language_code} not loaded: {path} not found")



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
    def __initConnects(self) -> None:
        # self.__connectFileMenuActions()
        # self.__connectHelpMenuActions()
        # self.__connectTaskManagement()
        # self.__connectTaskRunning()
        # self.__connectTaskProperties()
        pass

    # -------------------------------------------------------------------------
    def __initSessionView(self) -> None:
        self.__session = Session()
        self.__ui.table_view_session.horizontalHeader().setVisible(True)
        self.__updateSessionViewModel()

    # -------------------------------------------------------------------------
    def __updateSessionViewModel(self) -> None:
        self.__ui.table_view_session.setModel(self.__session)
        self.__ui.table_view_session.selectionModel().selectionChanged.connect(self.__mapViewWithTask)

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
        self.__progression_mapper.addMapping(self.__ui.pbar_global_progress, 0, b"value")
        self.__progression_mapper.addMapping(self.__ui.pbar_task_progress, 1, b"value")
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
        task: TasksModel = self.__selected_task
        self.__task_view_mapper.setModel(task)
        self.__task_view_mapper.addMapping(
            self.__ui.line_edit_source, TaskProperties.SRC_FOLDER.value, b"text"
        )
        self.__task_view_mapper.addMapping(
            self.__ui.line_edit_destination, TaskProperties.DST_FILE.value, b"text"
        )
        self.__task_view_mapper.toFirst()

    # -------------------------------------------------------------------------
    def __updateFilesSelection(self) -> None:
        files_model = self.__selected_task.filesSelected()
        root_path = files_model.rootPath()

        filtering_model = TreeViewProxyModel(root_path)
        filtering_model.setSourceModel(files_model)
        self.__ui.tree_view_source.setModel(filtering_model)

        parent_index = files_model.index(root_path).parent()
        proxy_parent_index = filtering_model.mapFromSource(parent_index)
        self.__ui.tree_view_source.setRootIndex(proxy_parent_index)

        for col_index in range(1, files_model.columnCount()):
            self.__ui.tree_view_source.setColumnHidden(col_index, True)

        files_model.directoryLoaded.connect(self.__updateTreeChildren)

    # -------------------------------------------------------------------------
    def __updateTreeChildren(self, path: str) -> None:
        files_model = self.__selected_task.filesSelected()
        index = files_model.index(path)

        if files_model.filePath(index) != self.__ui.line_edit_source.text():
            parent_check_state = files_model.data(index, Qt.ItemDataRole.CheckStateRole)
            files_model.setData(index, parent_check_state, Qt.ItemDataRole.CheckStateRole)

    # -------------------------------------------------------------------------
    def __updatePackerViewMapper(self) -> None:
        packer_data = self.__selected_task.packerData()

        self.__updateCompressionMethod()

        self.__packer_mapper.setModel(packer_data)
        self.__packer_mapper.addMapping(
            self.__ui.compression_method_combo, DataName.COMPRESSION_METHOD.value, b"currentIndex"
        )
        self.__packer_mapper.toFirst()

        self.__updateCompressionLevel()

        self.__packer_mapper.addMapping(
            self.__ui.compression_level_combo, DataName.COMPRESSION_LEVEL.value, b"currentIndex"
        )
        self.__packer_mapper.toFirst()

        self.__updatePackerTypeViewMapper(packer_data)

    # -------------------------------------------------------------------------
    def __updatePackerTypeViewMapper(self, packer_data: ArchiverConfigModel) -> None:
        pass
        # packer_type_data = packer_data.packerTypeData()

        # self.__packer_type_mapper.setModel(packer_type_data)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_zip, 0)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_tar, 1)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_bz2, 2)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_tbz, 3)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_gz, 4)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_tgz, 5)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_lzma, 6)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_tlz, 7)
        # self.__packer_type_mapper.addMapping(self.__ui.rbutton_xz, 8)
        # self.__packer_type_mapper.toFirst()

    # -------------------------------------------------------------------------
    # ENABLE / DISABLE GUI
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    def __enableTaskProperties(self) -> None:
        self.__ui.group_box_file_selection.setEnabled(True)
        self.__ui.output_group.setEnabled(True)
        self.__ui.group_box_statistics.setEnabled(False)
        self.__disableUnavailablePackerType()

        self.__ui.push_button_create.setEnabled(False)
        self.__ui.push_button_remove.setEnabled(False)
        self.__ui.push_button_edit.setEnabled(True)
        self.__ui.push_button_edit.setText("Save")
        self.__ui.push_button_run_all.setEnabled(False)

        self.__ui.table_view_session.setEnabled(False)

    # -------------------------------------------------------------------------
    def __disableUnavailablePackerType(self) -> None:
        self.__ui.rbutton_tar.setEnabled(False)
        self.__ui.rbutton_bz2.setEnabled(False)
        self.__ui.rbutton_tbz.setEnabled(False)
        self.__ui.rbutton_gz.setEnabled(False)
        self.__ui.rbutton_tgz.setEnabled(False)
        self.__ui.rbutton_tlz.setEnabled(False)
        self.__ui.rbutton_xz.setEnabled(False)

    # -------------------------------------------------------------------------
    def __disableTaskProperties(self) -> None:
        self.__ui.group_box_file_selection.setEnabled(False)
        self.__ui.output_group.setEnabled(False)
        self.__ui.group_box_statistics.setEnabled(True)

        self.__ui.push_button_create.setEnabled(True)
        self.__ui.push_button_remove.setEnabled(True)
        self.__ui.push_button_edit.setEnabled(True)
        self.__ui.push_button_edit.setText("Edit")
        self.__ui.push_button_run_all.setEnabled(True)

        self.__ui.table_view_session.setEnabled(True)

    # -------------------------------------------------------------------------
    def __disableTask(self) -> None:
        self.__ui.push_button_create.setEnabled(False)
        self.__ui.push_button_remove.setEnabled(False)
        self.__ui.push_button_edit.setEnabled(False)
        self.__ui.push_button_run_all.setEnabled(False)
        self.__ui.push_button_cancel.setEnabled(True)

    # -------------------------------------------------------------------------
    def __enableTask(self) -> None:
        self.__ui.push_button_create.setEnabled(True)
        self.__ui.push_button_remove.setEnabled(True)
        self.__ui.push_button_edit.setEnabled(True)
        self.__ui.push_button_run_all.setEnabled(True)
        self.__ui.push_button_cancel.setEnabled(False)

    # -------------------------------------------------------------------------
    def __clearTaskProperties(self) -> None:
        self.__ui.line_edit_source.setText("")
        self.__ui.line_edit_destination.setText("")
        self.__ui.compression_method_combo.clear()
        self.__ui.compression_level_combo.clear()
        self.__ui.tree_view_source.setModel(None)

        checked_button = self.__formats_button_group.checkedButton()
        if checked_button:
            self.__formats_button_group.setExclusive(False)
            checked_button.setChecked(Fal__se)
            self.__formats_button_group.setExclusive(True)

    # -------------------------------------------------------------------------
    # CONNECT SIGNALS TO SLOTS
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    def __connectTaskManagement(self) -> None:
        self.__ui.push_button_create.clicked.connect(self.__createNewTask)
        self.__ui.push_button_remove.clicked.connect(self.__removeTask)
        self.__ui.push_button_edit.clicked.connect(self.__editTask)

    # -------------------------------------------------------------------------
    def __connectTaskRunning(self) -> None:
        self.__ui.push_button_run_all.clicked.connect(self.__runAll)
        self.__ui.push_button_cancel.clicked.connect(self.__cancelRun)

    # -------------------------------------------------------------------------
    def __connectTaskProperties(self) -> None:
        self.__ui.push_button_check_integrity.clicked.connect(self.__checkIntegrity)
        self.__ui.push_button_source.clicked.connect(self.__selectSourceFolder)
        self.__ui.push_button_destination.clicked.connect(self.__selectDestinationFile)
        self.__formats_button_group.buttonClicked.connect(self.__updatePackerType)
        self.__ui.compression_method_combo.activated.connect(self.__updateCompressionLevel)

    ###########################################################################
    # PRIVATE SLOTS
    ###########################################################################

    # -------------------------------------------------------------------------
    def __createNewSession(self) -> None:
        self.__session = Session()
        self.__updateSessionViewModel()
        self.__ui.push_button_remove.setEnabled(False)
        self.__ui.push_button_edit.setEnabled(False)
        self.__ui.push_button_run_all.setEnabled(False)
        self.__clearTaskProperties()
        self.__ui.pbar_global_progress.setFormat("%p%")
        self.__ui.pbar_task_progress.setFormat("%p%")
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
                        self.__ui.table_view_session.selectRow(0)
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
        self.__ui.table_view_session.selectRow(row_inserted)

        self.__enableTaskProperties()
        self.__updateCompressionMethod()
        self.__updateCompressionLevel()

    # -------------------------------------------------------------------------
    def __removeTask(self) -> None:
        model = self.__ui.table_view_session.model()
        current_row = self.__ui.table_view_session.currentIndex().row()
        model.removeRow(current_row)

        if self.__session.nbTasks() == 0:
            self.__ui.push_button_remove.setEnabled(False)
            self.__ui.push_button_edit.setEnabled(False)
            self.__ui.push_button_run_all.setEnabled(False)
            self.__clearTaskProperties()
            return
        elif current_row > self.__session.nbTasks():
            current_row -= 1

        self.__ui.table_view_session.selectRow(current_row)

    # -------------------------------------------------------------------------
    def __editTask(self) -> None:
        current_row = self.__ui.table_view_session.currentIndex().row()

        if current_row >= 0:
            if self.__ui.push_button_edit.text() == "Edit":
                self.__enableTaskProperties()
            else:
                self.__disableTaskProperties()


    # -------------------------------------------------------------------------
    def __checkIntegrity(self):
        self.__selected_task.checkIntegrity()

        dlg = FixWarnings(self.__selected_task.filesSelected(), self)
        dlg.exec()

    # -------------------------------------------------------------------------
    def __selectSourceFolder(self):
        files_model = self.__selected_task.filesSelected()
        selected_folder = QFileDialog.getExistingDirectory(
            self, "Select folder", self.__ui.line_edit_source.text(), QFileDialog.Option.ShowDirsOnly
        )

        if selected_folder:
            self.__ui.line_edit_source.setText(selected_folder)
            files_model.set_root_path(selected_folder)

            filtering_model = TreeViewProxyModel(selected_folder)
            filtering_model.setSourceModel(files_model)
            self.__ui.tree_view_source.setModel(filtering_model)

            parent_index = files_model.index(selected_folder).parent()
            proxy_parent_index = filtering_model.mapFromSource(parent_index)
            self.__ui.tree_view_source.setRootIndex(proxy_parent_index)

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

        self.__ui.compression_method_combo.setCurrentIndex(0)
        self.__ui.compression_level_combo.setCurrentIndex(0)
        self.__updateCompressionMethod()

    # -------------------------------------------------------------------------
    def __updateCompressionMethod(self):
        curr_index = self.__ui.compression_method_combo.currentIndex()

        packer_data = self.__selected_task.packerData()
        info = packer_data.methodsInfo()
        self.__ui.compression_method_combo.clear()
        for method in info:
            self.__ui.compression_method_combo.addItem(method)

        self.__ui.compression_method_combo.setCurrentIndex(curr_index)

        curr_index = self.__ui.compression_method_combo.currentIndex()

        self.__updateCompressionLevel()

    # -------------------------------------------------------------------------
    def __updateCompressionLevel(self):
        curr_index = self.__ui.compression_level_combo.currentIndex()
        c_method_curr_index = self.__ui.compression_method_combo.currentIndex()

        packer_data = self.__selected_task.packerData()
        info = packer_data.levelsInfo()
        self.__ui.compression_level_combo.clear()
        for level in info[c_method_curr_index]:
            self.__ui.compression_level_combo.addItem(level)

        if self.__ui.compression_level_combo.count() > curr_index:
            self.__ui.compression_level_combo.setCurrentIndex(curr_index)
        else:
            self.__ui.compression_level_combo.setCurrentIndex(0)

    # -------------------------------------------------------------------------
    def __mapViewWithTask(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        selected_row = self.__ui.table_view_session.currentIndex().row()
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

            self.__ui.pbar_global_progress.setFormat("%p%")
            self.__ui.pbar_task_progress.setFormat("%p%")

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

        self.__ui.pbar_global_progress.setFormat("Stopping...")
        self.__ui.pbar_task_progress.setFormat("Stopping...")
        self.__is_canceled = True

    # -------------------------------------------------------------------------
    def __runAllFinished(self):
        if self.__thread_pool.activeThreadCount() == 0:
            if self.__is_canceled:
                self.__ui.pbar_global_progress.setFormat("Stopped")
                self.__ui.pbar_task_progress.setFormat("Stopped")
                self.__is_canceled = False

            self.__enableTask()

            report = f"<b>{self.__progression.report()}</b>"
            QtCore.qInfo(report)
