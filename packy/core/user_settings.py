"""Provide persistent user-scoped application settings.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Future library
from __future__ import annotations

# Third-party
from PySide6.QtCore import (
    QByteArray,
    QCoreApplication,
    QObject,
    QSettings,
)

# Standard library
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, cast, final

if TYPE_CHECKING:
    # Third-party
    from PySide6.QtWidgets import QWidget

    # Standard library
    from collections.abc import Callable


###############################################################################
@final
class SettingNotFoundError(Exception):
    """Represent an unavailable application setting."""

    def __init__(self, setting_name: str) -> None:
        """Initialize the error for the specified setting.

        Args:
            setting_name (str): Name of the setting that could not be found.
        """
        msg = f"The setting with the name '{setting_name}'' cannot be found"
        super().__init__(msg)


###############################################################################
@final
class UserSettings(QObject):
    """Provide access to persistent user-scoped application settings.

    Settings are stored in an INI file identified by the application's
    organization and application names.
    """

    # -------------------------------------------------------------------------
    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the persistent application settings.

        Args:
            parent (QObject | None): Parent object, or ``None`` if the settings object
              has no parent.
        """
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)
        self._persistent_config = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            QCoreApplication.organizationName(),
            QCoreApplication.applicationName(),
        )

    # -------------------------------------------------------------------------
    @property
    def file_path(self) -> Path:
        """Redirection to :func:`PySide6.QtCore.QSettings.fileName`."""
        return Path(self._persistent_config.fileName()).resolve()

    # -------------------------------------------------------------------------
    def begin_group(self, prefix: str) -> None:
        """Redirection to :func:`PySide6.QtCore.QSettings.beginGroup`."""
        self._persistent_config.beginGroup(prefix)

    # -------------------------------------------------------------------------
    def end_group(self) -> None:
        """Redirection to func:`PySide6.QtCore.QSettings.endGroup`."""
        self._persistent_config.endGroup()

    # -------------------------------------------------------------------------
    def set_value[T](
        self,
        name: str,
        value: T,
        on_changed: Callable[[T], None] | None = None,
    ) -> bool:
        """Store a setting when its value has changed.

        The callback is invoked after the new value is stored.

        Args:
            name (str): Name of the setting to update.
            value (T): Value to store.
            on_changed (Callable[[T], None] | None): Function invoked with the new
              value after a change, or ``None`` to omit notification.

        Returns:
            bool: ``True`` if the value was changed and stored; otherwise, ``False``.
        """
        old_value = self._persistent_config.value(name)
        if old_value == value:
            return False
        self._persistent_config.setValue(name, value)
        if on_changed is not None:
            on_changed(value)
        return True

    # -------------------------------------------------------------------------
    def value[T](self, name: str, default_value: T) -> T:
        """See :func:`PySide6.QtCore.QSettings.value`."""
        if isinstance(default_value, Enum):
            value = self._persistent_config.value(name, default_value.value)
            try:
                return cast("T", type(default_value)(value))
            except ValueError:
                return default_value
        return cast(
            "T",
            self._persistent_config.value(
                name,
                default_value,
                type(default_value),
            ),
        )

    # -------------------------------------------------------------------------
    def save_layout_geometry_for(self, widget: QWidget) -> None:
        """Save a widget's visibility and geometry.

        When no settings group is active, the values are stored in a temporary group
        named after the widget.

        Args:
            widget (QWidget): Widget whose visibility and geometry are saved.
        """
        in_group: bool = self._persistent_config.group() != ""
        if not in_group:
            self._persistent_config.beginGroup(widget.objectName())
        self._persistent_config.setValue("Visible", widget.isVisible())
        self._persistent_config.setValue("Geometry", widget.saveGeometry())
        if not in_group:
            self._persistent_config.endGroup()

    # -------------------------------------------------------------------------
    def restore_layout_geometry_for(self, widget: QWidget) -> None:
        """Restore a widget's saved visibility and geometry.

        When no settings group is active, the values are read from a temporary group
        named after the widget. Missing visibility defaults to ``True``, and missing
        geometry defaults to an empty :class:`QByteArray`.

        Args:
            widget (QWidget): Widget whose visibility and geometry are restored.
        """
        in_group: bool = self._persistent_config.group() != ""
        if not in_group:
            self._persistent_config.beginGroup(widget.objectName())
        visible = cast(
            "bool",
            self._persistent_config.value("Visible", defaultValue=True, type=bool),
        )
        geometry = cast(
            "QByteArray",
            self._persistent_config.value("Geometry", QByteArray(), type=QByteArray),
        )
        if not in_group:
            self._persistent_config.endGroup()

        widget.setVisible(visible)
        widget.restoreGeometry(geometry)
        if visible:
            widget.show()
