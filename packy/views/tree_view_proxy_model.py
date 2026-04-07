"""Module providing a proxy model for filtering tree views by path."""

from typing import override

from PySide6 import QtCore
from PySide6.QtWidgets import QFileSystemModel


###############################################################################
class TreeViewProxyModel(QtCore.QSortFilterProxyModel):
    """A proxy model that filters file system entries based on a root path."""

    def __init__(self, root_path: str, parent: QtCore.QObject | None = None) -> None:
        """Initialize the proxy model with a target root path.

        Args:
            root_path: The absolute path used as the filter root.
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self._root_path = root_path

    @override
    def filterAcceptsRow(self, source_row: int, source_parent: QtCore.QModelIndex) -> bool:
        model = self.sourceModel()
        if not isinstance(model, QFileSystemModel):
            return super().filterAcceptsRow(source_row, source_parent)

        source_index = model.index(source_row, 0, source_parent)
        item_path = model.filePath(source_index)
        is_within_root = item_path.lower().startswith(self._root_path.lower())
        is_root_of_item = self._root_path.lower().startswith(item_path.lower())
        return is_within_root or is_root_of_item
