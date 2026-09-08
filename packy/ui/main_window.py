"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# Future library
from __future__ import annotations

# Local application
from packy.constants.settings_keys import MainWindowSettings
from packy.core.archiver_config_panel import ArchiverConfigPanel
from packy.core.batch import Batch
from packy.core.batch_workspace import BatchWorkspace
from packy.ui.about_dialog import AboutDialog
from packy.ui.options_dialog import OptionsDialog
from packy.ui.ui_main_window import Ui_MainWindow

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import QByteArray, QUrl, Slot
from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QWidget,
)

# Standard library
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Final, override

if TYPE_CHECKING:
    # Local application
    from packy.core.app_config import AppConfig
    from packy.core.user_settings import UserSettings


###############################################################################
class MainWindow(QMainWindow):
    # -------------------------------------------------------------------------
    def __init__(
        self,
        config: AppConfig,
        settings: UserSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self._log_folder_path: Final[Path] = Path(config.LOG_FILE_PATH).parent
        self._settings: Final[UserSettings] = settings

        self._setup_ui(config)
        self._setup_menu_bar(config)
        self._setup_toolbar(config)
        self._setup_central_widgets(config)
        self._setup_menu_connections(config)

        self._batch_workspace: BatchWorkspace = BatchWorkspace(
            config.MAX_RECENT_BATCHES,
            self,
        )
        self._archiver_config_panel: ArchiverConfigPanel = ArchiverConfigPanel(
            self._ui,
            self,
        )

        self._batch_workspace.batch_opened.connect(self._on_workspace_batch_opened)
        self._batch_workspace.batch_closed.connect(self._on_workspace_batch_closed)
        self._batch_workspace.recent_batches_changed.connect(self._update_recent_batches_menu)

        self._update_window_title()
        self._update_actions()
        QtCore.qDebug(f"{self.__class__.__name__} initialized.")
        # self.__thread_pool = QThreadPool()
        # self.__thread_pool.setMaxThreadCount(1)
        # self.__is_canceled = False

    # -------------------------------------------------------------------------
    def _setup_ui(self, _config: AppConfig) -> None:
        self._ui: Ui_MainWindow = Ui_MainWindow()
        self._ui.setupUi(self)  # pyright: ignore[reportUnknownMemberType]
        icon = QIcon(":/img/logo")
        self.setWindowIcon(icon)

    # -------------------------------------------------------------------------
    def _setup_menu_bar(self, config: AppConfig) -> None:
        # Add recent file actions to the recent batches menu
        separator = self._ui.menu_open_recent.insertSeparator(self._ui.action_clear_list)
        separator.setObjectName("separator_clear_list")

        self._recent_batch_actions: list[QAction] = []
        for _ in range(config.MAX_RECENT_BATCHES):
            action = QAction(self)
            action.setVisible(False)
            action.triggered.connect(partial(self._open_recent_batch, action))
            self._recent_batch_actions.append(action)
            self._ui.menu_open_recent.insertAction(separator, action)

        self._ui.menu_open_recent.setToolTipsVisible(True)

    # -------------------------------------------------------------------------
    def _setup_toolbar(self, _config: AppConfig) -> None:
        pass

    # -------------------------------------------------------------------------
    def _setup_central_widgets(self, _config: AppConfig) -> None:
        pass

    # -------------------------------------------------------------------------
    def _setup_menu_connections(self, _config: AppConfig) -> None:
        self._connect_file_menu_actions()
        self._connect_help_menu_actions()

    # -------------------------------------------------------------------------
    def _connect_file_menu_actions(self) -> None:
        self._ui.action_new_batch.triggered.connect(self._new_batch)
        self._ui.action_open_batch.triggered.connect(self._open_batch)
        self._ui.action_save_batch.triggered.connect(self._save_batch)
        self._ui.action_save_batch_as.triggered.connect(self._save_batch_as)
        self._ui.action_options.triggered.connect(self._show_options)
        self._ui.action_close_batch.triggered.connect(self._close_batch)
        self._ui.action_exit.triggered.connect(self.close)

    # -------------------------------------------------------------------------
    def _connect_help_menu_actions(self) -> None:
        self._ui.action_open_log_folder.triggered.connect(self._open_log_folder)
        self._ui.action_github_repo.triggered.connect(self._open_github_repo)
        self._ui.action_about.triggered.connect(self._show_about)

    # -------------------------------------------------------------------------
    @property
    def batch_workspace(self) -> BatchWorkspace:
        """The workspace where the batch lives and can be modified."""
        return self._batch_workspace

    # -------------------------------------------------------------------------
    @property
    def archiver_config_panel(self) -> ArchiverConfigPanel:
        """The panel where the archiver configuration can be modified."""
        return self._archiver_config_panel

    # -------------------------------------------------------------------------
    def load_settings(self) -> None:
        # Load MainWindow
        QtCore.qDebug(
            f"Loading {self.objectName()} settings from {MainWindowSettings.SETTINGS_GROUP}.",
        )
        self._settings.begin_group(MainWindowSettings.SETTINGS_GROUP)
        self._settings.restore_layout_geometry_for(self)
        state: QByteArray = self._settings.value(MainWindowSettings.STATE, QByteArray())
        self.restoreState(state)
        self._settings.end_group()

        # Load other components
        self._batch_workspace.load_settings(self._settings)
        self._archiver_config_panel.load_settings(self._settings)

    # -------------------------------------------------------------------------
    def save_settings(self) -> None:
        # Save MainWindow
        QtCore.qDebug(
            f"Saving {self.objectName()} settings in {MainWindowSettings.SETTINGS_GROUP}.",
        )
        self._settings.begin_group(MainWindowSettings.SETTINGS_GROUP)
        self._settings.save_layout_geometry_for(self)
        self._settings.set_value(MainWindowSettings.STATE, self.saveState())
        self._settings.end_group()

        # Save other components
        self._batch_workspace.save_settings(self._settings)
        self._archiver_config_panel.save_settings(self._settings)

    # -------------------------------------------------------------------------
    def restore_last_batch(self) -> None:
        QtCore.qDebug("Restoring last batch if exists in the history.")
        if self._batch_workspace.open_last_batch():
            QtCore.qDebug(f"Last batch restored: '{self._batch_workspace.current_batch}'.")
        else:
            QtCore.qDebug("Last batch restoration was canceled.")

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _new_batch(self) -> None:
        new_batch: Batch | None = self._batch_workspace.create_batch()
        if new_batch is None:
            return

        response: QMessageBox.StandardButton = QMessageBox.question(
            self,
            self.tr("New Batch Created"),
            self.tr("The new batch is ready. Do you want to open it?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if response == QMessageBox.StandardButton.Yes:
            self._batch_workspace.activate_batch(new_batch)

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _open_batch(self) -> None:
        self._batch_workspace.open_batch()

    # -------------------------------------------------------------------------
    @Slot(QAction, result=None)
    def _open_recent_batch(self, action: QAction) -> None:
        batch_file: Path = action.data()
        self._batch_workspace.open_recent_batch(batch_file)

    # -------------------------------------------------------------------------
    @Slot(result=bool)
    def _save_batch(self) -> bool:
        return self._batch_workspace.save_current_batch()

    # -------------------------------------------------------------------------
    @Slot(result=bool)
    def _save_batch_as(self) -> bool:
        return self._batch_workspace.save_current_batch_as()

    # -------------------------------------------------------------------------
    @Slot(result=bool)
    def _close_batch(self) -> bool:
        return self._batch_workspace.close_current_batch()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _show_options(self) -> None:
        dialog = OptionsDialog(self._settings, self)
        dialog.load_settings(self._settings)
        dialog.exec()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _open_log_folder(self) -> None:
        QDesktopServices.openUrl(QUrl.fromLocalFile(self._log_folder_path))

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _open_github_repo(self) -> None:
        QDesktopServices.openUrl(QUrl("https://github.com/mnchapel/packy"))

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    # -------------------------------------------------------------------------
    @override
    def closeEvent(self, event: QCloseEvent) -> None:
        QtCore.qDebug(f"Closing {self.objectName()}.")
        # close_button = QMessageBox.question(
        #     self, self.windowTitle(), "Are you sure?\n",
        #     QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes,
        #     QMessageBox.StandardButton.Yes,
        # )
        # if close_button == QMessageBox.StandardButton.Yes:
        if self._batch_workspace.close_current_batch():
            super().closeEvent(event)
            event.accept()
        else:
            event.ignore()
        # else:
        #     event.ignore()

    # -------------------------------------------------------------------------
    @Slot(Batch, result=None)
    def _on_workspace_batch_opened(self, new_batch: Batch) -> None:
        new_batch.file_path_changed.connect(self._update_window_title)
        new_batch.modified_changed.connect(self._update_window_title)

        self._archiver_config_panel.set_current_batch(new_batch)

        self._update_window_title()
        self._update_actions()

    # -------------------------------------------------------------------------
    @Slot(Batch, result=None)
    def _on_workspace_batch_closed(self, old_batch: Batch) -> None:
        old_batch.disconnect(self)

        self._archiver_config_panel.set_current_batch(None)

        self._update_window_title()
        self._update_actions()

    # -------------------------------------------------------------------------
    def _update_window_title(self) -> None:
        current_batch: Batch | None = self._batch_workspace.current_batch
        if current_batch is not None:
            self.setWindowTitle(current_batch.display_name + " - PackY")
            self.setWindowFilePath(str(current_batch.file_path))
            self.setWindowModified(current_batch.is_modified)
        else:
            self.setWindowTitle("PackY")
            self.setWindowFilePath("")
            self.setWindowModified(False)

    # -------------------------------------------------------------------------
    def _update_actions(self) -> None:
        has_current_batch = self._batch_workspace.has_current_batch()
        self._ui.action_save_batch.setEnabled(has_current_batch)
        self._ui.action_save_batch_as.setEnabled(has_current_batch)
        self._ui.action_close_batch.setEnabled(has_current_batch)

        # self.__ui.job_queue_table_view.setEnabled(has_current_batch)
        self._ui.create_job_button.setEnabled(has_current_batch)
        self._ui.remove_job_button.setEnabled(False)
        self._ui.save_job_button.setEnabled(False)
        self._ui.move_up_job_button.setEnabled(False)
        self._ui.move_down_job_button.setEnabled(False)
        self._ui.run_all_jobs_button.setEnabled(False)
        self._ui.cancel_jobs_button.setEnabled(False)

        self._ui.statistics_group.setEnabled(False)
        self._ui.file_selection_group.setEnabled(False)
        self._ui.output_group.setEnabled(False)

    # -------------------------------------------------------------------------
    @Slot(list, result=None)
    def _update_recent_batches_menu(self, recently_opened: list[Path]) -> None:
        files: list[Path] = recently_opened
        actions: list[QAction] = self._recent_batch_actions

        for action, file in zip(actions, files, strict=False):
            action.setText(file.name)
            action.setData(file)
            action.setVisible(True)
            action.setToolTip(str(file))

        nb_visible_actions = min(len(files), len(actions))
        for action in actions[nb_visible_actions:]:
            action.setVisible(False)

        self._ui.menu_open_recent.setEnabled(nb_visible_actions > 0)

    ###########################################################################
    # PRIVATE MEMBER METHODS
    ###########################################################################

    # # -------------------------------------------------------------------------
    # def __initSessionView(self) -> None:
    #     self.__session = Session()
    #     self.__ui.job_queue_table_view.horizontalHeader().setVisible(True)
    #     self.__updateSessionViewModel()

    # # -------------------------------------------------------------------------
    # def __updateSessionViewModel(self) -> None:
    #     self.__ui.job_queue_table_view.setModel(self.__session)
    #     self.__ui.job_queue_table_view.selectionModel().selectionChanged.connect(self.__mapViewWithTask)

    # # -------------------------------------------------------------------------
    # def __initTaskView(self) -> None:
    #     self.__createTaskMapper()
    #     self.__createPackerMapper()

    # # -------------------------------------------------------------------------
    # def __initProgressionView(self) -> None:
    #     self.__progression = Progression()

    #     self.__progression_mapper = QtWidgets.QDataWidgetMapper(self)
    #     self.__progression_mapper.setOrientation(Qt.Orientation.Vertical)
    #     self.__progression_mapper.setModel(self.__progression)
    #     self.__progression_mapper.addMapping(self.__ui.global_progress_bar, 0, b"value")
    #     self.__progression_mapper.addMapping(self.__ui.job_progress_bar, 1, b"value")
    #     self.__progression_mapper.toFirst()

    # # ----------------
    # # -------------------------------------------------------------------------
    # def __initTasksStatus(self) -> None:
    #     tasks = self.__session.tasks()
    #     for task in tasks:
    #         task.initStatus()

    # # -------------------------------------------------------------------------
    # def __updateTaskViewMapper(self) -> None:
    #     task: TaskListModel = self.__selected_task
    #     self.__task_view_mapper.setModel(task)
    #     self.__task_view_mapper.addMapping(
    #         self.__ui.source_folder_input, TaskProperties.SRC_FOLDER.value, b"text"
    #     )
    #     self.__task_view_mapper.addMapping(
    #         self.__ui.destination_folder_input, TaskProperties.DST_FILE.value, b"text"
    #     )
    #     self.__task_view_mapper.toFirst()

    # # -------------------------------------------------------------------------
    # def __updateFilesSelection(self) -> None:
    #     files_model = self.__selected_task.filesSelected()
    #     root_path = files_model.rootPath()

    #     filtering_model = TreeViewProxyModel(root_path)
    #     filtering_model.setSourceModel(files_model)
    #     self.__ui.source_files_tree_view.setModel(filtering_model)

    #     parent_index = files_model.index(root_path).parent()
    #     proxy_parent_index = filtering_model.mapFromSource(parent_index)
    #     self.__ui.source_files_tree_view.setRootIndex(proxy_parent_index)

    #     for col_index in range(1, files_model.columnCount()):
    #         self.__ui.source_files_tree_view.setColumnHidden(col_index, True)

    #     files_model.directoryLoaded.connect(self.__updateTreeChildren)

    # # -------------------------------------------------------------------------
    # def __updateTreeChildren(self, path: str) -> None:
    #     files_model = self.__selected_task.filesSelected()
    #     index = files_model.index(path)

    #     if files_model.filePath(index) != self.__ui.source_folder_input.text():
    #         parent_check_state = files_model.data(index, Qt.ItemDataRole.CheckStateRole)
    #         files_model.setData(index, parent_check_state, Qt.ItemDataRole.CheckStateRole)

    # # -------------------------------------------------------------------------
    # def __updatePackerViewMapper(self) -> None:
    #     packer_data = self.__selected_task.packerData()

    #     self.__updateCompressionMethod()

    #     self.__packer_mapper.setModel(packer_data)
    #     self.__packer_mapper.addMapping(
    #         self.__ui.compression_method_combo, DataName.COMPRESSION_METHOD.value, b"currentIndex"
    #     )
    #     self.__packer_mapper.toFirst()

    #     self.__updateCompressionLevel()

    #     self.__packer_mapper.addMapping(
    #         self.__ui.compression_level_combo, DataName.COMPRESSION_LEVEL.value, b"currentIndex"
    #     )
    #     self.__packer_mapper.toFirst()

    #     self.__updatePackerTypeViewMapper(packer_data)

    # # -------------------------------------------------------------------------
    # # ENABLE / DISABLE GUI
    # # -------------------------------------------------------------------------

    # # -------------------------------------------------------------------------
    # def __enableTaskProperties(self) -> None:
    #     self.__ui.file_selection_group.setEnabled(True)
    #     self.__ui.output_group.setEnabled(True)
    #     self.__ui.statistics_group.setEnabled(False)
    #     self.__disableUnavailablePackerType()

    #     self.__ui.create_job_button.setEnabled(False)
    #     self.__ui.remove_job_button.setEnabled(False)
    #     self.__ui.save_job_button.setEnabled(True)
    #     self.__ui.run_all_jobs_button.setEnabled(False)

    #     self.__ui.job_queue_table_view.setEnabled(False)

    # # -------------------------------------------------------------------------
    # def __disableTaskProperties(self) -> None:
    #     self.__ui.file_selection_group.setEnabled(False)
    #     self.__ui.output_group.setEnabled(False)
    #     self.__ui.statistics_group.setEnabled(True)

    #     self.__ui.create_job_button.setEnabled(True)
    #     self.__ui.remove_job_button.setEnabled(True)
    #     self.__ui.save_job_button.setEnabled(True)
    #     self.__ui.run_all_jobs_button.setEnabled(True)

    #     self.__ui.job_queue_table_view.setEnabled(True)

    # # -------------------------------------------------------------------------
    # def __disableTask(self) -> None:
    #     self.__ui.create_job_button.setEnabled(False)
    #     self.__ui.remove_job_button.setEnabled(False)
    #     self.__ui.save_job_button.setEnabled(False)
    #     self.__ui.run_all_jobs_button.setEnabled(False)
    #     self.__ui.cancel_jobs_button.setEnabled(True)

    # # -------------------------------------------------------------------------
    # def __enableTask(self) -> None:
    #     self.__ui.create_job_button.setEnabled(True)
    #     self.__ui.remove_job_button.setEnabled(True)
    #     self.__ui.save_job_button.setEnabled(True)
    #     self.__ui.run_all_jobs_button.setEnabled(True)
    #     self.__ui.cancel_jobs_button.setEnabled(False)

    # # -------------------------------------------------------------------------
    # def __clearTaskProperties(self) -> None:
    #     self.__ui.source_folder_input.setText("")
    #     self.__ui.destination_folder_input.setText("")
    #     self.__ui.compression_method_combo.clear()
    #     self.__ui.compression_level_combo.clear()
    #     self.__ui.source_files_tree_view.setModel(None)

    #     checked_button = self.__formats_button_group.checkedButton()
    #     if checked_button:
    #         self.__formats_button_group.setExclusive(False)
    #         checked_button.setChecked(Fal__se)
    #         self.__formats_button_group.setExclusive(True)

    # # -------------------------------------------------------------------------
    # # CONNECT SIGNALS TO SLOTS
    # # -------------------------------------------------------------------------

    # # -------------------------------------------------------------------------
    # def __connectTaskManagement(self) -> None:
    #     self.__ui.create_job_button.clicked.connect(self.__createNewTask)
    #     self.__ui.remove_job_button.clicked.connect(self.__removeTask)
    #     self.__ui.save_job_button.clicked.connect(self.__editTask)

    # # -------------------------------------------------------------------------
    # def __connectTaskRunning(self) -> None:
    #     self.__ui.run_all_jobs_button.clicked.connect(self.__runAll)
    #     self.__ui.cancel_jobs_button.clicked.connect(self.__cancelRun)

    # # -------------------------------------------------------------------------
    # def __connectTaskProperties(self) -> None:
    #     self.__ui.check_integrity_button.clicked.connect(self.__checkIntegrity)
    #     self.__ui.source_folder_browser.clicked.connect(self.__selectSourceFolder)
    #     self.__ui.destination_folder_browser.clicked.connect(self.__selectDestinationFile)
    #     self.__formats_button_group.buttonClicked.connect(self.__updatePackerType)
    #     self.__ui.compression_method_combo.activated.connect(self.__updateCompressionLevel)

    # ###########################################################################
    # # PRIVATE SLOTS
    # ###########################################################################

    # # -------------------------------------------------------------------------
    # def __createNewSession(self) -> None:
    #     self.__session = Session()
    #     self.__updateSessionViewModel()
    #     self.__ui.remove_job_button.setEnabled(False)
    #     self.__ui.save_job_button.setEnabled(False)
    #     self.__ui.run_all_jobs_button.setEnabled(False)
    #     self.__clearTaskProperties()
    #     self.__ui.global_progress_bar.setFormat("%p%")
    #     self.__ui.job_progress_bar.setFormat("%p%")
    #     self.__progression.init()
    #     self.__setTitle()

    # # -------------------------------------------------------------------------
    # def __openSession(self, s) -> None:
    #     [filename, _] = QFileDialog.getOpenFileName(self, "Open session", "", "JSON (*.json)")
    #     if filename:
    #         with open(filename, "r") as file:
    #             self.__session = json.load(file, cls=SessionDecoder)
    #             if self.__session is not None:
    #                 self.__updateSessionViewModel()
    #                 self.__setTitle(self.__session.name())
    #                 if self.__session.nbTasks() > 0:
    #                     self.__selected_task = self.__session.taskAt(0)
    #                     self.__ui.job_queue_table_view.selectRow(0)
    #                     self.__disableTaskProperties()

    # # -------------------------------------------------------------------------
    # def __saveSession(self, s) -> None:
    #     if not self.__session.name():
    #         self.__saveSessionAs(s)
    #     else:
    #         dst_file_path = self.__session.outputFile()
    #         tmp_dst_file_path = dst_file_path + "~"

    #         try:
    #             output_file = open(tmp_dst_file_path, "w")
    #             json.dump(self.__session, output_file, cls=SessionEncoder, indent=4)
    #             output_file.close()
    #         except (IOError, shutil.SameFileError) as ex:
    #             error_msg = type(ex).__name__ + ": " + str(ex)
    #             QtCore.qCritical(error_msg)
    #         else:
    #             shutil.copy(tmp_dst_file_path, dst_file_path)
    #         finally:
    #             os.remove(tmp_dst_file_path)

    # # -------------------------------------------------------------------------
    # def __saveSessionAs(self, s) -> None:
    #     [filename, _] = QFileDialog.getSaveFileName(self, "Save As", "", "JSON (*.json)")
    #     if filename:
    #         self.__session.setName(filename)
    #         self.__setTitle(self.__session.name())
    #         dst_file_path = self.__session.outputFile()
    #         with open(dst_file_path, "w") as output_file:
    #             json.dump(self.__session, output_file, cls=SessionEncoder, indent=4)

    # # -------------------------------------------------------------------------
    # def __createNewTask(self) -> None:
    #     row_inserted = self.__session.insertRow()

    #     self.__selected_task = self.__session.taskAt(row_inserted)
    #     self.__ui.job_queue_table_view.selectRow(row_inserted)

    #     self.__enableTaskProperties()
    #     self.__updateCompressionMethod()
    #     self.__updateCompressionLevel()

    # # -------------------------------------------------------------------------
    # def __removeTask(self) -> None:
    #     model = self.__ui.job_queue_table_view.model()
    #     current_row = self.__ui.job_queue_table_view.currentIndex().row()
    #     model.removeRow(current_row)

    #     if self.__session.nbTasks() == 0:
    #         self.__ui.remove_job_button.setEnabled(False)
    #         self.__ui.save_job_button.setEnabled(False)
    #         self.__ui.run_all_jobs_button.setEnabled(False)
    #         self.__clearTaskProperties()
    #         return
    #     elif current_row > self.__session.nbTasks():
    #         current_row -= 1

    #     self.__ui.job_queue_table_view.selectRow(current_row)

    # # -------------------------------------------------------------------------
    # def __editTask(self) -> None:
    #     current_row = self.__ui.job_queue_table_view.currentIndex().row()

    #     if current_row >= 0:
    #         if self.__ui.save_job_button.text() == "Edit":
    #             self.__enableTaskProperties()
    #         else:
    #             self.__disableTaskProperties()

    # # -------------------------------------------------------------------------
    # def __checkIntegrity(self):
    #     self.__selected_task.checkIntegrity()

    #     dlg = FixWarnings(self.__selected_task.filesSelected(), self)
    #     dlg.exec()

    # # -------------------------------------------------------------------------
    # def __selectSourceFolder(self):
    #     files_model = self.__selected_task.filesSelected()
    #     selected_folder = QFileDialog.getExistingDirectory(
    #         self, "Select folder", self.__ui.source_folder_input.text(), QFileDialog.Option.ShowDirsOnly
    #     )

    #     if selected_folder:
    #         self.__ui.source_folder_input.setText(selected_folder)
    #         files_model.set_root_path(selected_folder)

    #         filtering_model = TreeViewProxyModel(selected_folder)
    #         filtering_model.setSourceModel(files_model)
    #         self.__ui.source_files_tree_view.setModel(filtering_model)

    #         parent_index = files_model.index(selected_folder).parent()
    #         proxy_parent_index = filtering_model.mapFromSource(parent_index)
    #         self.__ui.source_files_tree_view.setRootIndex(proxy_parent_index)

    # # -------------------------------------------------------------------------
    # def __selectDestinationFile(self):
    #     raw_dest_file = self.__selected_task.rawDestFile()
    #     [raw_basename, _] = QFileDialog.getSaveFileName(self, "Select file", raw_dest_file)

    #     if raw_basename:
    #         self.__selected_task.setRawDstFile(raw_basename)

    # # -------------------------------------------------------------------------
    # def __updatePackerType(self, button: QtWidgets.QAbstractButton):
    #     self.__packer_type_mapper.submit()
    #     self.__task_view_mapper.submit()

    #     self.__ui.compression_method_combo.setCurrentIndex(0)
    #     self.__ui.compression_level_combo.setCurrentIndex(0)
    #     self.__updateCompressionMethod()

    # # -------------------------------------------------------------------------
    # def __updateCompressionMethod(self):
    #     curr_index = self.__ui.compression_method_combo.currentIndex()

    #     packer_data = self.__selected_task.packerData()
    #     info = packer_data.methodsInfo()
    #     self.__ui.compression_method_combo.clear()
    #     for method in info:
    #         self.__ui.compression_method_combo.addItem(method)

    #     self.__ui.compression_method_combo.setCurrentIndex(curr_index)

    #     curr_index = self.__ui.compression_method_combo.currentIndex()

    #     self.__updateCompressionLevel()

    # # -------------------------------------------------------------------------
    # def __updateCompressionLevel(self):
    #     curr_index = self.__ui.compression_level_combo.currentIndex()
    #     c_method_curr_index = self.__ui.compression_method_combo.currentIndex()

    #     packer_data = self.__selected_task.packerData()
    #     info = packer_data.levelsInfo()
    #     self.__ui.compression_level_combo.clear()
    #     for level in info[c_method_curr_index]:
    #         self.__ui.compression_level_combo.addItem(level)

    #     if self.__ui.compression_level_combo.count() > curr_index:
    #         self.__ui.compression_level_combo.setCurrentIndex(curr_index)
    #     else:
    #         self.__ui.compression_level_combo.setCurrentIndex(0)

    # # -------------------------------------------------------------------------
    # def __mapViewWithTask(self, selected: QItemSelection, deselected: QItemSelection) -> None:
    #     selected_row = self.__ui.job_queue_table_view.currentIndex().row()
    #     self.__selected_task = self.__session.taskAt(selected_row)

    #     self.__updateTaskViewMapper()
    #     self.__updatePackerViewMapper()
    #     self.__updateFilesSelection()

    # # -------------------------------------------------------------------------
    # def __runAll(self) -> None:
    #     nb_checked_tasks = self.__session.nbCheckedTasks()

    #     if nb_checked_tasks == 0:
    #         msg = QMessageBox()
    #         msg.setIcon(QMessageBox.Icon.Warning)
    #         msg.setText("Nothing to run!")
    #         msg.setInformativeText("Please select at least one task.")
    #         msg.setWindowTitle("Warning")
    #         msg.exec()
    #     else:
    #         self.__initTasksStatus()
    #         self.__disableTask()

    #         self.__progression.init()
    #         self.__progression.setNbTask(self.__session.nbCheckedTasks())

    #         self.__ui.global_progress_bar.setFormat("%p%")
    #         self.__ui.job_progress_bar.setFormat("%p%")

    #         tasks = self.__session.tasks()

    #         for task in tasks:
    #             if task.isChecked() == Qt.CheckState.Checked.value:
    #                 packer = createPacker(task)
    #                 packer.signals.info.connect(lambda msg: QtCore.qInfo(msg))
    #                 packer.signals.error.connect(self.__progression.errorReported)
    #                 packer.signals.progress.connect(self.__progression.updateTaskProgress)
    #                 packer.signals.finish.connect(self.__progression.updateGlobalProgress)
    #                 self.__thread_pool.start(packer)
    #                 packer.signals.finish.connect(self.__runAllFinished)

    # # -------------------------------------------------------------------------
    # def __cancelRun(self) -> None:
    #     self.__thread_pool.clear()
    #     QtCore.qInfo("<b>Cancel. Waiting for the current task to finish.<b>")

    #     self.__ui.global_progress_bar.setFormat("Stopping...")
    #     self.__ui.job_progress_bar.setFormat("Stopping...")
    #     self.__is_canceled = True

    # # -------------------------------------------------------------------------
    # def __runAllFinished(self):
    #     if self.__thread_pool.activeThreadCount() == 0:
    #         if self.__is_canceled:
    #             self.__ui.global_progress_bar.setFormat("Stopped")
    #             self.__ui.job_progress_bar.setFormat("Stopped")
    #             self.__is_canceled = False

    #         self.__enableTask()

    #         report = f"<b>{self.__progression.report()}</b>"
    #         QtCore.qInfo(report)
