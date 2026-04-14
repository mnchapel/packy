"""Model representing a file system with checkable items.

This model extends ``QFileSystemModel`` to add support for check states
on files and directories, allowing users to select items within a
directory tree. It also tracks differences between the current file
system and the stored selection through a warnings system.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Standard library
import os
from enum import Enum
from pathlib import Path
from typing import Any, override

# Local application
from models.warnings import Warnings

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import QDir, QModelIndex, QObject, QPersistentModelIndex, Qt, Slot
from PySide6.QtWidgets import QFileSystemModel

from __feature__ import snake_case, true_property


###############################################################################
class FilesModelSerialKeys(Enum):
    """Enumeration of keys used for FilesModel serialization.

    These keys are used when converting a FilesModel instance to and from
    a dictionary (e.g., for JSON serialization).

    Attributes:
        ROOT_PATH (str):
            Key representing the root directory path of the model.
        CHECK (str):
            Key representing the mapping of file paths to their check states.
    """

    ROOT_PATH = "root_path"
    CHECK = "check"


###############################################################################
class FilesModel(QFileSystemModel):
    """File system model with checkable items and integrity tracking.

    This class extends ``QFileSystemModel`` to add support for check states
    on files and directories. It allows users to select items in a directory
    tree and keeps track of changes between the current file system and the
    stored selection using a warnings mechanism.

    The model maintains an internal mapping of file paths to their check
    states. Items not explicitly stored in this mapping are considered
    unchecked by default.

    It also provides utilities to detect added or removed files relative
    to the stored selection and to update the model accordingly.

    Attributes:
        __check_state_items (dict[str, int]):
            a dict with the check state for files and directories. If an item is not in the dict,
            its value is Qt.CheckState.Unchecked.value by default.
        __warnings (Warnings):
            an object which contains the modifications (added/removed items) between the model
            and the current selection.
    """

    # -------------------------------------------------------------------------
    def __init__(
        self,
        json_dict: dict[str, Any] | None = None,
        parent: QObject | None = None,
    ) -> None:
        """Initializes the file system model.

        Args:
                json_dict (dict, optional):
                    Serialized representation of the model used to restore its state.
                    Defaults to None.
                parent (QObject, optional):
                    Parent object passed to the underlying Qt model.
        """
        super().__init__(parent)
        self.__check_state_items: dict[str, int] = {}
        self.__warnings: Warnings = Warnings()

        if json_dict is not None:
            self.__json_init(json_dict)

        self.__init_filter()
        self.rowsInserted.connect(self.__check_if_added_items)

    # -------------------------------------------------------------------------
    def __json_init(self, json_dict: dict[str, Any]) -> None:
        self.set_root_path(json_dict[FilesModelSerialKeys.ROOT_PATH.value])
        self.__check_state_items = json_dict[FilesModelSerialKeys.CHECK.value]
        self.checkIntegrity()

    # -------------------------------------------------------------------------
    def __init_filter(self) -> None:
        file_filter = self.filter()
        self.set_filter(file_filter | QDir.Filter.Hidden)

    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """Returns a string representation of the model."""
        return f"files_model: root_path = {self.root_path()}, check = {{{self.__checks_to_str()}}}"

    # -------------------------------------------------------------------------
    def __checks_to_str(self) -> dict[str, int]:
        return {str(key): value for key, value in self.__check_state_items.items()}

    # -------------------------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        """Checks if two FilesModel instances are equal."""
        if not isinstance(other, FilesModel):
            return NotImplemented
        return (
            self.root_path() == other.root_path()
            and self.__check_state_items == other.__check_state_items
        )

    # -------------------------------------------------------------------------
    def __hash__(self) -> int:
        """Returns the hash of the model."""
        return hash((self.root_path(), tuple(sorted(self.__check_state_items.items()))))

    # -------------------------------------------------------------------------
    @property
    def checks(self) -> dict[str, int]:
        """Returns the dictionary of check states."""
        return self.__check_state_items

    # -------------------------------------------------------------------------
    @property
    def warnings(self) -> Warnings:
        """Returns the warnings object."""
        return self.__warnings

    # -------------------------------------------------------------------------
    @override
    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        match role:
            case Qt.ItemDataRole.CheckStateRole:
                if index.column() == 0:
                    return self.__check_state(index)
                return None
            case _:
                return super().data(index, role)

    # -------------------------------------------------------------------------
    @override
    def set_data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        match role:
            case Qt.ItemDataRole.CheckStateRole:
                if index.column() == 0:
                    self.__check_state_items[self.file_path(index)] = value
                    self.dataChanged.emit(index, index)

                    self.__update_child_files(index, value, role)
                    self.__update_parent_files(index, value)

                    return True

                QtCore.qDebug(
                    f"Wrong index.column() = {index.column()}. Index column should be equal to 0.",
                )
                return False
            case _:
                return super().set_data(index, value, role)

    # -------------------------------------------------------------------------
    def __update_child_files(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: int,
        role: Qt.ItemDataRole,
    ) -> None:
        if value != Qt.CheckState.PartiallyChecked.value:
            for i in range(self.row_count(index)):
                child_index = self.index(i, 0, index)
                self.set_data(child_index, value, role)

    # -------------------------------------------------------------------------
    def __update_parent_files(self, index: QModelIndex | QPersistentModelIndex, value: int) -> None:
        match value:
            case Qt.CheckState.Checked.value:
                self.__propagate_check_to_parents(index)
            case Qt.CheckState.Unchecked.value:
                self.__propagate_uncheck_to_parents(index)
            case _:
                QtCore.qDebug(
                    f"The Qt.CheckState value {value} should not appear in this function.",
                )

    # -------------------------------------------------------------------------
    def __propagate_check_to_parents(self, index: QModelIndex | QPersistentModelIndex) -> None:
        index_parent = index.parent()

        if index_parent == QModelIndex():
            return
        if self.file_path(index_parent) == self.root_path():
            return

        all_siblings_checked = True
        for i in range(self.row_count(index_parent)):
            index_sibling = self.index(i, 0, index_parent)
            if self.__check_state(index_sibling) != Qt.CheckState.Checked.value:
                all_siblings_checked = False

        if all_siblings_checked:
            self.__update_check_state(index_parent, Qt.CheckState.Checked)
            self.__propagate_check_to_parents(index_parent)
        elif self.__check_state(index_parent) == Qt.CheckState.Unchecked.value:
            self.__update_check_state(index_parent, Qt.CheckState.PartiallyChecked)
            self.__propagate_check_to_parents(index_parent)

    # -------------------------------------------------------------------------
    def __check_state(self, item: QModelIndex | QPersistentModelIndex | str) -> int:
        if isinstance(item, QModelIndex | QPersistentModelIndex):
            return self.__check_state_index(item)
        return self.__check_state_path(item)

    # -------------------------------------------------------------------------
    def __check_state_index(self, index: QModelIndex | QPersistentModelIndex) -> int:
        return self.__check_state_path(self.file_path(index))

    # -------------------------------------------------------------------------
    def __check_state_path(self, item_path: str) -> int:
        if item_path in self.__check_state_items:
            return self.__check_state_items[item_path]
        return Qt.CheckState.Unchecked.value

    # -------------------------------------------------------------------------
    def __update_check_state(self, index: QModelIndex, check_state: Qt.CheckState) -> None:
        self.__check_state_items[self.file_path(index)] = check_state.value
        self.dataChanged.emit(index, index)

    # -------------------------------------------------------------------------
    def __propagate_uncheck_to_parents(self, index: QModelIndex | QPersistentModelIndex) -> None:
        index_parent = index.parent()

        if self.__check_state(index_parent) == Qt.CheckState.Unchecked.value:
            return

        at_least_one_selected_child: bool = False

        for i in range(self.row_count(index_parent)):
            index_child = self.index(i, 0, index_parent)
            if self.__check_state(index_child) != Qt.CheckState.Unchecked.value:
                at_least_one_selected_child = True
                break

        new_check_state = Qt.CheckState.Unchecked
        if at_least_one_selected_child:
            new_check_state = Qt.CheckState.PartiallyChecked

        self.__update_check_state(index_parent, new_check_state)
        self.__propagate_uncheck_to_parents(index_parent)

    # -------------------------------------------------------------------------
    @override
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        return super().flags(index) | Qt.ItemFlag.ItemIsUserCheckable

    # -------------------------------------------------------------------------
    @override
    def set_root_path(self, path: str) -> QModelIndex:
        self.__check_state_items.clear()
        self.__warnings.clear()

        return super().set_root_path(path)

    # -------------------------------------------------------------------------
    def serialize(self) -> dict[str, Any]:
        """Serialize the current instance into a JSON-compatible dictionary."""
        data_dict: dict[str, Any] = {}

        data_dict[FilesModelSerialKeys.ROOT_PATH.value] = self.root_path()
        data_dict[FilesModelSerialKeys.CHECK.value] = self.__checks_to_str()

        return data_dict

    # -------------------------------------------------------------------------
    def checkIntegrity(self) -> None:
        """Check if checked items still exist and update warnings accordingly."""
        for item in self.__check_state_items:
            if self.__isItemChecked(item):
                # Removed item?
                if not self.__doesExists(item):
                    self.__warnings.addRemovedItem(item)
                # Added item?
                elif Path(item).is_dir():
                    self.listNewItems(item)
                elif self.__warnings.isInAddedCandidateItems(item):
                    self.__warnings.addAddedItem(item)

    # -------------------------------------------------------------------------
    def __isItemChecked(self, item: QModelIndex | str) -> bool:
        return self.__check_state(item) == Qt.CheckState.Checked.value

    # -------------------------------------------------------------------------
    def __doesExists(self, item_path: str) -> bool:
        return Path(item_path).exists()

    # -------------------------------------------------------------------------
    def listNewItems(self, dir_path: str) -> None:
        """Scan the root directory to add new files to the model.

        Identify untracked items and add them to warnings.
        """
        for root, _, files in os.walk(dir_path):
            for name in files:
                item = Path(root) / name
                if str(item) not in self.__check_state_items:
                    self.__warnings.addAddedItem(str(item))

    # -------------------------------------------------------------------------
    def updateModel(self) -> None:
        """Update the internal state based on current warnings."""
        removed_items = self.__warnings.removedItems()
        for item in removed_items:
            del self.__check_state_items[item]

        added_items = self.__warnings.addedItems()
        for item in added_items:
            self.__check_state_items[item] = Qt.CheckState.Checked.value

        self.__warnings.clear()

    # -------------------------------------------------------------------------
    @Slot(QModelIndex, int, int, result=None)
    def __check_if_added_items(self, parent: QModelIndex, first: int, last: int) -> None:
        for i in range(first, last + 1):
            child = self.index(i, 0, parent)
            if self.__isItemUnchecked(child):
                self.__warnings.addCandidateAddedItem(self.file_path(child))

    # -------------------------------------------------------------------------
    def __isItemUnchecked(self, item: QModelIndex | str) -> bool:
        return self.__check_state(item) == Qt.CheckState.Unchecked.value

    # -------------------------------------------------------------------------
    def __isItemPartiallyChecked(self, item: QModelIndex | str) -> bool:
        return self.__check_state(item) == Qt.CheckState.PartiallyChecked.value
