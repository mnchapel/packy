"""Provide a Qt-integrated logging utility for debugging purposes.

This module defines a logger that captures Qt messages via a custom
message handler, formats them with contextual information, and writes
them to a log file. It also supports optional console output in
development environments.

Typical usage example:

  from pathlib import Path

  DebugLogger.start(Path("app.log"))
  # Run application...
  DebugLogger.stop()

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import QDateTime, QMessageLogContext, Qt, QThread, QtMsgType

# Standard library
import os
import sys
from typing import TYPE_CHECKING, Literal, TextIO, final

if TYPE_CHECKING:
    # Standard library
    from pathlib import Path


@final
class DebugLogger:
    """Provide a centralized logging facility for Qt messages.

    This class installs a Qt message handler to capture, format, and
    persist log messages into a file. It also optionally outputs logs
    to the console in development environments.

    Attributes:
        __log_file (TextIO | None): The file object used to write log
            messages. None if logging is not active.
    """

    __log_file: TextIO | None = None

    # -------------------------------------------------------------------------
    @classmethod
    def start(cls, log_file_path: Path) -> bool:
        """Start logging by opening the log file and installing handler.

        Args:
            log_file_path (Path): The path to the log file.

        Returns:
            bool: True if logging started successfully, false if already active.

        Raises:
            OSError: If the log file cannot be opened.
            PermissionError: If access to the log file is denied.
        """
        if cls.is_active():
            return False

        try:
            cls.__log_file = log_file_path.open(mode="a", buffering=1, encoding="utf-8")
        except OSError, PermissionError:
            cls.__log_file = None
            raise
        else:
            QtCore.qInstallMessageHandler(cls.q_message_handler)
            return True

    # -------------------------------------------------------------------------
    @classmethod
    def stop(cls) -> bool:
        """Stop logging and release associated resources.

        Returns:
            bool: True if logging was stopped, false if it was not active.
        """
        if not cls.is_active():
            return False

        QtCore.qInstallMessageHandler(None)
        cls.__log_file.close()  # pyright: ignore[reportOptionalMemberAccess] with the first test, we know the var is not None
        cls.__log_file = None
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def is_active(cls) -> bool:
        """Check whether the logger is currently active.

        Returns:
            bool: True if logging is active, false otherwise.
        """
        return cls.__log_file is not None

    # -------------------------------------------------------------------------
    @classmethod
    def q_message_handler(
        cls,
        msg_type: QtMsgType,
        msg_context: QMessageLogContext,
        msg: str,
    ) -> None:
        """Handle Qt log messages and delegate formatting and logging.

        Args:
            msg_type (QtMsgType): The type/severity of the message.
            msg_context (QMessageLogContext): Context information such as
                file and line number.
            msg (str): The log message content.
        """
        formated_msg = cls.__format_message(msg_type, msg_context.file, msg_context.line, msg)
        cls.__log_message(msg_type, formated_msg)

    # -------------------------------------------------------------------------
    @classmethod
    def __format_message(cls, msg_type: QtMsgType, ctx_file: str, ctx_line: int, msg: str) -> str:
        """Format a log message into a structured string.

        !! Warning !! Since the display of "files" and "lines" only works by default when Qt
        is in debug mode, we need to set QT_MESSAGELOGCONTEXT to enable them. But I haven't
        figured out how to do that in Python environment.

        Args:
            msg_type (QtMsgType): The type/severity of the message.
            ctx_file (str): The source file where the message originated.
            ctx_line (int): The line number in the source file.
            msg (str): The log message content.

        Returns:
            str: The formatted log message.
        """
        timestamp = QDateTime.currentDateTime().toString(Qt.DateFormat.ISODateWithMs)
        pid = os.getpid()
        thread_id = hex(id(QThread.currentThread()))
        level = cls.__msg_type_to_str(msg_type)
        formated_msg = f"[{timestamp}][{pid},0x{thread_id}][{ctx_file}:{ctx_line}][{level}]: {msg}"
        return formated_msg  # noqa: RET504

    # -------------------------------------------------------------------------
    @classmethod
    def __log_message(cls, msg_type: QtMsgType, msg: str) -> None:
        """Write a formatted message to the log file and optionally console.

        Args:
            msg_type (QtMsgType): The type/severity of the message.
            msg (str): The formatted log message.
        """
        if not cls.is_active():
            return

        # Log in file
        cls.__log_file.write(msg + "\n")  # pyright: ignore[reportOptionalMemberAccess] with the first test, we know the var is not None

        # Log in console
        in_dev_mode = not getattr(sys, "frozen", False)
        if in_dev_mode:
            print(msg)  # noqa: T201

        if msg_type == QtMsgType.QtFatalMsg:
            cls.__log_file.flush()  # pyright: ignore[reportOptionalMemberAccess] with the first test, we know the var is not None
            os.abort()

    # -----------------------------------------------------------------------------
    @classmethod
    def __msg_type_to_str(
        cls,
        msg_type: QtMsgType,
    ) -> Literal["DEBUG", "INFO", "WARNING", "CRITICAL", "FATAL", "UNKNOWN"]:
        match msg_type:
            case QtMsgType.QtDebugMsg:
                return "DEBUG"
            case QtMsgType.QtInfoMsg:
                return "INFO"
            case QtMsgType.QtWarningMsg:
                return "WARNING"
            case QtMsgType.QtCriticalMsg:
                return "CRITICAL"
            case QtMsgType.QtFatalMsg:
                return "FATAL"
            case _:
                return "UNKNOWN"

    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """Prevent instantiation of this utility class."""
