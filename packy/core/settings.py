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
from enum import Enum, auto
from typing import TYPE_CHECKING, cast, final

if TYPE_CHECKING:
    # Standard library
    from collections.abc import Callable


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
@final
class Settings(QObject):
    """Manage persistent application settings using QSettings.

    This class provides methods to save and restore UI state and user
    preferences. It also emits signals when settings are modified.

    Attributes:
        layout_geometry_changed (Signal): Emitted when a widget geometry
            is saved. Arguments: (QWidget, QRect).
        main_window_state_changed (Signal): Emitted when the main window
            state is saved. Arguments: (QByteArray).
    """

    layout_geometry_changed = Signal(QWidget, QRect)
    main_window_state_changed = Signal(QByteArray)

    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    def begin_group(self, prefix: str) -> None:
        """Redirection to :func:`PySide6.QtCore.QSettings.beginGroup`."""
        self.__settings.beginGroup(prefix)

    # -------------------------------------------------------------------------
    def end_group(self) -> None:
        """Redirection to func:`PySide6.QtCore.QSettings.endGroup`."""
        self.__settings.endGroup()

    # -------------------------------------------------------------------------
    def set_value[T](
        self,
        key: str,
        value: T,
        on_changed: Callable[[T], None] | None = None,
    ) -> bool:
        """Sets the value of setting key to value.

        If the key already exists, the previous value is overwritten.

        Args:
            key (str): The name of the setting key.
            value (Any): The value of the setting key.
            on_changed (Callable[[Any], None] | None): A callback function
                to be called when the value is changed.

        Returns:
            bool: true if the value has changed; false otherwise
        """
        old_value = self.__settings.value(key)
        if old_value == value:
            return False
        self.__settings.setValue(key, value)
        if on_changed is not None:
            on_changed(value)
        return True

    # -------------------------------------------------------------------------
    def value[T](self, key: str, default: T) -> T:
        """See :func:`PySide6.QtCore.QSettings.value`."""
        val = self.__settings.value(key, default, type(default))
        if isinstance(default, Enum) and not isinstance(val, Enum):
            try:
                return type(default)(val)
            except ValueError:
                return default
        return cast("T", val)

    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    def save_main_window_state(self, main_window: QMainWindow) -> None:
        """Save the state of the main window.

        Args:
            main_window (QMainWindow): The main window instance.
        """
        self.__settings.beginGroup(main_window.objectName())
        self.__settings.setValue("State", main_window.saveState())
        self.__settings.endGroup()
        self.main_window_state_changed.emit(main_window.saveState())

    # -------------------------------------------------------------------------
    def restore_main_window_state(self, main_window: QMainWindow) -> None:
        """Restore the state of the main window.

        Args:
            main_window (QMainWindow): The main window instance.
        """
        self.__settings.beginGroup(main_window.objectName())
        state = cast("QByteArray", self.__settings.value("State", QByteArray(), type=QByteArray))
        main_window.restoreState(state)
        self.__settings.endGroup()
