"""Define archive configuration labels, options, and the Qt item model.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.constants.settings_keys import BatchSettings
from packy.core.archiver import Archiver
from packy.core.configurable import Configurable
from packy.utils.int_str_enum import IntStrEnum

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)

# Standard library
from dataclasses import dataclass
from enum import IntEnum, auto, unique
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, final, override

if TYPE_CHECKING:
    # Local application
    from packy.core.batch import Batch
    from packy.core.user_settings import UserSettings

    # Standard library
    from collections.abc import Callable


###############################################################################
@unique
class FormatLabel(IntStrEnum):
    """Represent display labels for supported archive formats."""

    ZIP = (Archiver.Format.ZIP, "zip")
    TAR = (Archiver.Format.TAR, "tar")
    BZ2 = (Archiver.Format.BZ2, "bz2")
    TBZ = (Archiver.Format.TBZ, "tbz")
    GZ = (Archiver.Format.GZ, "gz")
    TGZ = (Archiver.Format.TGZ, "tgz")
    LZMA = (Archiver.Format.LZMA, "lzma")
    TLZ = (Archiver.Format.TLZ, "tlz")
    XZ = (Archiver.Format.XZ, "xz")

    # -------------------------------------------------------------------------
    @property
    def format(self) -> Archiver.Format:
        """The archive format associated with the label."""
        return Archiver.Format(self.int_value)


###############################################################################
@unique
class CompressionMethodLabel(IntStrEnum):
    """Represent display labels for available compression methods."""

    DEFLATE = (Archiver.CompressionMethod.DEFLATE, "Deflate")
    STORE = (Archiver.CompressionMethod.STORE, "Store")
    OPTIMAL = (Archiver.CompressionMethod.OPTIMAL, "Optimal (2x slower)")

    # -------------------------------------------------------------------------
    @property
    def compression_method(self) -> Archiver.CompressionMethod:
        """The archive compression method associated with the label."""
        return Archiver.CompressionMethod(self.int_value)


###############################################################################
@unique
class CompressionLevelLabel(IntStrEnum):
    """Represent display labels for available compression levels."""

    NORMAL = (Archiver.CompressionLevel.NORMAL, "Normal")
    MAXIMUM = (Archiver.CompressionLevel.MAXIMUM, "Maximum")
    FAST = (Archiver.CompressionLevel.FAST, "Fast")
    FASTEST = (Archiver.CompressionLevel.FASTEST, "Fastest")

    # -------------------------------------------------------------------------
    @property
    def compression_level(self) -> Archiver.CompressionLevel:
        """The archive compression level associated with the label."""
        return Archiver.CompressionLevel(self.int_value)


###############################################################################
@dataclass
class FormatOptions(Protocol):
    """Define registration and creation of format-specific archive options."""

    _registry: ClassVar[dict[FormatLabel, type[FormatOptions]]] = {}

    # -------------------------------------------------------------------------
    @classmethod
    def register(
        cls,
        fmt: FormatLabel,
    ) -> Callable[[type[FormatOptions]], type[FormatOptions]]:
        """Register an options class for an archive format.

        Args:
            fmt (FormatLabel): Archive format associated with the options class.

        Returns:
            Callable[[type[FormatOptions]], type[FormatOptions]]: Decorator that
              registers and returns the options class.
        """

        def decorator(subclass: type[FormatOptions]) -> type[FormatOptions]:
            cls._registry[fmt] = subclass
            return subclass

        return decorator

    # -------------------------------------------------------------------------
    @classmethod
    def create(cls, fmt: FormatLabel) -> FormatOptions | None:
        """Create registered options for an archive format.

        Args:
            fmt (FormatLabel): Archive format whose options to create.

        Returns:
            FormatOptions | None: New options instance, or ``None`` when no options
              class is registered for the format.
        """
        subclass = cls._registry.get(fmt)
        return subclass() if subclass else None


###############################################################################
@FormatOptions.register(FormatLabel.ZIP)
@dataclass
class ZipOptions(FormatOptions):
    """Represent format-specific options for ZIP archives."""


###############################################################################
class FinalMeta(type(QAbstractListModel), type(Configurable)):  # pyright: ignore[reportGeneralTypeIssues]  # noqa: D101
    pass


###############################################################################
@final
class ArchiverConfigModel(QAbstractListModel, Configurable, metaclass=FinalMeta):
    """Expose archive configuration values through a Qt item model.

    Signals:
        format_changed (FormatLabel): Emitted when the archive format changes,
          with the new format.
        compression_method_changed (CompressionMethodLabel): Emitted when the
          compression method changes, with the new method.
        compression_level_changed (CompressionLevelLabel): Emitted when the
          compression level changes, with the new level.
    """

    ###########################################################################
    class Field(IntEnum):
        """Identify archive configuration fields in the model."""

        FORMAT = 0
        COMPRESSION_METHOD = auto()
        COMPRESSION_LEVEL = auto()

    # -------------------------------------------------------------------------
    format_changed = Signal(FormatLabel, arguments=["new_format"])
    compression_method_changed = Signal(
        CompressionMethodLabel,
        arguments=["new_compression_method"],
    )
    compression_level_changed = Signal(
        CompressionLevelLabel,
        arguments=["new_compression_level"],
    )

    # -------------------------------------------------------------------------
    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the archive configuration model.

        Args:
            parent (QObject | None): Parent object for the model.
        """
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)

        self._current_batch: Batch | None = None
        self._default_format = FormatLabel.ZIP
        self._default_compression_method = CompressionMethodLabel.STORE
        self._default_compression_level = CompressionLevelLabel.NORMAL
        self._default_options: FormatOptions | None = FormatOptions.create(
            self._default_format,
        )

    # -------------------------------------------------------------------------
    @override
    def rowCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        if parent is None:
            parent = QModelIndex()
        if parent.isValid():
            return 0
        return len(ArchiverConfigModel.Field)

    # -------------------------------------------------------------------------
    @override
    def columnCount(self, parent: QModelIndex | QPersistentModelIndex | None = None) -> int:
        if parent is None:
            parent = QModelIndex()
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
        try:
            column = ArchiverConfigModel.Field(row)
        except ValueError:
            return None

        config_value = self._config_value_for_column(column)
        if role == Qt.ItemDataRole.DisplayRole:
            return config_value.str_value
        if role == Qt.ItemDataRole.EditRole:
            return config_value.int_value
        if role == Qt.ItemDataRole.UserRole:
            return config_value
        return None

    # -------------------------------------------------------------------------
    def _config_value_for_column(self, column: Field) -> IntStrEnum:
        """Return the configuration value represented by a model column.

        Args:
            column (Column): Configuration field whose current value to return.

        Returns:
            IntStrEnum: Current value associated with the configuration field.
        """
        match column:
            case ArchiverConfigModel.Field.FORMAT:
                return self.format_label
            case ArchiverConfigModel.Field.COMPRESSION_METHOD:
                return self.compression_method_label
            case ArchiverConfigModel.Field.COMPRESSION_LEVEL:
                return self.compression_level_label

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
        try:
            column = ArchiverConfigModel.Field(row)
        except ValueError:
            return False

        if role == Qt.ItemDataRole.EditRole:
            self._set_config_value(column, value, value_is_int=True)
            return True
        if role == Qt.ItemDataRole.UserRole:
            self._set_config_value(column, value, value_is_int=False)
            return True
        return False

    # -------------------------------------------------------------------------
    def _set_config_value(
        self,
        column: Field,
        value: Any,  # noqa: ANN401
        *,
        value_is_int: bool,
    ) -> None:
        """Set a configuration value for a model column.

        Args:
            column (Column): Configuration field to update.
            value (Any): Value to assign to the configuration field.
            value_is_int (bool): Whether ``value`` is the integer representation of
              the configuration value.
        """
        match column:
            case ArchiverConfigModel.Field.FORMAT:
                self.format_label = FormatLabel(value) if value_is_int else value
            case ArchiverConfigModel.Field.COMPRESSION_METHOD:
                self.compression_method_label = CompressionMethodLabel(value) if value_is_int else value
            case ArchiverConfigModel.Field.COMPRESSION_LEVEL:
                self.compression_level_label = CompressionLevelLabel(value) if value_is_int else value

    # -------------------------------------------------------------------------
    @override
    def load_settings(self, settings: UserSettings) -> None:
        QtCore.qDebug(
            f"Loading {self.objectName()} from {BatchSettings.SETTINGS_GROUP}.",
        )

    # -------------------------------------------------------------------------
    @override
    def save_settings(self, settings: UserSettings) -> None:
        QtCore.qDebug(
            f"Saving {self.objectName()} in {BatchSettings.SETTINGS_GROUP}.",
        )

    # -------------------------------------------------------------------------
    @property
    def current_batch(self) -> Batch | None:
        """The batch that supplies archive configuration values, if any."""
        return self._current_batch

    # -------------------------------------------------------------------------
    def set_current_batch(self, new_batch: Batch | None) -> None:
        """Set the batch that supplies archive configuration values.

        Changing the batch disconnects the previous batch, connects archive
        configuration change signals from the new batch when present, and resets the
        model.

        Args:
            new_batch (Batch | None): Batch to observe, or ``None`` to clear the
              current batch.
        """
        if self._current_batch == new_batch:
            return

        if self._current_batch is not None:
            self._current_batch.disconnect(self)

        if new_batch is not None:
            self._connect_batch_signals(new_batch)

        self.beginResetModel()
        self._current_batch = new_batch
        self.endResetModel()

    # -------------------------------------------------------------------------
    def _connect_batch_signals(self, new_batch: Batch) -> None:
        """Connect archive configuration signals from a batch to the model.

        Args:
            new_batch (Batch): Batch whose archive configuration signals to
              connect.
        """
        new_batch.format_changed.connect(
            self._emit_format_changed,
        )
        new_batch.compression_level_changed.connect(
            self._emit_compression_level_changed,
        )
        new_batch.compression_method_changed.connect(
            self._emit_compression_method_changed,
        )

    # -------------------------------------------------------------------------
    @property
    def format_label(self) -> FormatLabel:
        """The archive format for the current batch, or the default format."""
        if self._current_batch is None:
            return self._default_format
        return FormatLabel(self._current_batch.archiver_format)

    # -------------------------------------------------------------------------
    @format_label.setter
    def format_label(self, value: FormatLabel) -> None:
        """Set the archive format for the current batch.

        The assignment has no effect when no batch is set or the value is unchanged.
        A change updates the batch and emits format change notifications.

        Args:
            value (FormatLabel): Archive format to assign.
        """
        if self._current_batch is None or self.format_label == value:
            return

        old_value = self._current_batch.archiver_format
        self._current_batch.archiver_format = value.format
        self._default_options = FormatOptions.create(value)
        self._emit_format_changed(
            old_value,
            self._current_batch.archiver_format,
        )

    # -------------------------------------------------------------------------
    @Slot(Archiver.Format, Archiver.Format)
    def _emit_format_changed(
        self,
        _old_value: Archiver.Format,
        new_value: Archiver.Format,
    ) -> None:
        """Emit model notifications for an archive format change.

        Args:
            _old_value (Archiver.Format): Previous archive format.
            new_value (Archiver.Format): New archive format to publish.
        """
        self._emit_data_changed(ArchiverConfigModel.Field.FORMAT)
        self.format_changed.emit(FormatLabel(new_value))

    # -------------------------------------------------------------------------
    def _emit_data_changed(self, column: Field) -> None:
        """Emit data change notifications for an archive configuration column.

        Args:
            column (Column): Configuration field whose model data changed.
        """
        index_changed: QModelIndex = self.index(column.value, 0, QModelIndex())
        self.dataChanged.emit(
            index_changed,
            index_changed,
            [
                Qt.ItemDataRole.DisplayRole,
                Qt.ItemDataRole.EditRole,
                Qt.ItemDataRole.UserRole,
            ],
        )

    # -------------------------------------------------------------------------
    @property
    def compression_method_label(self) -> CompressionMethodLabel:
        """The compression method for the current batch, or the default method."""
        if self._current_batch is None:
            return self._default_compression_method
        return CompressionMethodLabel(
            self._current_batch.archiver_compression_method,
        )

    # -------------------------------------------------------------------------
    @compression_method_label.setter
    def compression_method_label(self, value: CompressionMethodLabel) -> None:
        """Set the compression method for the current batch.

        The assignment has no effect when no batch is set or the value is unchanged.
        A change updates the batch and emits compression method change notifications.

        Args:
            value (CompressionMethodLabel): Compression method to assign.
        """
        if self._current_batch is None or self.compression_method_label == value:
            return

        old_value = self._current_batch.archiver_compression_method
        self._current_batch.archiver_compression_method = value.compression_method
        self._emit_compression_method_changed(
            old_value,
            self._current_batch.archiver_compression_method,
        )

    # -------------------------------------------------------------------------
    @Slot(Archiver.CompressionMethod, Archiver.CompressionMethod)
    def _emit_compression_method_changed(
        self,
        _old_value: Archiver.CompressionMethod,
        new_value: Archiver.CompressionMethod,
    ) -> None:
        """Emit model notifications for a compression method change.

        Args:
            _old_value (Archiver.CompressionMethod): Previous compression method.
            new_value (Archiver.CompressionMethod): New compression method to publish.
        """
        self._emit_data_changed(ArchiverConfigModel.Field.COMPRESSION_METHOD)
        self.compression_method_changed.emit(CompressionMethodLabel(new_value))

    # -------------------------------------------------------------------------
    @property
    def compression_level_label(self) -> CompressionLevelLabel:
        """The compression level for the current batch, or the default level."""
        if self._current_batch is None:
            return self._default_compression_level
        return CompressionLevelLabel(
            self._current_batch.archiver_compression_level,
        )

    # -------------------------------------------------------------------------
    @compression_level_label.setter
    def compression_level_label(self, value: CompressionLevelLabel) -> None:
        """Set the compression level for the current batch.

        The assignment has no effect when no batch is set or the value is unchanged.
        A change updates the batch and emits compression level change notifications.

        Args:
            value (CompressionLevelLabel): Compression level to assign.
        """
        if self._current_batch is None or self.compression_level_label == value:
            return

        old_value: Archiver.CompressionLevel = self._current_batch.archiver_compression_level
        self._current_batch.archiver_compression_level = value.compression_level
        self._emit_compression_level_changed(
            old_value,
            self._current_batch.archiver_compression_level,
        )

    # -------------------------------------------------------------------------
    @Slot(Archiver.CompressionLevel, Archiver.CompressionLevel)
    def _emit_compression_level_changed(
        self,
        _old_value: Archiver.CompressionLevel,
        new_value: Archiver.CompressionLevel,
    ) -> None:
        """Emit model notifications for a compression level change.

        Args:
            _old_value (Archiver.CompressionLevel): Previous compression level.
            new_value (Archiver.CompressionLevel): New compression level to publish.
        """
        self._emit_data_changed(ArchiverConfigModel.Field.COMPRESSION_LEVEL)
        self.compression_level_changed.emit(CompressionLevelLabel(new_value))
