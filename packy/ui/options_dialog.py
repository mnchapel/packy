"""Provide the application options dialog and its setting types.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.configurable import Configurable
from packy.core.user_settings import UserSettings
from packy.ui.ui_options_dialog import Ui_OptionsDialog

# Third-party
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QPushButton, QWidget

# Standard library
from enum import StrEnum
from typing import final, override


###############################################################################
class SettingsKeys:
    """Define keys used to persist application options."""

    GEOMETRY = "Geometry"
    STATE = "State"
    RETENTION_POLICY = "Snapshot/Retention/Policy"
    RETENTION_COUNT = "Snapshot/Retention/Count"
    ARCHIVE_FILENAME_SUFFIX = "Task/Archive/FilenameSuffix"


###############################################################################
class SnapshotRetentionPolicy(StrEnum):
    """Represent the available snapshot retention policies."""

    KEEP_ALL = "KeepAll"
    KEEP_LAST_N = "KeepLastN"


###############################################################################
class FilenameSuffix(StrEnum):
    """Represent the available archive filename suffix options."""

    CURRENT_DATE = "CurrentDate"
    VERSION_NUMBER = "VersionNumber"
    NONE = "None"


###############################################################################
class FinalMeta(type(QDialog), type(Configurable)):  # pyright: ignore[reportGeneralTypeIssues]  # noqa: D101
    pass


###############################################################################
@final
class OptionsDialog(QDialog, Configurable, metaclass=FinalMeta):
    """Provide controls for editing and applying application options.

    Signals:
        options_changed: Emitted after the current options are applied.
        snapshot_retention_policy_changed (SnapshotRetentionPolicy): Carries a
          changed snapshot retention policy.
        snapshot_retention_count_changed (int): Carries a changed snapshot
          retention count.
        archive_filename_suffix_changed (FilenameSuffix): Carries a changed archive
          filename suffix option.
    """

    # -------------------------------------------------------------------------
    options_changed = Signal()
    snapshot_retention_policy_changed = Signal(SnapshotRetentionPolicy)
    snapshot_retention_count_changed = Signal(int)
    archive_filename_suffix_changed = Signal(FilenameSuffix)

    # -------------------------------------------------------------------------
    def __init__(self, settings: UserSettings, parent: QWidget | None = None) -> None:
        """Initialize the options dialog and its user interface.

        Args:
            settings (UserSettings): Settings object used to load and save options.
            parent (QWidget | None): Parent widget for the dialog.
        """
        super().__init__(parent)

        self._ui = Ui_OptionsDialog()
        self._ui.setupUi(self)
        self._settings: UserSettings = settings
        self._apply_button: QPushButton = self._ui.options_button_box.button(
            QDialogButtonBox.StandardButton.Apply,
        )

        # Widgets mapping
        self._retention_policy_by_button: dict[QAbstractButton, SnapshotRetentionPolicy] = {
            self._ui.keep_all_radio: SnapshotRetentionPolicy.KEEP_ALL,
            self._ui.keep_latest_radio: SnapshotRetentionPolicy.KEEP_LAST_N,
        }

        self._filename_suffix_by_button: dict[QAbstractButton, FilenameSuffix] = {
            self._ui.add_date_radio: FilenameSuffix.CURRENT_DATE,
            self._ui.add_version_radio: FilenameSuffix.VERSION_NUMBER,
            self._ui.no_suffix_radio: FilenameSuffix.NONE,
        }

        self._setup_connections()

    # -------------------------------------------------------------------------
    def _setup_connections(self) -> None:
        """Connect the option controls and dialog buttons to their handlers."""
        self._ui.retention_policy_button_group.buttonClicked.connect(
            self._enable_apply_button,
        )
        self._ui.archive_naming_button_group.buttonClicked.connect(
            self._enable_apply_button,
        )
        self._ui.keep_latest_spin.valueChanged.connect(
            self._enable_apply_button,
        )
        self._ui.keep_latest_radio.toggled.connect(
            self._ui.keep_latest_spin.setEnabled,
        )

        self._ui.options_button_box.accepted.connect(self._on_accept)
        self._ui.options_button_box.rejected.connect(self._on_cancel)
        self._apply_button.clicked.connect(self._on_apply)

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _enable_apply_button(self) -> None:
        """Enable the Apply button."""
        self._set_apply_button_enabled(enabled=True)

    # -------------------------------------------------------------------------
    def _set_apply_button_enabled(self, enabled: bool) -> None:  # noqa: FBT001
        """Set whether the Apply button is enabled.

        Args:
            enabled (bool): Whether the Apply button is enabled.
        """
        self._apply_button.setEnabled(enabled)

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _on_accept(self) -> None:
        """Accept the dialog and apply the current options."""
        self._on_apply()
        super().accept()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _on_cancel(self) -> None:
        """Reject the dialog."""
        super().reject()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _on_apply(self) -> None:
        """Save the current options and emit the options change notification."""
        self.save_settings(self._settings)
        self._set_apply_button_enabled(enabled=False)
        self.options_changed.emit()

    # -------------------------------------------------------------------------
    @Slot(UserSettings, result=None)
    @override
    def load_settings(self, settings: UserSettings) -> None:
        self._load_general_page_settings(settings)
        self._load_task_page_settings(settings)
        self._set_apply_button_enabled(enabled=False)

    # -------------------------------------------------------------------------
    def _load_general_page_settings(self, settings: UserSettings) -> None:
        """Load snapshot retention settings into the general options page.

        Args:
            settings (UserSettings): Settings object from which to load the values.
        """
        snapshot_retention_policy = settings.value(
            SettingsKeys.RETENTION_POLICY,
            SnapshotRetentionPolicy.KEEP_ALL,
        )
        self._select_button_for_value(
            self._retention_policy_by_button,
            snapshot_retention_policy,
        )

        self._ui.keep_latest_spin.setEnabled(
            self._ui.keep_latest_radio.isChecked(),
        )
        snapshots_retention_count = settings.value(SettingsKeys.RETENTION_COUNT, 1)
        self._ui.keep_latest_spin.setValue(snapshots_retention_count)

    # -------------------------------------------------------------------------
    def _load_task_page_settings(self, settings: UserSettings) -> None:
        """Load archive naming settings into the task options page.

        Args:
            settings (UserSettings): Settings object from which to load the values.
        """
        archive_filename_suffix = settings.value(
            SettingsKeys.ARCHIVE_FILENAME_SUFFIX,
            FilenameSuffix.NONE,
        )
        self._select_button_for_value(
            self._filename_suffix_by_button,
            archive_filename_suffix,
        )

    # -------------------------------------------------------------------------
    @staticmethod
    def _select_button_for_value[T: StrEnum](
        mapping: dict[QAbstractButton, T],
        value: T,
    ) -> None:
        """Select the button mapped to a value when one exists.

        Args:
            mapping (dict[QAbstractButton, T]): Buttons and their mapped
              values.
            value (T): Value whose mapped button to select.
        """
        for button, mapped_value in mapping.items():
            if mapped_value == value:
                button.setChecked(True)
                return

    # -------------------------------------------------------------------------
    @Slot(UserSettings, result=None)
    @override
    def save_settings(self, settings: UserSettings) -> None:
        """Save the current option selections.

        Args:
            settings (UserSettings): Settings object in which to store the values.
        """
        self._save_general_page_settings(settings)
        self._save_task_page_settings(settings)

    # -------------------------------------------------------------------------
    def _save_general_page_settings(self, settings: UserSettings) -> None:
        """Save snapshot retention settings from the general options page.

        Args:
            settings (UserSettings): Settings object in which to store the
              values.
        """
        retention_policy = self._value_for_checked_button(
            self._retention_policy_by_button,
            self._ui.retention_policy_button_group.checkedButton(),
        )
        if retention_policy is not None:
            settings.set_value(
                SettingsKeys.RETENTION_POLICY,
                retention_policy,
                self.snapshot_retention_policy_changed.emit,
            )

        retention_count = self._ui.keep_latest_spin.value()
        settings.set_value(
            SettingsKeys.RETENTION_COUNT,
            retention_count,
            self.snapshot_retention_count_changed.emit,
        )

    # -------------------------------------------------------------------------
    def _save_task_page_settings(self, settings: UserSettings) -> None:
        """Save archive naming settings from the task options page.

        Args:
            settings (UserSettings): Settings object in which to store the
              values.
        """
        filename_suffix = self._value_for_checked_button(
            self._filename_suffix_by_button,
            self._ui.archive_naming_button_group.checkedButton(),
        )
        if filename_suffix is not None:
            settings.set_value(
                SettingsKeys.ARCHIVE_FILENAME_SUFFIX,
                filename_suffix,
                self.archive_filename_suffix_changed.emit,
            )

    # -------------------------------------------------------------------------
    @staticmethod
    def _value_for_checked_button[T: StrEnum](
        mapping: dict[QAbstractButton, T],
        button: QAbstractButton | None,
    ) -> T | None:
        """Return the value mapped to the checked button, if any.

        Args:
            mapping (dict[QAbstractButton, T]): Buttons and their mapped
              values.
            button (QAbstractButton | None): Checked button, or ``None`` when
              no button is selected.

        Returns:
            T | None: Mapped value, or ``None`` when no button is selected.
        """
        return mapping.get(button) if button is not None else None
