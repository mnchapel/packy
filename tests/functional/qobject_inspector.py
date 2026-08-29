"""Inspect the state of selected QObjects in a Qt application.

The resulting snapshot stores QObject properties by property name and
observed child objects in nested dictionaries keyed by object name.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Future library
from __future__ import annotations

# Third-party
from PySide6.QtCore import QObject
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QGroupBox, QMainWindow, QMenu, QPushButton

# Standard library
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    # Third-party
    from PySide6.QtCore import QObject

    # Standard library
    from collections.abc import Iterator, Mapping

###############################################################################
### Type aliases
###############################################################################
type PropertyName = str
type ObjectName = str
type PropertySnapshot = dict[PropertyName, object]
type ObjectSnapshots = dict[ObjectName, QObjectState]


###############################################################################
### Object inspection configuration
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class QObjectState:
    """Captured state of a QObject."""

    qobject: QObject
    properties: PropertySnapshot

    def __getitem__(self, property_name: PropertyName) -> object:
        """Return the value of the requested property."""
        return self.properties[property_name]


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ObjectConfiguration:
    """Configuration used to inspect one QObject type."""

    property_names: tuple[PropertyName, ...] = ()
    observed_names: tuple[ObjectName, ...] = ()


# -----------------------------------------------------------------------------
OBJECT_CONFIGURATIONS: Final[Mapping[type[QObject], ObjectConfiguration]] = MappingProxyType(
    {
        QMainWindow: ObjectConfiguration(
            property_names=(
                "visible",
                "windowTitle",
                "windowFilePath",
                "windowModified",
            ),
        ),
        QAction: ObjectConfiguration(
            property_names=(
                "enabled",
                "visible",
                "checked",
            ),
            observed_names=(
                "action_save_batch",
                "action_save_batch_as",
                "action_close_batch",
            ),
        ),
        QMenu: ObjectConfiguration(
            property_names=(
                "enabled",
                "visible",
            ),
            observed_names=("open_recent_menu",),
        ),
        QPushButton: ObjectConfiguration(
            property_names=(
                "enabled",
                "visible",
                "checked",
            ),
            observed_names=(
                "create_job_button",
                "remove_job_button",
                "save_job_button",
                "move_up_job_button",
                "move_down_job_button",
                "run_all_jobs_button",
                "cancel_jobs_button",
            ),
        ),
        QGroupBox: ObjectConfiguration(
            property_names=(
                "enabled",
                "visible",
                "checked",
            ),
            observed_names=(
                "statistics_group",
                "file_selection_group",
                "output_group",
            ),
        ),
    },
)


###############################################################################
### QObject inspection helpers
###############################################################################
# -----------------------------------------------------------------------------
def _get_configuration(obj: QObject) -> ObjectConfiguration:
    """Return the inspection configuration applicable to a QObject.

    Args:
        obj (QObject): QObject to inspect.

    Returns:
        Configuration associated with the object's type.

    Raises:
        AssertionError: The object's type is not configured.
    """
    for object_type, configuration in OBJECT_CONFIGURATIONS.items():
        if isinstance(obj, object_type):
            return configuration

    msg = f"No inspection configuration for {type(obj).__name__} (objectName={obj.objectName()!r})"
    raise AssertionError(msg)


# -----------------------------------------------------------------------------
def _capture_properties(
    obj: QObject,
    property_names: tuple[PropertyName, ...],
) -> PropertySnapshot:
    """Capture selected Qt property values for an object.

    Args:
        obj (QObject): QObject whose properties are captured.
        property_names (tuple[PropertyName, ...]): Names of the Qt properties to include.

    Returns:
        PropertySnapshot: Current property values indexed by property name.

    Raises:
        AssertionError: A requested property does not exist.
    """
    snapshot: PropertySnapshot = {}
    meta_object = obj.metaObject()

    for property_name in property_names:
        property_index = meta_object.indexOfProperty(property_name)

        assert property_index >= 0, (
            f"Property {property_name!r} not found on "
            f"{meta_object.className()} "
            f"(objectName={obj.objectName()!r})"
        )
        snapshot[property_name] = obj.property(property_name)

    return snapshot


# -----------------------------------------------------------------------------
def _find_child(
    parent: QObject,
    object_type: type[QObject],
    object_name: ObjectName,
) -> QObject:
    """Find a named child QObject of the requested type.

    Args:
        parent (QObject): QObject whose descendants are searched.
        object_type (type[QObject]): Required type of the child.
        object_name (ObjectName): Required value of the child's ``objectName`` property.

    Returns:
        QObject: The matching child QObject.

    Raises:
        AssertionError: No matching child exists.
    """
    obj = parent.findChild(object_type, object_name)

    assert obj is not None, f"{object_type.__name__} with objectName={object_name!r} not found"
    return obj


# -----------------------------------------------------------------------------
def _iter_observed_children(
    root: QObject,
) -> Iterator[tuple[QObject, ObjectConfiguration]]:
    """Yield configured child QObjects together with their configurations.

    Args:
        root (QObject): QObject root whose current state is captured.

    Yields:
        Iterator[tuple[QObject, ObjectConfiguration]]: Child QObjects and their configurations.
    """
    for object_type, configuration in OBJECT_CONFIGURATIONS.items():
        for object_name in configuration.observed_names:
            obj = _find_child(
                root,
                object_type,
                object_name,
            )
            yield obj, configuration


###############################################################################
### Public API
###############################################################################
def capture_qobjects_state(root: QObject) -> ObjectSnapshots:
    """Capture the configured state of a QObject and its observed children.

    The root object's properties are stored under its object name. Each
    configured child QObject is stored under its own object name.

    Args:
        root (QObject): QObject whose current state is captured.

    Returns:
        ObjectSnapshots: Snapshot of the configured QObject state.

    Raises:
        AssertionError: If the root has no object name, an object type is not
          configured, a configured child is missing, or a configured Qt
          property does not exist.
    """
    root_name = root.objectName()
    assert root_name, "Root QObject must have a non-empty objectName"

    configuration = _get_configuration(root)
    snapshot: ObjectSnapshots = {
        root_name: QObjectState(
            qobject=root,
            properties=_capture_properties(
                root,
                configuration.property_names,
            ),
        ),
    }
    for obj, configuration in _iter_observed_children(root):
        object_name = obj.objectName()

        assert object_name, (
            f"Observed QObject of type {type(obj).__name__} must have a non-empty objectName"
        )

        snapshot[object_name] = QObjectState(
            qobject=obj,
            properties=_capture_properties(
                obj,
                configuration.property_names,
            ),
        )

    return snapshot
