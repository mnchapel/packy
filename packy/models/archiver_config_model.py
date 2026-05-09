"""Archiver configuration models and archive option abstractions.

This module defines archive formats, compression settings, and a Qt model
used to expose archiver configuration through Qt's model/view framework.
It also provides a registry system for archive format-specific options.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.isettings_persistable import ISettingsPersistable
from packy.core.labeled_enum import LabeledEnum

# Third-party
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
)

# Standard library
from dataclasses import dataclass
from enum import IntEnum, auto, unique
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, final, override

if TYPE_CHECKING:
    # Local application
    from packy.core.settings import Settings

    # Standard library
    from collections.abc import Callable


###############################################################################
@unique
class ArchiveFormat(LabeledEnum):
    """Supported archive output formats."""

    ZIP = (auto(), "zip")
    TAR = (auto(), "tar")
    BZ2 = (auto(), "bz2")
    TBZ = (auto(), "tbz")
    GZ = (auto(), "gz")
    TGZ = (auto(), "tgz")
    LZMA = (auto(), "lzma")
    TLZ = (auto(), "tlz")
    XZ = (auto(), "xz")


###############################################################################
@unique
class CompressionMethod(LabeledEnum):
    """Supported archive compression methods."""

    DEFLATE = (auto(), "Deflate")
    STORE = (auto(), "Store")
    OPTIMAL = (auto(), "Optimal (2x slower)")


###############################################################################
@unique
class CompressionLevel(LabeledEnum):
    """Supported compression levels."""

    NORMAL = (auto(), "Normal")
    MAXIMUM = (auto(), "Maximum")
    FAST = (auto(), "Fast")
    FASTEST = (auto(), "Fastest")


###############################################################################
@dataclass
class FormatOptions(Protocol):
    """Archive format-specific option containers.

    Provides a registry mechanism allowing format option implementations
    to be dynamically associated with archive formats.

    Attributes:
        _registry (ClassVar[dict[ArchiveFormat, type[FormatOptions]]]):
            Mapping between archive formats and their option classes.
    """

    _registry: ClassVar[dict[ArchiveFormat, type[FormatOptions]]] = {}

    @classmethod
    def register(cls, fmt: ArchiveFormat) -> Callable[[type[FormatOptions]], type[FormatOptions]]:
        """Registers a format option class for a specific archive format.

        Args:
            fmt (ArchiveFormat): The archive format associated with the
                    option class.

        Returns:
            Callable[[type[FormatOptions]], type[FormatOptions]]: A class
            decorator registering the option implementation.
        """

        def decorator(subclass: type[FormatOptions]) -> type[FormatOptions]:
            cls._registry[fmt] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, fmt: ArchiveFormat) -> FormatOptions | None:
        """Creates the option instance associated with an archive format.

        Args:
            fmt (ArchiveFormat): The archive format.

        Returns:
            FormatOptions | None: The instantiated format options object, or
            None if no implementation is registered.
        """
        subclass = cls._registry.get(fmt)
        return subclass() if subclass else None


###############################################################################
@FormatOptions.register(ArchiveFormat.ZIP)
@dataclass
class ZipOptions(FormatOptions):
    """Configuration options specific to ZIP archive generation."""


###############################################################################
class FinalMeta(type(QAbstractListModel), type(ISettingsPersistable)):  # pyright: ignore[reportGeneralTypeIssues]  # noqa: D101
    pass


###############################################################################
@final
class ArchiverConfigModel(QAbstractListModel, ISettingsPersistable, metaclass=FinalMeta):
    """Qt list model storing archiver configuration parameters.

    This model exposes archive settings through Qt's model/view API to
    support direct binding with widgets using QDataWidgetMapper.

    Signals:
        format_changed (ArchiveFormat): Emitted when the archive format
            changes.
        compression_changed (CompressionMethod): Emitted when the
            compression method changes.
        compression_level_changed (CompressionLevel): Emitted when the
            compression level changes.
        options_changed (FormatOptions): Emitted when format-specific
            options change.
    """

    class Column(IntEnum):
        """Model rows representing archiver configuration fields.

        Attributes:
            FORMAT (int): Archive format row.
            COMPRESSION (int): Compression method row.
            COMPRESSION_LEVEL (int): Compression level row.
        """

        FORMAT = 0
        COMPRESSION = auto()
        COMPRESSION_LEVEL = auto()

    format_changed = Signal(ArchiveFormat)
    compression_changed = Signal(CompressionMethod)
    compression_level_changed = Signal(CompressionLevel)
    options_changed = Signal(FormatOptions)

    # -------------------------------------------------------------------------
    def __init__(self, parent: QObject | None = None) -> None:
        """Initializes the archiver configuration model.

        Creates the default archive configuration and initializes the
        associated format-specific options.

        Args:
            parent (QObject | None): The parent object. Defaults to None.
        """
        super().__init__(parent)

        self.__format: ArchiveFormat = ArchiveFormat.ZIP
        self.__compression: CompressionMethod = CompressionMethod.STORE
        self.__compression_level: CompressionLevel = CompressionLevel.NORMAL
        self.__options: FormatOptions | None = FormatOptions.create(self.__format)

    # -------------------------------------------------------------------------
    @override
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        if parent is None:
            parent = QModelIndex()
        if parent.isValid():
            return 0
        return len(ArchiverConfigModel.Column)

    # -------------------------------------------------------------------------
    @override
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex) -> int:
        if parent.isValid():
            return 0
        return 1

    # -------------------------------------------------------------------------
    @override
    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.ItemIsEnabled
        return super().flags(index) | Qt.ItemFlag.ItemIsEditable

    # -------------------------------------------------------------------------
    @override
    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid():
            return None
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            match ArchiverConfigModel.Column(row):
                case ArchiverConfigModel.Column.FORMAT:
                    return self.__format.label
                case ArchiverConfigModel.Column.COMPRESSION:
                    return self.__compression.label
                case ArchiverConfigModel.Column.COMPRESSION_LEVEL:
                    return self.__compression_level.label
        if role == Qt.ItemDataRole.EditRole:
            match ArchiverConfigModel.Column(row):
                case ArchiverConfigModel.Column.FORMAT:
                    return self.__format.id
                case ArchiverConfigModel.Column.COMPRESSION:
                    return self.__compression.id
                case ArchiverConfigModel.Column.COMPRESSION_LEVEL:
                    return self.__compression_level.id
        if role == Qt.ItemDataRole.UserRole:
            match ArchiverConfigModel.Column(row):
                case ArchiverConfigModel.Column.FORMAT:
                    return self.__format
                case ArchiverConfigModel.Column.COMPRESSION:
                    return self.__compression
                case ArchiverConfigModel.Column.COMPRESSION_LEVEL:
                    return self.__compression_level
        return None

    # -------------------------------------------------------------------------
    @override
    def setData(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid():
            return False
        row = index.row()

        if role == Qt.ItemDataRole.EditRole:
            match ArchiverConfigModel.Column(row):
                case ArchiverConfigModel.Column.FORMAT:
                    if not isinstance(value, int):
                        raise TypeError
                    self.format = ArchiveFormat(value)
                case ArchiverConfigModel.Column.COMPRESSION:
                    if not isinstance(value, int):
                        raise TypeError
                    self.compression = CompressionMethod(value)
                case ArchiverConfigModel.Column.COMPRESSION_LEVEL:
                    if not isinstance(value, int):
                        raise TypeError
                    self.compression_level = CompressionLevel(value)
                case _:
                    return False
            return True
        if role == Qt.ItemDataRole.UserRole:
            match ArchiverConfigModel.Column(row):
                case ArchiverConfigModel.Column.FORMAT:
                    if not isinstance(value, ArchiveFormat):
                        raise TypeError
                    self.format = value
                case ArchiverConfigModel.Column.COMPRESSION:
                    if not isinstance(value, CompressionMethod):
                        raise TypeError
                    self.compression = value
                case ArchiverConfigModel.Column.COMPRESSION_LEVEL:
                    if not isinstance(value, CompressionLevel):
                        raise TypeError
                    self.compression_level = value
                case _:
                    return False
            return True
        return False

    # -------------------------------------------------------------------------
    @override
    def read_settings(self, settings: Settings) -> None:
        pass

    # -------------------------------------------------------------------------
    @override
    def write_settings(self, settings: Settings) -> None:
        pass

    # -------------------------------------------------------------------------
    @property
    def format(self) -> ArchiveFormat:
        """The currently selected archive format.

        Returns:
            ArchiveFormat: The selected archive format.
        """
        return self.__format

    # -------------------------------------------------------------------------
    @format.setter  # noqa: A003
    def format(self, value: ArchiveFormat) -> None:
        """Sets the archive format.

        Updating the format also refreshes the associated format-specific
        options instance.

        Args:
            value (ArchiveFormat): The archive format to apply.
        """
        if self.__format == value:
            return
        self.__format = value
        self.__options = FormatOptions.create(value)
        index_changed = self.index(ArchiverConfigModel.Column.FORMAT.value, 0)
        self.dataChanged.emit(
            index_changed,
            index_changed,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.UserRole],
        )
        self.format_changed.emit(value)

    # -------------------------------------------------------------------------
    @property
    def compression(self) -> CompressionMethod:
        """The currently selected compression method.

        Returns:
            CompressionMethod: The active compression method.
        """
        return self.__compression

    # -------------------------------------------------------------------------
    @compression.setter
    def compression(self, value: CompressionMethod) -> None:
        """Sets the compression method.

        Args:
            value (CompressionMethod): The compression method to apply.
        """
        if self.__compression == value:
            return
        self.__compression = value
        index_changed = self.index(ArchiverConfigModel.Column.COMPRESSION.value, 0)
        self.dataChanged.emit(
            index_changed,
            index_changed,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.UserRole],
        )
        self.compression_changed.emit(value)

    # -------------------------------------------------------------------------
    @property
    def compression_level(self) -> CompressionLevel:
        """The currently selected compression level.

        Returns:
            CompressionLevel: The active compression level.
        """
        return self.__compression_level

    # -------------------------------------------------------------------------
    @compression_level.setter
    def compression_level(self, value: CompressionLevel) -> None:
        """Sets the compression level.

        Args:
            value (CompressionLevel): The compression level to apply.
        """
        if self.__compression_level == value:
            return
        self.__compression_level = value
        index_changed = self.index(
            ArchiverConfigModel.Column.COMPRESSION_LEVEL.value,
            0,
            QModelIndex(),
        )
        self.dataChanged.emit(
            index_changed,
            index_changed,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.UserRole],
        )
        self.compression_level_changed.emit(value)
