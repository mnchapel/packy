"""Message display widgets and utilities for formatted UI logging.

This module provides a QTextEdit-based widget for displaying colored
messages in a GUI, along with a message type enumeration.

Typical usage example:

  widget = MessagesWidget()
  widget.insert_line("Operation completed", MsgType.SUCCESS)

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.ui_strings import UIStrings

# Third-party
from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QContextMenuEvent
from PySide6.QtWidgets import QMenu, QTextEdit, QWidget

# Standard library
from enum import IntEnum, auto
from typing import final, override


###############################################################################
class MsgType(IntEnum):
    """Enumeration of message severity levels for UI display.

    Attributes:
        INFO (int): Informational message.
        SUCCESS (int): Successful operation message.
        ERROR (int): Error message.
    """

    INFO = 1
    SUCCESS = auto()
    ERROR = auto()


###############################################################################
@final
class MessagesWidget(QTextEdit):
    """A text widget for displaying formatted messages with severity colors.

    Provides convenience methods to insert color-coded messages and extend
    the default context menu with a clear action.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the message widget.

        Args:
            parent (QWidget | None): Parent widget. Defaults to None.
        """
        super().__init__(parent)

    @override
    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        menu: QMenu = super().createStandardContextMenu()
        menu.addSeparator()
        clear_action: QAction = QAction(UIStrings.tr(UIStrings.Menu.CLEAR), self)
        clear_action.triggered.connect(self.clear_messages)
        menu.addAction(clear_action)
        menu.exec(event.globalPos())

    @Slot(result=None)
    def clear_messages(self) -> None:
        """Clears all displayed messages from the widget."""
        super().clear()

    @Slot(result=None)
    def insert_line(self, message: str, msg_type: MsgType = MsgType.INFO) -> None:
        """Inserts a formatted message line with color based on its type.

        Args:
            message (str): The message text to display.
            msg_type (MsgType): The type of message, determining its color.
                Defaults to MsgType.INFO.
        """
        match msg_type:
            case MsgType.INFO:
                msg_font_color = "blue"
            case MsgType.SUCCESS:
                msg_font_color = "green"
            case MsgType.ERROR:
                msg_font_color = "red"

        message = f"<font color='{msg_font_color}'>{message}</font>"
        super().append(message)

    @Slot(result=None)
    def print_op_pack_file(self, msg_type: MsgType, file_path: str) -> None:
        """Formats and displays a pack file operation message.

        Args:
            msg_type (MsgType): The type of message to display.
            file_path (str): The file path involved in the operation.
        """
        match msg_type:
            case MsgType.INFO:
                message = UIStrings.tr(UIStrings.MessagesView.OP_INFO)
            case MsgType.SUCCESS:
                message = UIStrings.tr(UIStrings.MessagesView.OP_SUCCESS)
            case MsgType.ERROR:
                message = UIStrings.tr(UIStrings.MessagesView.OP_ERROR)

        message += UIStrings.tr(UIStrings.MessagesView.OP_PACK).format(file_path)
        self.insert_line(message, msg_type)
