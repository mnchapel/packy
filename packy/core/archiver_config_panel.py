"""Provide the archiver configuration panel and its widget bindings.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.constants.settings_keys import BatchSettings
from packy.core.archiver_config_model import (
    ArchiverConfigModel,
    CompressionLevelLabel,
    CompressionMethodLabel,
    FormatLabel,
)
from packy.core.configurable import Configurable
from packy.widgets.radio_group_widget import RadioGroupWidget

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QButtonGroup, QDataWidgetMapper, QRadioButton

# Standard library
from typing import TYPE_CHECKING, final, override

if TYPE_CHECKING:
    # Local application
    from packy.core.batch import Batch
    from packy.core.user_settings import UserSettings
    from packy.ui.ui_main_window import Ui_MainWindow


###############################################################################
class FinalMeta(type(QObject), type(Configurable)):  # pyright: ignore[reportGeneralTypeIssues]  # noqa: D101
    pass


###############################################################################
@final
class ArchiverConfigPanel(QObject, Configurable, metaclass=FinalMeta):
    """Coordinate the archive configuration widgets and their data model."""

    # -------------------------------------------------------------------------
    def __init__(
        self,
        main_window_widgets: Ui_MainWindow,
        parent: QObject | None = None,
    ) -> None:
        """Initialize the archive configuration panel.

        Args:
            main_window_widgets (Ui_MainWindow): Main-window widgets that contain the
              archive configuration controls.
            parent (QObject | None): Parent object for this panel.
        """
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)

        self._ui: Ui_MainWindow = main_window_widgets
        self._model = ArchiverConfigModel(self)

        self._setup_format_widget()
        self._setup_compression_method_widget()
        self._setup_compression_level_widget()
        self._setup_config_mapper()
        self._update_enabled_state()

        QtCore.qDebug(f"{self.__class__.__name__} initialized.")

    # -------------------------------------------------------------------------
    def _setup_format_widget(self) -> None:
        """Create and populate the archive format radio-button group."""
        self._format_button_group = QButtonGroup(self)
        self._format_button_group.setObjectName("FormatButtonGroup")

        rows_per_column = 3
        for index, format_label in enumerate(FormatLabel):
            format_button = QRadioButton(self._ui.archiver_config_group)
            format_button.setText(self.tr(format_label.str_value))
            format_button.setObjectName(f"{format_label.str_value}FormatButton")
            self._format_button_group.addButton(
                format_button,
                format_label.int_value,
            )

            row, column = divmod(index, rows_per_column)
            self._ui.format_buttons_layout.addWidget(format_button, row, column, 1, 1)

        self._format_group_widget = RadioGroupWidget(
            self._format_button_group,
            self._ui.archiver_config_group,
        )
        self._format_group_widget.setObjectName("FormatGroupWidget")

    # -------------------------------------------------------------------------
    def _setup_compression_method_widget(self) -> None:
        """Populate the compression method selector."""
        for method in CompressionMethodLabel:
            self._ui.compression_method.addItem(
                self.tr(method.str_value),
                method,
            )

    # -------------------------------------------------------------------------
    def _setup_compression_level_widget(self) -> None:
        """Populate the compression level selector."""
        for level in CompressionLevelLabel:
            self._ui.compression_level.addItem(
                self.tr(level.str_value),
                level,
            )

    # -------------------------------------------------------------------------
    def _setup_config_mapper(self) -> None:
        """Map the archive configuration widgets to the data model."""
        self._config_mapper = QDataWidgetMapper(self)
        self._config_mapper.setObjectName("ArchiverWidgetMapper")
        self._config_mapper.setSubmitPolicy(QDataWidgetMapper.SubmitPolicy.AutoSubmit)
        self._config_mapper.setOrientation(Qt.Orientation.Vertical)
        self._config_mapper.setModel(self._model)
        self._config_mapper.addMapping(
            self._format_group_widget,
            ArchiverConfigModel.Field.FORMAT,
            b"selected_button",
        )
        self._config_mapper.addMapping(
            self._ui.compression_method,
            ArchiverConfigModel.Field.COMPRESSION_METHOD,
            b"currentIndex",
        )
        self._config_mapper.addMapping(
            self._ui.compression_level,
            ArchiverConfigModel.Field.COMPRESSION_LEVEL,
            b"currentIndex",
        )
        self._config_mapper.toFirst()

    # -------------------------------------------------------------------------
    @property
    def model(self) -> ArchiverConfigModel:
        """The model associtated with this panel and used by its components."""
        return self._model

    # -------------------------------------------------------------------------
    @override
    def load_settings(self, settings: UserSettings) -> None:
        QtCore.qDebug(
            f"Loading {self.objectName()} settings from {BatchSettings.SETTINGS_GROUP}.",
        )
        self._model.load_settings(settings)

    # -------------------------------------------------------------------------
    @override
    def save_settings(self, settings: UserSettings) -> None:
        QtCore.qDebug(
            f"Saving {self.objectName()} settings in {BatchSettings.SETTINGS_GROUP}.",
        )
        self._model.save_settings(settings)

    # -------------------------------------------------------------------------
    def set_current_batch(self, new_batch: Batch | None) -> None:
        """Set the batch associated with the archive configuration.

        Args:
            new_batch (Batch | None): Batch to associate with the configuration, or
              ``None`` to clear the current batch.
        """
        if self._model.current_batch == new_batch:
            return

        if self._model.current_batch is not None:
            self._model.current_batch.disconnect(self)

        self._model.set_current_batch(new_batch)
        self._update_enabled_state()

    # -------------------------------------------------------------------------
    def _update_enabled_state(self) -> None:
        """Enable the archive configuration controls when a batch is set."""
        is_batch_set: bool = self._model.current_batch is not None
        self._ui.archiver_config_group.setEnabled(is_batch_set)
