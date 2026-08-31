"""Unit tests for :class:`Logger`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Future library
from __future__ import annotations

# Local application
import packy.core.logger as logger_module
from packy.core.logger import Logger

# Third-party
import pytest
from PySide6 import QtCore
from PySide6.QtCore import QtMsgType

# Standard library
from io import TextIOBase
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture

    # Standard library
    from collections.abc import Generator
    from unittest.mock import MagicMock, Mock


###############################################################################
### Helpers
###############################################################################
# -----------------------------------------------------------------------------
class HandlerInstallationAbort(BaseException):
    """Represent a non-Exception abort during Qt handler installation."""


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def qt_install_message_handler(mocker: MockerFixture) -> Generator[Mock]:
    """Isolate Qt's process-wide handler and restore clean Logger state."""
    # Setup
    previous_handler = mocker.sentinel.previous_handler
    message_handler_mock: MagicMock = mocker.patch.object(
        logger_module,
        "qInstallMessageHandler",
        autospec=True,
        return_value=previous_handler,
    )

    Logger.stop()
    message_handler_mock.reset_mock()

    yield message_handler_mock

    # Teardown
    message_handler_mock.side_effect = None
    message_handler_mock.return_value = mocker.sentinel.previous_handler
    Logger.stop()


# -----------------------------------------------------------------------------
@pytest.fixture
def message_context(mocker: MockerFixture) -> Mock:
    """Provide stable Qt source metadata consumed only as message data."""
    return mocker.Mock(
        name="message_context",
        spec=QtCore.QMessageLogContext,
        file="worker.py",
        line=24,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def fixed_runtime(mocker: MockerFixture) -> str:
    """Provide deterministic timestamp, process, and Qt thread log metadata."""
    timestamp = "2026-08-05T12:34:56.789+02:00"
    process_id = 731
    thread = mocker.sentinel.qt_thread

    date_time_cls_mock: MagicMock = mocker.patch.object(logger_module, "QDateTime")
    date_time_cls_mock.currentDateTime.return_value.toString.return_value = timestamp
    mocker.patch.object(
        logger_module.os,
        "getpid",
        autospec=True,
        return_value=process_id,
    )
    qt_thread_cls_mock: MagicMock = mocker.patch.object(
        logger_module,
        "QThread",
        autospec=True,
        spec_set=True,
    )
    qt_thread_cls_mock.currentThread.return_value = thread

    return f"[{timestamp}][{process_id},0x{id(thread):x}]"


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestLoggerConstruction:
    """Cover Logger construction and its effect on logging state."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_construction_does_not_activate_logging(
        self,
        qt_install_message_handler: Mock,
    ) -> None:
        """Constructing Logger leaves its process-wide logging state inactive."""
        # Act
        logger = Logger()

        # Assert
        assert isinstance(logger, Logger)
        assert Logger.is_active() is False
        qt_install_message_handler.assert_not_called()


###############################################################################
class TestLoggerStart:
    """Cover Logger startup, repeated activation, and failure cleanup."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_activates_logging_and_installs_the_handler(
        self,
        qt_install_message_handler: Mock,
        tmp_path: Path,
    ) -> None:
        """Starting should open logging and preserve the prior Qt handler."""
        # Arrange
        log_path = tmp_path / "application.log"

        # Act
        started = Logger.start(log_path)

        # Assert
        assert started is True
        assert Logger.is_active() is True
        assert log_path.exists()
        qt_install_message_handler.assert_called_once_with(Logger.q_message_handler)

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    def test_preserves_existing_log_content(
        self,
        tmp_path: Path,
    ) -> None:
        """Starting with an existing file preserves its previous UTF-8 content."""
        # Arrange
        log_path = tmp_path / "application.log"
        existing_content = "existing café entry\n"
        log_path.write_text(
            existing_content,
            encoding="utf-8",
        )

        # Act
        started = Logger.start(log_path)
        stopped = Logger.stop()

        # Assert
        assert started is True
        assert stopped is True
        assert log_path.read_text(encoding="utf-8") == existing_content

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_when_already_active_returns_false_without_reinstalling_handler(
        self,
        qt_install_message_handler: Mock,
        tmp_path: Path,
    ) -> None:
        """A repeated start keeps the existing destination and handler active."""
        # Arrange
        first_path = tmp_path / "first.log"
        second_path = tmp_path / "second.log"
        assert Logger.start(first_path) is True

        # Act
        started = Logger.start(second_path)

        # Assert
        assert started is False
        assert Logger.is_active() is True
        assert second_path.exists() is False
        qt_install_message_handler.assert_called_once_with(
            Logger.q_message_handler,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_equivalence_partitioning
    def test_with_unopenable_path_raises_oserror(
        self,
        qt_install_message_handler: Mock,
        tmp_path: Path,
    ) -> None:
        """An unopenable log path raises OSError without activating logging."""
        # Arrange
        log_path = tmp_path / "missing" / "application.log"

        # Act / Assert
        with pytest.raises(FileNotFoundError):
            Logger.start(log_path)

        assert Logger.is_active() is False
        qt_install_message_handler.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_branch
    def test_cleans_up_before_propagating_base_exception(
        self,
        qt_install_message_handler: Mock,
        mocker: MockerFixture,
    ) -> None:
        """A handler-install abort closes the opened file before propagating."""
        # Arrange
        log_path_mock = mocker.create_autospec(
            Path,
            instance=True,
            spec_set=True,
        )
        log_file_mock = mocker.create_autospec(
            TextIOBase,
            instance=True,
            spec_set=True,
        )
        log_path_mock.open.return_value = log_file_mock

        interruption = HandlerInstallationAbort()
        qt_install_message_handler.side_effect = interruption

        # Act / Assert
        with pytest.raises(HandlerInstallationAbort) as exc_info:
            Logger.start(log_path_mock)

        assert exc_info.value is interruption
        assert Logger.is_active() is False
        log_path_mock.open.assert_called_once_with(
            mode="a",
            buffering=1,
            encoding="utf-8",
        )
        log_file_mock.close.assert_called_once_with()


###############################################################################
class TestLoggerStop:
    """Cover Logger shutdown, handler restoration, and inactive-state behavior."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_restores_previous_handler_before_closing_file(
        self,
        qt_install_message_handler: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Stopping should restore the previous Qt handler before closing the log."""
        # Arrange
        log_path_mock = mocker.create_autospec(
            Path,
            instance=True,
            spec_set=True,
        )
        log_file_mock = mocker.create_autospec(
            TextIOBase,
            instance=True,
            spec_set=True,
        )
        previous_handler = mocker.sentinel.previous_handler

        log_path_mock.open.return_value = log_file_mock
        qt_install_message_handler.return_value = previous_handler
        assert Logger.start(log_path_mock) is True

        call_stack_mock = mocker.Mock(name="call_stack_mock")
        call_stack_mock.attach_mock(qt_install_message_handler, "install")
        call_stack_mock.attach_mock(log_file_mock, "log_file")

        # Act
        stopped = Logger.stop()

        # Assert
        assert stopped is True
        assert Logger.is_active() is False
        assert call_stack_mock.mock_calls == [
            mocker.call.install(previous_handler),
            mocker.call.log_file.close(),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_when_inactive_returns_false_without_restoring_handler(
        self,
        qt_install_message_handler: Mock,
    ) -> None:
        """Stopping while inactive is a side-effect-free no-op."""
        # Arrange
        assert Logger.is_active() is False

        # Act
        stopped = Logger.stop()

        # Assert
        assert stopped is False
        assert Logger.is_active() is False
        qt_install_message_handler.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_branch
    def test_cleans_up_before_propagating_base_exception(
        self,
        qt_install_message_handler: Mock,
        mocker: MockerFixture,
    ) -> None:
        """A handler-restoration abort cleans up logging before propagating."""
        # Arrange
        log_path_mock = mocker.create_autospec(
            Path,
            instance=True,
            spec_set=True,
        )
        log_file_mock = mocker.create_autospec(
            TextIOBase,
            instance=True,
            spec_set=True,
        )
        log_path_mock.open.return_value = log_file_mock

        assert Logger.start(log_path_mock) is True

        qt_install_message_handler.reset_mock()
        interruption = HandlerInstallationAbort()
        qt_install_message_handler.side_effect = interruption

        # Act / Assert
        with pytest.raises(HandlerInstallationAbort) as exc_info:
            Logger.stop()

        assert exc_info.value is interruption
        assert Logger.is_active() is False
        log_file_mock.close.assert_called_once_with()
        qt_install_message_handler.assert_called_once_with(
            mocker.sentinel.previous_handler,
        )


###############################################################################
class TestLoggerMessageHandler:
    """Cover message formatting, output routing, severity, and fatal flushing."""

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        ("msg_type", "expected_level"),
        [
            pytest.param(
                QtMsgType.QtDebugMsg,
                "DEBUG",
                id="debug",
                marks=[
                    pytest.mark.scenario_happy_path,
                    pytest.mark.technique_branch,
                ],
            ),
            pytest.param(
                QtMsgType.QtInfoMsg,
                "INFO",
                id="info",
                marks=[
                    pytest.mark.scenario_alternate_path,
                    pytest.mark.technique_branch,
                ],
            ),
            pytest.param(
                QtMsgType.QtWarningMsg,
                "WARNING",
                id="warning",
                marks=[
                    pytest.mark.scenario_alternate_path,
                    pytest.mark.technique_branch,
                ],
            ),
            pytest.param(
                QtMsgType.QtCriticalMsg,
                "CRITICAL",
                id="critical",
                marks=[
                    pytest.mark.scenario_alternate_path,
                    pytest.mark.technique_branch,
                ],
            ),
        ],
    )
    def test_writes_exact_file_and_console_entry(  # noqa: PLR0913, PLR0917
        self,
        message_context: Mock,
        fixed_runtime: str,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        msg_type: QtMsgType,
        expected_level: str,
    ) -> None:
        """Each non-fatal Qt severity produces its exact UTF-8 log entry."""
        # Arrange
        log_path = tmp_path / "application.log"
        message = "test ready"

        log_path.write_text("existing entry\n", encoding="utf-8")
        monkeypatch.delattr(
            logger_module.sys,
            "frozen",
            raising=False,
        )  # force development mode for _log_message

        assert Logger.start(log_path) is True

        expected = (
            f"{fixed_runtime}"
            f"[{message_context.file}:{message_context.line}]"
            f"[{expected_level}]: {message}"
        )

        # Act
        Logger.q_message_handler(
            msg_type,
            message_context,
            message,
        )
        stopped = Logger.stop()
        captured = capsys.readouterr()

        # Assert
        assert stopped is True
        assert log_path.read_text(encoding="utf-8") == f"existing entry\n{expected}\n"
        assert captured.out == f"{expected}\n"
        assert captured.err == ""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_branch
    def test_fatal_message_is_written_and_flushed(
        self,
        message_context: Mock,
        fixed_runtime: str,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A fatal message is written as FATAL and explicitly flushed."""
        # Arrange
        log_path_mock = mocker.create_autospec(
            Path,
            instance=True,
            spec_set=True,
        )
        log_file_mock = mocker.create_autospec(
            TextIOBase,
            instance=True,
            spec_set=True,
        )
        log_path_mock.open.return_value = log_file_mock

        monkeypatch.delattr(
            logger_module.sys,
            "frozen",
            raising=False,
        )  # force development mode for _log_message

        assert Logger.start(log_path_mock) is True

        expected = (
            f"{fixed_runtime}[{message_context.file}:{message_context.line}][FATAL]: unrecoverable"
        )

        # Act
        Logger.q_message_handler(
            QtMsgType.QtFatalMsg,
            message_context,
            "unrecoverable",
        )
        stopped = Logger.stop()
        captured = capsys.readouterr()

        # Assert
        assert stopped is True
        log_file_mock.write.assert_called_once_with(f"{expected}\n")
        log_file_mock.flush.assert_called_once_with()
        assert captured.out == f"{expected}\n"
        assert captured.err == ""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_branch
    @pytest.mark.usefixtures("fixed_runtime")
    def test_while_inactive_emits_no_output(
        self,
        qt_install_message_handler: Mock,
        message_context: Mock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """A message received while inactive produces no logging output."""
        # Act
        Logger.q_message_handler(
            QtMsgType.QtInfoMsg,
            message_context,
            "ignored",
        )
        captured = capsys.readouterr()

        # Assert
        assert Logger.is_active() is False
        assert captured.out == ""
        assert captured.err == ""
        qt_install_message_handler.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_branch
    def test_in_non_dev_mode_writes_only_to_file(
        self,
        message_context: Mock,
        fixed_runtime: str,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Frozen mode preserves file output while suppressing stdout."""
        # Arrange
        log_path = tmp_path / "application.log"

        monkeypatch.setattr(
            logger_module.sys,
            "frozen",
            True,
            raising=False,
        )  # force non-development mode for _log_message

        assert Logger.start(log_path) is True

        expected = f"{fixed_runtime}[{message_context.file}:{message_context.line}][INFO]: packaged"

        # Act
        Logger.q_message_handler(
            QtMsgType.QtInfoMsg,
            message_context,
            "packaged",
        )
        stopped = Logger.stop()
        captured = capsys.readouterr()

        # Assert
        assert stopped is True
        assert log_path.read_text(encoding="utf-8") == f"{expected}\n"
        assert captured.out == ""
        assert captured.err == ""
