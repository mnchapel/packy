"""Manage batch files for the application workspace.

Provide ``BatchWorkspace``, which creates, opens, saves, activates, and
closes batches and maintains the recent-batch history.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.constants.settings_keys import WorkspaceSettings
from packy.core.batch import Batch
from packy.core.batch_workspace_dialogs import BatchWorkspaceDialogs, SaveDecision
from packy.core.batch_workspace_history import BatchWorkspaceHistory
from packy.core.configurable import Configurable
from packy.core.user_settings import UserSettings

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import QObject, QStandardPaths, Signal

# Standard library
from pathlib import Path
from typing import TYPE_CHECKING, final, override

if TYPE_CHECKING:
    # Third-party
    from PySide6.QtWidgets import QWidget


###############################################################################
class FinalMeta(type(QObject), type(Configurable)):  # pyright: ignore[reportGeneralTypeIssues]  # noqa: D101
    pass


###############################################################################
@final
class BatchWorkspace(QObject, Configurable, metaclass=FinalMeta):
    """Coordinate batch files and the active batch for a workspace.

    The workspace tracks recently opened batch paths and manages the Qt lifecycle
    of the active batch.

    Signals:
        recent_batches_changed (list): Emitted with the current recent batch paths
          when the history is loaded or updated.
        batch_opened (Batch): Emitted after a batch becomes active, with the new
          batch.
        batch_saved: Emitted after the active batch is saved successfully.
        batch_closed (Batch): Emitted after the active batch is cleared, with the
          previous batch.
    """

    # -------------------------------------------------------------------------
    recent_batches_changed = Signal(list, arguments=["recent_batch_paths"])
    batch_opened = Signal(Batch, arguments=["new_batch"])
    batch_saved = Signal()
    batch_closed = Signal(Batch, arguments=["old_batch"])

    # -------------------------------------------------------------------------
    def __init__(self, max_recent_batches: int, parent: QWidget) -> None:
        """Initialize the batch workspace.

        Args:
            max_recent_batches (int): Maximum number of paths retained when updating
              the recent batch history.
            parent (QWidget): Parent widget of the workspace.
        """
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)

        self._dialogs = BatchWorkspaceDialogs(parent)
        self._recent_history = BatchWorkspaceHistory(max_recent_batches, UserSettings(), self)
        self._current_batch: Batch | None = None

        self._recent_history.recent_batches_changed.connect(self.recent_batches_changed)

        QtCore.qDebug(f"{self.__class__.__name__} initialized.")

    # -------------------------------------------------------------------------
    @override
    def load_settings(self, settings: UserSettings) -> None:
        QtCore.qDebug(
            f"Loading {self.objectName()} settings from {WorkspaceSettings.SETTINGS_GROUP}.",
        )
        self._recent_history.load_from_settings(settings)

    # -------------------------------------------------------------------------
    @override
    def save_settings(self, settings: UserSettings) -> None:
        QtCore.qDebug(
            f"Saving {self.objectName()} settings in {WorkspaceSettings.SETTINGS_GROUP}.",
        )
        self._recent_history.save_to_settings(settings)

    # -------------------------------------------------------------------------
    def create_batch(self) -> Batch | None:
        """Create and save a new batch selected by the user.

        The save dialog starts in the default batch location. A ``.json`` suffix is
        added when the selected path does not already end with one.

        Returns:
            Batch | None: The saved batch, or ``None`` if creation is canceled or the
              initial save fails.
        """
        QtCore.qDebug("Creating a new batch.")
        suggested_file_path: Path = self._default_batch_location() / self.tr(
            Batch.default_filename(),
        )
        selected_file_path: Path | None = self._dialogs.choose_new_batch_path(suggested_file_path)
        if selected_file_path is None:
            QtCore.qDebug("Creation canceled.")
            return None
        if not selected_file_path.name.endswith(".json"):
            selected_file_path = selected_file_path.with_name(
                f"{selected_file_path.name.rstrip('.')}.json",
            )

        batch: Batch = Batch(selected_file_path)
        [saved, error] = batch.save()
        if not saved:
            QtCore.qWarning(f"Failed to save new batch '{selected_file_path}': {error}")
            self._dialogs.show_save_error(selected_file_path, error)
            return None

        QtCore.qDebug(f"New batch created: '{selected_file_path}'.")
        return batch

    # -------------------------------------------------------------------------
    def _default_batch_location(self) -> Path:
        """Return the default directory for batch file dialogs.

        Returns:
            Path: The directory of the most recently opened batch, or the system
              documents directory when no recent batch is available.
        """
        # Try to first return the latest batch directory
        path: Path | None = self._recent_history.latest_opened
        if path is not None:
            return path.parent

        # Or return the OS document directory: "~/Documents" for macOS,
        # "C:/Users/<USER>/Documents" for Windows "~/Documents" for Linux.
        dir_path_str = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation,
        )
        return Path(dir_path_str)

    # -------------------------------------------------------------------------
    def open_last_batch(self) -> bool:
        """Open the most recently opened batch.

        Returns:
            bool: ``True`` if the batch is already open or becomes active; ``False``
              if no recent batch exists, loading fails, or activation is canceled.
        """
        QtCore.qDebug("Opening last batch.")
        batch_file: Path | None = self._recent_history.latest_opened
        if batch_file is None:
            QtCore.qDebug("No recent batch to open.")
            return False

        [opened, error] = self._open_batch_file(batch_file)
        if not opened and error != "":
            QtCore.qWarning(f"Failed to open the last batch: '{batch_file}'.")
            self._dialogs.show_open_last_error(batch_file.name, error)
        else:
            QtCore.qDebug(f"Last batch opened: '{batch_file}'.")
            self._dialogs.show_open_last_success(batch_file.name)
        return opened

    # -------------------------------------------------------------------------
    def open_recent_batch(self, recent_batch: Path) -> bool:
        """Open a batch from the recent batch history.

        Args:
            recent_batch (Path): Recent batch path to open.

        Returns:
            bool: ``True`` if the requested batch is already open or becomes active;
              ``False`` if the path is not in the recent history, loading fails, or
              activation is canceled.
        """
        QtCore.qDebug("Opening a recent batch.")
        if recent_batch not in self._recent_history.recently_opened:
            QtCore.qDebug(f"No recent batch '{recent_batch}' found in the history.")
            return False

        [opened, _] = self._open_batch_file(recent_batch)
        if opened:
            QtCore.qDebug(f"Recent batch opened: '{recent_batch}'.")
        else:
            QtCore.qWarning(f"Failed to open the recent batch: '{recent_batch}'.")

        return opened

    # -------------------------------------------------------------------------
    def open_batch(self) -> bool:
        """Prompt the user to select and open a batch file.

        Returns:
            bool: ``True`` if the selected batch is already open or becomes active;
              ``False`` if selection is canceled, loading fails, or activation is
              canceled.
        """
        QtCore.qDebug("Opening batch.")
        suggested_file_path: Path = self._default_batch_location()
        selected_file_path: Path | None = self._dialogs.choose_open_batch_path(suggested_file_path)
        if selected_file_path is None:
            QtCore.qDebug("Opening canceled.")
            return False

        [opened, error] = self._open_batch_file(selected_file_path)
        if not opened and error != "":
            QtCore.qWarning(f"Failed to open the batch: {Path(selected_file_path).resolve()}.")
            self._dialogs.show_open_error(selected_file_path, error)
        return opened

    # -------------------------------------------------------------------------
    def _open_batch_file(self, batch_file: Path) -> tuple[bool, str]:
        """Load a batch file and activate it in the workspace.

        If the resolved path identifies the current batch, the method succeeds
        without loading it again.

        Args:
            batch_file (Path): Path of the batch file to open.

        Returns:
            tuple[bool, str]: A success flag and an error message. A false success
              flag can have an empty message when activation is canceled; load
              failures return the loader's error message.
        """
        batch_file_path: Path = Path(batch_file).resolve()
        QtCore.qDebug(f"Opening batch file in the workspace: '{batch_file_path}'.")

        if self.current_batch is not None and self.current_batch.file_path == batch_file_path:
            QtCore.qDebug("Batch file is already open.")
            return (True, "")

        QtCore.qDebug("Loading the batch file.")
        [batch, error] = Batch.load(batch_file_path)
        if batch is None:
            QtCore.qWarning(f"Failed to load batch file: {error}")
            return (False, error)

        if not self.activate_batch(batch):
            QtCore.qDebug("Opening the batch file was canceled.")
            return (False, "")

        QtCore.qDebug("Batch opened.")
        return (True, "")

    # -------------------------------------------------------------------------
    @property
    def batch_history(self) -> tuple[Path, ...]:
        """The recent batch paths, ordered from most to least recently opened."""
        return self._recent_history.recently_opened

    # -------------------------------------------------------------------------
    @property
    def current_batch(self) -> Batch | None:
        """The active batch, or ``None`` when no batch is open."""
        return self._current_batch

    # -------------------------------------------------------------------------
    def has_current_batch(self) -> bool:
        """Return whether the workspace has an active batch.

        Returns:
            bool: ``True`` when a batch is active; otherwise, ``False``.
        """
        return self._current_batch is not None

    # -------------------------------------------------------------------------
    def activate_batch(self, batch: Batch) -> bool:
        """Make a batch active and take responsibility for its Qt lifecycle.

        The current batch is closed before the new batch is installed. If closing is
        canceled or fails, activation stops and the existing batch remains active.

        After activation, the workspace becomes the batch's Qt parent, emits
        :attr:`batch_opened`, and adds the batch file path to the recent history.
        Closing the batch later detaches it from the workspace and schedules it for
        deletion.

        Args:
            batch (Batch): Batch to make active.

        Returns:
            bool: ``True`` when the batch becomes active; ``False`` when it is already
              active or the current batch cannot be closed.
        """
        QtCore.qDebug("Activating batch in the workspace.")
        if self._current_batch == batch:
            QtCore.qDebug("Batch is already active.")
            return False

        if self._current_batch is None:
            QtCore.qDebug("No current batch to close.")
        elif not self.close_current_batch():
            return False
        assert self._current_batch is None

        # self.__tasks_model.set # TODO use the model like in ProjectManager::setProject()

        self._current_batch = batch
        self._current_batch.setParent(self)

        self.batch_opened.emit(self._current_batch)
        QtCore.qDebug("Batch activated.")

        self._recent_history.add_recently_opened(self._current_batch.file_path)
        return True

    # -------------------------------------------------------------------------
    def save_current_batch(self) -> bool:
        """Save the active batch to its current file.

        A successful save emits :attr:`batch_saved`. A save failure displays an error
        message to the user.

        Returns:
            bool: ``True`` if the active batch is saved successfully; ``False`` if no
              batch is active or saving fails.
        """
        QtCore.qDebug("Saving current batch.")
        if self._current_batch is None:
            QtCore.qDebug("No current batch to save.")
            return False

        [saved, error] = self._current_batch.save()
        if not saved:
            QtCore.qWarning(
                f"Failed to save batch file '{self._current_batch.file_path}': {error}",
            )
            self._dialogs.show_save_error(self._current_batch.file_path, error)
            return False

        self.batch_saved.emit()
        return True

    # -------------------------------------------------------------------------
    def save_current_batch_as(self) -> bool:
        """Prompt for a destination and save the active batch there.

        If the selected filename does not end with ``.json``, the user must confirm
        the extension mismatch before saving proceeds. A successful save emits
        :attr:`batch_saved`.

        Returns:
            bool: ``True`` if the active batch is saved successfully; ``False`` if no
              batch is active, selection is canceled, or saving fails.
        """
        QtCore.qDebug("Saving the current batch as a new file.")
        if self._current_batch is None:
            QtCore.qDebug("No current batch to save.")
            return False

        suggested_file_path: Path = self._default_batch_location() / self.tr(
            Batch.default_filename(),
        )
        selected_file_path: Path | None = self._dialogs.choose_save_batch_path(suggested_file_path)
        if selected_file_path is None:
            QtCore.qDebug("Saving canceled.")
            return False

        [saved, error] = self._current_batch.save(selected_file_path)
        if not saved:
            QtCore.qWarning(f"Failed to save batch file '{selected_file_path}': {error}")
            self._dialogs.show_save_error(selected_file_path, error)
            return False

        self.batch_saved.emit()
        return True

    # -------------------------------------------------------------------------
    def close_current_batch(self) -> bool:
        """Close the active batch.

        If the batch has unsaved changes, the user can save, discard, or cancel. A
        successful close clears the active batch, emits :attr:`batch_closed`, and
        schedules the former batch for deletion.

        Returns:
            bool: ``True`` if no batch is active or the active batch is closed;
              ``False`` if closing is canceled or a requested save fails.
        """
        QtCore.qDebug("Closing the current batch.")
        if self._current_batch is None:
            QtCore.qDebug("No open batch to close.")
            return True

        if not self._request_save_batch_modifications():
            QtCore.qDebug("Closing canceled.")
            return False

        self._current_batch.disconnect(self)

        old_batch = self._current_batch
        self._current_batch = None

        self.batch_closed.emit(old_batch)
        old_batch.setParent(None)
        old_batch.deleteLater()
        QtCore.qDebug("Batch closed.")
        return True

    # -------------------------------------------------------------------------
    def _request_save_batch_modifications(self) -> bool:
        """Resolve unsaved changes before closing the active batch.

        If the active batch has modifications, prompt the user to save, discard, or
        cancel. Choosing save delegates to :meth:`save_current_batch`.

        Returns:
            bool: ``True`` if closing may continue; ``False`` if the user cancels or
              saving the modified batch fails.
        """
        if self.current_batch is None or not self.current_batch.is_modified:
            return True

        response: SaveDecision = self._dialogs.confirm_unsaved_changes()
        match response:
            case SaveDecision.SAVE:
                return self.save_current_batch()
            case SaveDecision.DISCARD:
                return True
            case SaveDecision.CANCEL:
                return False

    # # -------------------------------------------------------------------------
    # def add_task(self) -> str:
    #     task: str = "Task"
    #     # self.__tasks_model.add_task()
    #     return task

    # # -------------------------------------------------------------------------
    # @Slot(str, result=None)
    # def on_task_added(self, task: str) -> None:
    #     # self.task_added.emit(task)
    #     # TODO voir MapDocument::onLayerAdded
    #     pass

    # # -------------------------------------------------------------------------
    # def remove_task(self) -> None:
    #     pass

    # # -------------------------------------------------------------------------
    # @Slot(str, result=None)
    # def on_task_removed(self, task: str) -> None:
    #     # self.task_removed.emit(task)
    #     pass
