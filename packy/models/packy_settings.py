"""Provide application settings management.

This module defines settings manager responsible for
persisting and restoring user preferences.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Third-party
from PySide6.QtCore import QByteArray, QCoreApplication, QObject, QRect, QSettings, Signal
from PySide6.QtWidgets import QMainWindow, QWidget

# Standard library
from enum import Enum, StrEnum, auto
from typing import cast


# ###############################################################################
class PreferencesGeneral(Enum):
    SR_KEEP_ALL = 0  # "Snapshot retention": "Keep all snapshots"
    SR_NB_SNAPSHOT = auto()  # "Snapshot retention": "Number of latest snapshots to keep"
    SR_NB = auto()  # "Snapshot retention": spin_box_nb_snapshots


# ###############################################################################
class PreferencesTask(Enum):
    SUFFIX_CURR_DATE = 0  # "Output format": "Add the current date"
    SUFFIX_VERSION_NUM = auto()  # "Output format": "Add version numbers"
    SUFFIX_NOTHING = auto()  # "Output format": "Add nothing"


# ###############################################################################
class PreferencesKeys(Enum):
    GENERAL_SR = "general/snapshot_retention"
    GENERAL_NB_SNAPSHOT = "general/nb_snapshots"
    TASK_SUFFIX = "task/suffix"


###############################################################################
class SettingNotFoundError(Exception):
    """A required setting key is missing from the configuration storage."""

    def __init__(self, setting: str) -> None:
        """Initialize the exception with the missing setting key.

        Args:
            setting (str): The name of the missing setting key.
        """
        msg = f'The setting key "{setting}" cannot be found'
        super().__init__(msg)


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
class PackySettings(QObject):
    """Manage persistent application settings using QSettings.

    This class provides methods to save and restore UI state and user
    preferences. It also emits signals when settings are modified.

    Attributes:
        layout_geometry_changed (Signal): Emitted when a widget geometry
            is saved. Arguments: (QWidget, QRect).
        main_window_state_changed (Signal): Emitted when the main window
            state is saved. Arguments: (QByteArray).
        snapshot_retention_policy_changed (Signal): Emitted when the
            snapshot retention policy changes. Arguments:
            (SnapshotRetentionPolicy).
        snapshot_retention_count_changed (Signal): Emitted when the
            snapshot retention count changes. Arguments: (int).
        archive_filename_suffix_changed (Signal): Emitted when the
            archive filename suffix changes. Arguments:
            (FilenameSuffix).
    """

    layout_geometry_changed = Signal(QWidget, QRect)
    main_window_state_changed = Signal(QByteArray)
    snapshot_retention_policy_changed = Signal(SnapshotRetentionPolicy)
    snapshot_retention_count_changed = Signal(int)
    archive_filename_suffix_changed = Signal(FilenameSuffix)

    # --------------------------------------------------------------------------
    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the settings manager.

        Args:
            parent (QObject | None): The parent object. Defaults to None.
        """
        super().__init__(parent)
        self.__settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            QCoreApplication.organizationName(),
            QCoreApplication.applicationName(),
        )

    # --------------------------------------------------------------------------
    def save_layout_geometry_for(self, widget: QWidget) -> None:
        """Save visibility and geometry state for a widget.

        Args:
            widget (QWidget): The widget whose layout state is saved.
        """
        visible = widget.isVisible()
        self.__settings.beginGroup(widget.objectName())
        self.__settings.setValue("Visible", visible)
        self.__settings.setValue("Geometry", widget.saveGeometry())
        self.__settings.endGroup()
        self.layout_geometry_changed.emit(widget, widget.geometry())

    # --------------------------------------------------------------------------
    def restore_layout_geometry(self, widget: QWidget) -> None:
        """Restore visibility and geometry state for a widget.

        Args:
            widget (QWidget): The widget whose layout state is restored.
        """
        self.__settings.beginGroup(widget.objectName())
        visible = cast("bool", self.__settings.value("Visible", defaultValue=True, type=bool))
        widget.setVisible(visible)
        geometry = cast(
            "QByteArray",
            self.__settings.value("Geometry", QByteArray(), type=QByteArray),
        )
        widget.restoreGeometry(geometry)
        self.__settings.endGroup()

    # --------------------------------------------------------------------------
    def save_main_window_state(self, main_window: QMainWindow) -> None:
        """Save the state of the main window.

        Args:
            main_window (QMainWindow): The main window instance.
        """
        self.__settings.beginGroup("MainWindow")
        self.__settings.setValue("State", main_window.saveState())
        self.__settings.endGroup()
        self.main_window_state_changed.emit(main_window.saveState())

    # --------------------------------------------------------------------------
    def restore_main_window_state(self, main_window: QMainWindow) -> None:
        """Restore the state of the main window.

        Args:
            main_window (QMainWindow): The main window instance.
        """
        self.__settings.beginGroup("MainWindow")
        state = cast("QByteArray", self.__settings.value("State", QByteArray(), type=QByteArray))
        main_window.restoreState(state)
        self.__settings.endGroup()

    # --------------------------------------------------------------------------
    def snapshot_retention_policy(self) -> SnapshotRetentionPolicy:
        """Return the current snapshot retention policy.

        Returns:
            SnapshotRetentionPolicy: The configured retention policy.
        """
        raw = self.__settings.value(
            "Snapshot/Retention/Policy",
            SnapshotRetentionPolicy.KEEP_ALL,
            type=str,
        )
        try:
            return SnapshotRetentionPolicy(str(raw))
        except ValueError:
            return SnapshotRetentionPolicy.KEEP_ALL

    # --------------------------------------------------------------------------
    def set_snapshot_retention_policy(self, policy: SnapshotRetentionPolicy) -> None:
        """Set the snapshot retention policy.

        Args:
            policy (SnapshotRetentionPolicy): The retention policy to set.
        """
        self.__settings.setValue("Snapshot/Retention/Policy", policy.value)
        self.snapshot_retention_policy_changed.emit(policy)

    # --------------------------------------------------------------------------
    def snapshots_retention_count(self) -> int:
        """Return the number of snapshots to retain.

        Returns:
            int: The configured retention count.
        """
        return cast("int", self.__settings.value("Snapshot/Retention/Count", 1, type=int))

    # --------------------------------------------------------------------------
    def set_snapshots_retention_count(self, count: int) -> None:
        """Set the number of snapshots to retain.

        Args:
            count (int): The number of snapshots to keep.
        """
        self.__settings.setValue("Snapshot/Retention/Count", count)
        self.snapshot_retention_count_changed.emit(count)

    # --------------------------------------------------------------------------
    def archive_filename_suffix(self) -> FilenameSuffix:
        """Return the current archive filename suffix strategy.

        Returns:
            FilenameSuffix: The configured filename suffix strategy.
        """
        raw = self.__settings.value("Task/Archive/FilenameSuffix", FilenameSuffix.NONE, type=str)
        try:
            return FilenameSuffix(str(raw))
        except ValueError:
            return FilenameSuffix.NONE

    # --------------------------------------------------------------------------
    def set_archive_filename_suffix(self, suffix: FilenameSuffix) -> None:
        """Set the archive filename suffix strategy.

        Args:
            suffix (FilenameSuffix): The suffix strategy to apply.
        """
        self.__settings.setValue("Task/Archive/FilenameSuffix", suffix.value)
        self.archive_filename_suffix_changed.emit(suffix)
