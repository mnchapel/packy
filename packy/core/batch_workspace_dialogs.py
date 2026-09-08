"""Provide dialogs and save decisions for the batch workspace.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.constants.file_filters import FileFilter

# Third-party
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

# Standard library
from enum import IntEnum, auto, unique
from pathlib import Path
from typing import final


###############################################################################
@unique
class SaveDecision(IntEnum):
    """Represent the user's choice for unsaved batch modifications."""

    SAVE = auto()
    DISCARD = auto()
    CANCEL = auto()


###############################################################################
@final
class BatchWorkspaceDialogs:
    """Provide user interactions required by the batch workspace."""

    # -------------------------------------------------------------------------
    def __init__(self, parent: QWidget) -> None:
        """Initialize the batch workspace dialogs.

        Args:
            parent (QWidget): Parent widget of the dialogs.
        """
        self._parent = parent

    # -------------------------------------------------------------------------
    @staticmethod
    def _tr(text: str) -> str:
        """Translate text in the batch workspace dialog context.

        Args:
            text (str): Source text to translate.

        Returns:
            str: The translated text.
        """
        return QCoreApplication.translate("BatchWorkspaceDialogs", text)

    # -------------------------------------------------------------------------
    def _batch_file_filter(self) -> str:
        """Return the translated Batch file filter used by batch file dialogs.

        Returns:
            str: The batch-specific filter.
        """
        return self._tr(FileFilter.BATCH_FILE)

    # -------------------------------------------------------------------------
    def _files_filter(self) -> str:
        """Return the translated all files filter used by batch file dialogs.

        Returns:
            str: The all files filter.
        """
        return f"{self._tr(FileFilter.ALL_FILES)};;{self._batch_file_filter()}"

    # -------------------------------------------------------------------------
    def choose_new_batch_path(self, default_file_path: Path) -> Path | None:
        """Prompt the user to select a resolved path for a new batch.

        Args:
            default_file_path (Path): Initial file path displayed by the save dialog.

        Returns:
            Path | None: The resolved selected path, or ``None`` if the dialog is
              canceled.
        """
        [selected_file_path, _selected_filter] = QFileDialog.getSaveFileName(
            self._parent,
            self._tr("New Batch"),
            str(default_file_path),
            self._files_filter(),
            self._batch_file_filter(),
        )
        if selected_file_path == "":
            return None

        return Path(selected_file_path).resolve()

    # -------------------------------------------------------------------------
    def choose_open_batch_path(self, default_file_path: Path) -> Path | None:
        """Prompt the user to select a resolved batch file to open.

        Args:
            default_file_path (Path): Initial path displayed by the open dialog.

        Returns:
            Path | None: The resolved selected path, or ``None`` if the dialog is
              canceled.
        """
        [selected_file_path, _selected_filter] = QFileDialog.getOpenFileName(
            self._parent,
            self._tr("Open Batch"),
            str(default_file_path),
            self._files_filter(),
            self._batch_file_filter(),
        )
        if selected_file_path == "":
            return None

        return Path(selected_file_path).resolve()

    # -------------------------------------------------------------------------
    def choose_save_batch_path(self, default_file_path: Path) -> Path | None:
        """Prompt the user to select a resolved destination for the active batch.

        When the selected path does not end with ``.json``, ask the user to confirm
        the extension mismatch. If confirmation is declined, reopen the save dialog.

        Args:
            default_file_path (Path): Initial file path displayed by the save dialog.

        Returns:
            Path | None: The resolved selected path, or ``None`` if the dialog is
              canceled.
        """
        while True:
            [selected_file_path, _selected_filter] = QFileDialog.getSaveFileName(
                self._parent,
                self._tr("Save Batch As"),
                str(default_file_path),
                self._files_filter(),
                self._batch_file_filter(),
            )
            if selected_file_path != "" and not selected_file_path.endswith(".json"):
                message_box: QMessageBox = QMessageBox(
                    QMessageBox.Icon.Warning,
                    self._tr("Extension Mismatch"),
                    self._tr("The file extension does not match the chosen file type."),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    self._parent,
                )
                message_box.setInformativeText(
                    self._tr(
                        "PackY may not automatically recognize this file when loading it. "
                        "Are you sure you want to save with this extension?",
                    ),
                )
                answer: int = message_box.exec()
                if answer != QMessageBox.StandardButton.Yes:
                    continue

            if selected_file_path == "":
                return None

            return Path(selected_file_path).resolve()

    # -------------------------------------------------------------------------
    def confirm_unsaved_changes(self) -> SaveDecision:
        """Ask how unsaved batch modifications should be handled.

        Returns:
            SaveDecision: The user's choice.
        """
        response: QMessageBox.StandardButton = QMessageBox.warning(
            self._parent,
            self._tr("Unsaved Changes"),
            self._tr("There are unsaved changes. Do you want to save now?"),
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )

        match response:
            case QMessageBox.StandardButton.Save:
                return SaveDecision.SAVE
            case QMessageBox.StandardButton.Discard:
                return SaveDecision.DISCARD
            case QMessageBox.StandardButton.Cancel | _:
                return SaveDecision.CANCEL

    # -------------------------------------------------------------------------
    def show_save_error(self, file_path: Path, error: str) -> None:
        """Inform the user that a batch could not be saved.

        Args:
            file_path (Path): Path of the batch that could not be saved.
            error (str): Error message describing the save failure.
        """
        QMessageBox.critical(
            self._parent,
            self._tr("Error Saving Batch"),
            self._tr(
                "An error occurred while saving the batch '{0}':\n{1}",
            ).format(file_path, error),
        )

    # -------------------------------------------------------------------------
    def show_open_error(self, file_path: Path, error: str) -> None:
        """Inform the user that a batch could not be opened.

        Args:
            file_path (Path): Path of the batch that could not be opened.
            error (str): Error message describing the open failure.
        """
        QMessageBox.critical(
            self._parent,
            self._tr("Error Opening Batch"),
            self._tr(
                "Error to open '{0}':\n{1}",
            ).format(file_path, error),
        )

    # -------------------------------------------------------------------------
    def show_open_last_success(self, batch_display_name: str) -> None:
        """Inform the user that the last batch has been opened.

        Args:
            batch_display_name (str): Display name of the batch that was opened.
        """
        QMessageBox.information(
            self._parent,
            self._tr("Batch Opened"),
            self._tr(
                "Last batch '{0}' opened.",
            ).format(batch_display_name),
        )

    # -------------------------------------------------------------------------
    def show_open_last_error(self, batch_display_name: str, error: str) -> None:
        """Inform the user that the last batch could not be opened.

        Args:
            batch_display_name (str): Display name of the batch that could not
              be opened.
            error (str): Error message describing the restoration failure.
        """
        QMessageBox.warning(
            self._parent,
            self._tr("Error Opening Batch"),
            self._tr(
                "Cannot open the last batch '{0}':\n{1}",
            ).format(batch_display_name, error),
        )
