"""Provide a dialog to configure application settings.

This module defines a Qt dialog that allows users to modify Packy
application settings.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.models.packy_settings import (
    FilenameSuffix,
    PackySettings,
    SnapshotRetentionPolicy,
)
from packy.ui.ui_options_dialog import Ui_OptionsDialog

# Third-party
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox


###############################################################################
class OptionsDialog(QDialog):
    """A dialog for viewing and modifying Packy application settings.

    This dialog presents configurable options related to snapshot
    retention and archive naming. It initializes its UI from the provided
    settings object and updates the settings when the user applies changes.

    Attributes:
        options_changed (Signal): Emitted when settings are modified and applied.
    """

    options_changed = Signal()

    # -------------------------------------------------------------------------
    def __init__(self, app_settings: PackySettings, parent: QDialog | None = None) -> None:
        """Initialize the dialog and bind it to application settings.

        Args:
            app_settings (PackySettings): The settings instance to read from
                and write to.
            parent (QDialog | None): The parent dialog. Defaults to None.
        """
        super().__init__(parent)

        self.__ui: Ui_OptionsDialog = Ui_OptionsDialog()
        self.__ui.setupUi(self)
        self.__settings: PackySettings = app_settings

        # Widgets mapping
        self.__retention_policy_by_button: dict[QAbstractButton, SnapshotRetentionPolicy] = {
            self.__ui.retention_keep_all_radio: SnapshotRetentionPolicy.KEEP_ALL,
            self.__ui.retention_keep_last_n_radio: SnapshotRetentionPolicy.KEEP_LAST_N,
        }

        self.__filename_suffix_by_button: dict[QAbstractButton, FilenameSuffix] = {
            self.__ui.archive_naming_add_date_radio: FilenameSuffix.CURRENT_DATE,
            self.__ui.archive_naming_add_version_radio: FilenameSuffix.VERSION_NUMBER,
            self.__ui.archive_naming_no_suffix_radio: FilenameSuffix.NONE,
        }

        self.__read_general_page_settings()
        self.__read_task_page_settings()
        self.__update_ui_state()
        self.__setup_connections()

    # --------------------------------------------------------------------------
    def __read_general_page_settings(self) -> None:
        snapshot_retention_policy = self.__settings.snapshot_retention_policy()
        for radio_btn, policy in self.__retention_policy_by_button.items():
            if policy == snapshot_retention_policy:
                radio_btn.setChecked(True)
                break

        self.__ui.retention_count_spin.setValue(self.__settings.snapshots_retention_count())

    # --------------------------------------------------------------------------
    def __read_task_page_settings(self) -> None:
        archive_filename_suffix = self.__settings.archive_filename_suffix()
        for radio_btn, suffix in self.__filename_suffix_by_button.items():
            if suffix == archive_filename_suffix:
                radio_btn.setChecked(True)
                break

    # --------------------------------------------------------------------------
    def __setup_connections(self) -> None:
        self.__ui.retention_policy_button_group.buttonClicked.connect(self.__update_ui_state)
        self.__ui.dialog_button_box.accepted.connect(self.__on_accept)
        self.__ui.dialog_button_box.rejected.connect(self.__on_cancel)
        self.__ui.dialog_button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.__on_apply,
        )

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __update_ui_state(self) -> None:
        is_keep_last_policy = self.__ui.retention_keep_last_n_radio.isChecked()
        self.__ui.retention_count_spin.setEnabled(is_keep_last_policy)

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __on_accept(self) -> None:
        self.__on_apply()
        super().accept()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __on_cancel(self) -> None:
        super().reject()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __on_apply(self) -> None:
        self.__write_settings()
        self.options_changed.emit()

    # -------------------------------------------------------------------------
    def __write_settings(self) -> None:
        selected_retention_btn = self.__ui.retention_policy_button_group.checkedButton()
        if selected_retention_btn is not None:
            self.__settings.set_snapshot_retention_policy(
                self.__retention_policy_by_button[selected_retention_btn],
            )

        self.__settings.set_snapshots_retention_count(self.__ui.retention_count_spin.value())

        selected_filename_suffix_btn = self.__ui.archive_naming_button_group.checkedButton()
        if selected_filename_suffix_btn is not None:
            self.__settings.set_archive_filename_suffix(
                self.__filename_suffix_by_button[selected_filename_suffix_btn],
            )
