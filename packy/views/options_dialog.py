"""Provide a dialog to configure application settings.

This module defines a Qt dialog that allows users to modify Packy
application settings.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.isettings_persistable import ISettingsPersistable
from packy.ui.ui_options_dialog import Ui_OptionsDialog

# Third-party
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QWidget

# Standard library
from enum import StrEnum
from typing import TYPE_CHECKING, final, override

if TYPE_CHECKING:
    # Local application
    from packy.core.settings import Settings


###############################################################################
class SettingsKeys:
    """Define available settings keys."""

    GEOMETRY = "Geometry"
    STATE = "State"
    RETENTION_POLICY = "Snapshot/Retention/Policy"
    RETENTION_COUNT = "Snapshot/Retention/Count"
    ARCHIVE_FILENAME_SUFFIX = "Task/Archive/FilenameSuffix"


###############################################################################
class SnapshotRetentionPolicy(StrEnum):
    """Define available snapshot retention strategies."""

    KEEP_ALL = "KeepAll"
    KEEP_LAST_N = "KeepLastN"


###############################################################################
class FilenameSuffix(StrEnum):
    """Define available filename suffix strategies for archives."""

    CURRENT_DATE = "CurrentDate"
    VERSION_NUMBER = "VersionNumber"
    NONE = "None"


###############################################################################
class FinalMeta(type(QDialog), type(ISettingsPersistable)):  # pyright: ignore[reportGeneralTypeIssues]  # noqa: D101
    pass


###############################################################################
@final
class OptionsDialog(QDialog, ISettingsPersistable, metaclass=FinalMeta):
    """A dialog for viewing and modifying Packy application settings.

    This dialog presents configurable options related to snapshot
    retention and archive naming. It initializes its UI from the provided
    settings object and updates the settings when the user applies changes.

    Args:
        QDialog (_type_): _description_
        ISettingsPersistable (_type_): _description_
        metaclass (_type_, optional): _description_. Defaults to FinalMeta.

    Attributes:
        options_changed (Signal): Emitted when settings are modified and applied.
        snapshot_retention_policy_changed (Signal): Emitted when the
            snapshot retention policy changes. Arguments:
            (SnapshotRetentionPolicy).
        snapshot_retention_count_changed (Signal): Emitted when the
            snapshot retention count changes. Arguments: (int).
        archive_filename_suffix_changed (Signal): Emitted when the
            archive filename suffix changes. Arguments:
            (FilenameSuffix).
    """

    options_changed = Signal()
    snapshot_retention_policy_changed = Signal(SnapshotRetentionPolicy)
    snapshot_retention_count_changed = Signal(int)
    archive_filename_suffix_changed = Signal(FilenameSuffix)

    # -------------------------------------------------------------------------
    def __init__(self, app_settings: Settings, parent: QWidget | None = None) -> None:
        """Initialize the dialog and bind it to application settings.

        Args:
            app_settings (PackySettings): The settings instance to read from
                and write to.
            parent (QWidget | None): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        self.__ui: Ui_OptionsDialog = Ui_OptionsDialog()
        self.__ui.setupUi(self)
        self.__settings: Settings = app_settings

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

        self.read_settings(self.__settings)
        self.__setup_connections()

    # -------------------------------------------------------------------------
    @override
    def read_settings(self, settings: Settings) -> None:
        if settings != self.__settings:
            raise ValueError(  # noqa: TRY003
                "The parameter settings must be the same instance as the dialog's"
                "settings because the instance variable is the model of this view.",
            )
        self.__read_general_page_settings()
        self.__read_task_page_settings()
        self.__reset_apply_button()

    # -------------------------------------------------------------------------
    def __read_general_page_settings(self) -> None:
        snapshot_retention_policy = self.__settings.value(
            SettingsKeys.RETENTION_POLICY,
            SnapshotRetentionPolicy.KEEP_ALL.value,
        )
        for radio_btn, policy in self.__retention_policy_by_button.items():
            if policy == snapshot_retention_policy:
                radio_btn.setChecked(True)
                break

        self.__ui.retention_count_spin.setEnabled(self.__ui.retention_keep_last_n_radio.isChecked())
        snapshots_retention_count = self.__settings.value(SettingsKeys.RETENTION_COUNT, 1)
        self.__ui.retention_count_spin.setValue(snapshots_retention_count)

    # -------------------------------------------------------------------------
    def __read_task_page_settings(self) -> None:
        archive_filename_suffix = self.__settings.value(
            SettingsKeys.ARCHIVE_FILENAME_SUFFIX,
            FilenameSuffix.NONE.value,
        )
        for radio_btn, suffix in self.__filename_suffix_by_button.items():
            if suffix == archive_filename_suffix:
                radio_btn.setChecked(True)
                break

    # -------------------------------------------------------------------------
    def __setup_connections(self) -> None:
        self.__ui.retention_policy_button_group.buttonClicked.connect(self.__on_state_changed)
        self.__ui.archive_naming_button_group.buttonClicked.connect(self.__on_state_changed)
        self.__ui.retention_count_spin.valueChanged.connect(self.__on_state_changed)
        self.__ui.retention_keep_last_n_radio.toggled.connect(
            self.__ui.retention_count_spin.setEnabled,
        )
        self.__ui.dialog_button_box.accepted.connect(self.__on_accept)
        self.__ui.dialog_button_box.rejected.connect(self.__on_cancel)
        self.__ui.dialog_button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.__on_apply,
        )

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def __on_state_changed(self) -> None:
        apply_btn = self.__ui.dialog_button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.setEnabled(True)

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
        self.write_settings(self.__settings)
        self.__reset_apply_button()
        self.options_changed.emit()

    # -------------------------------------------------------------------------
    def __reset_apply_button(self) -> None:
        apply_btn = self.__ui.dialog_button_box.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.setEnabled(False)

    # -------------------------------------------------------------------------
    @override
    def write_settings(self, settings: Settings) -> None:
        if settings != self.__settings:
            raise ValueError(  # noqa: TRY003
                "The parameter settings must be the same instance as the dialog's"
                "settings because the instance variable is the model of this view.",
            )
        policy_selection_btn = self.__ui.retention_policy_button_group.checkedButton()
        if policy_selection_btn is not None:
            policy = self.__retention_policy_by_button[policy_selection_btn].value
            self.__settings.set_value(
                SettingsKeys.RETENTION_POLICY,
                policy,
                self.snapshot_retention_policy_changed.emit,
            )

        retention_count = self.__ui.retention_count_spin.value()
        self.__settings.set_value(
            SettingsKeys.RETENTION_COUNT,
            retention_count,
            self.snapshot_retention_count_changed.emit,
        )

        filename_suffix_selection_btn = self.__ui.archive_naming_button_group.checkedButton()
        if filename_suffix_selection_btn is not None:
            suffix = self.__filename_suffix_by_button[filename_suffix_selection_btn].value
            self.__settings.set_value(
                SettingsKeys.ARCHIVE_FILENAME_SUFFIX,
                suffix,
                self.archive_filename_suffix_changed.emit,
            )
