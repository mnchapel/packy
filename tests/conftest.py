"""Fixtures shared by the test suite.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
import packy.core.app as app_module
from packy.core.app import App
from packy.core.app_config import AppConfig
from packy.core.logger import Logger

# Third-party
import pytest
from PySide6 import QtCore
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from collections.abc import Generator
    from pathlib import Path
    from unittest.mock import MagicMock


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class QtFileDialogMocks:
    """Expose blocking native file dialogs patched for tests."""

    get_save_file_name: MagicMock
    get_open_file_name: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class QtMessageBoxMocks:
    """Expose blocking message-box operations patched for tests."""

    critical: MagicMock
    information: MagicMock
    question: MagicMock
    warning: MagicMock
    exec: MagicMock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def qapp_args() -> list[str]:
    """Provide arguments for the unique QApplication instance."""
    return []


# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def qapp_cls() -> type[App]:
    """Use PackY's custom QApplication class in pytest-qt."""
    return App


# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def isolate_qsettings(tmp_path: Path) -> None:
    """Use distinct QSettings storage for each test."""
    user_directory: Path = tmp_path / "settings_user"
    system_directory: Path = tmp_path / "settings_system"

    user_directory.mkdir()
    system_directory.mkdir()

    QApplication.setOrganizationName("PackY")
    QApplication.setApplicationName("PackY")

    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        str(user_directory),
    )
    QSettings.setPath(
        QSettings.Format.IniFormat,
        QSettings.Scope.SystemScope,
        str(system_directory),
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def app(qapp: QApplication) -> Generator[App]:
    """Provide a clean PackY application and restore clean lifecycle state afterward."""
    # Setup
    assert isinstance(qapp, App)

    try:
        assert qapp.state is AppState.CREATED
        yield qapp
    finally:
        # Teardown
        if qapp.state is AppState.RUNNING:
            qapp.post_run()
            assert qapp.state is AppState.FINISHED

        qapp.dispose()
        assert qapp.state is AppState.DISPOSED
        qapp._lifecycle._state = AppState.CREATED # pyright: ignore[reportPrivateUsage] Forces the app to be in the first state to restore it to its initial state.

# -----------------------------------------------------------------------------
@pytest.fixture
def app_config(mocker: MockerFixture, tmp_path: Path) -> AppConfig:
    """Provide the default application configuration test double."""
    log_path = tmp_path / "app.log"
    mocker.patch.object(
        AppConfig,
        "_determine_log_path",
        autospec=True,
        return_value=log_path,
    )
    return AppConfig(
        DEFAULT_LANGUAGE_CODE="en-US",
        MAX_RECENT_BATCHES=3,
        VERSION="1.2.3",
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def initialized_app(
    app: App,
    app_config: AppConfig,
) -> App:
    """Provide an initialized PackY application."""
    app.initialize(app_config)
    assert app.state is AppState.INITIALIZED
    return app


# -----------------------------------------------------------------------------
@pytest.fixture
def launched_app(
    qapp: QApplication,
    app_config: AppConfig,
    mocker: MockerFixture,
    qtbot: QtBot,
) -> Generator[App]:
    """Run a fully initialized application with a logger and a main window."""
    # Setup
    assert isinstance(qapp, App)
    mocker.patch.object(
        app_module,
        "AppConfig",
        autospec=True,
        spec_set=True,
        return_value=app_config,
    )
    app_exec_mock: MagicMock = mocker.patch.object(
        qapp,
        "exec",
        autospec=True,
        return_value=0,
    )

    try:
        # Initialize logging
        has_started = Logger.start(app_config.LOG_FILE_PATH)
        if not has_started:
            QtCore.qWarning("Debug logger cannot be started!")
            pytest.fail("Debug logger cannot be started")

        # Launch application
        qapp.dispose()
        qapp.initialize(app_config)
        exit_code = qapp.run()
        assert exit_code == 0
        app_exec_mock.assert_called_once_with()

        window = qapp.main_window
        assert window is not None
        qtbot.waitUntil(window.isVisible)

        yield qapp
    finally:
        # Teardown
        qapp.dispose()
        has_stopped = Logger.stop()
        if not has_stopped:
            QtCore.qWarning("Debug logger cannot be stopped!")
            pytest.fail("Debug logger cannot be stopped")


# -----------------------------------------------------------------------------
@pytest.fixture
def qt_file_dialog_mocks(mocker: MockerFixture) -> QtFileDialogMocks:
    """Patch blocking native file dialogs with canceled responses by default."""
    # Setup
    get_save_file_name_mock: MagicMock = mocker.patch.object(
        QFileDialog,
        "getSaveFileName",
        autospec=True,
        return_value=("", ""),
    )
    get_open_file_name_mock: MagicMock = mocker.patch.object(
        QFileDialog,
        "getOpenFileName",
        autospec=True,
        return_value=("", ""),
    )

    return QtFileDialogMocks(
        get_save_file_name=get_save_file_name_mock,
        get_open_file_name=get_open_file_name_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def qt_message_box_mocks(mocker: MockerFixture) -> QtMessageBoxMocks:
    """Patch only blocking QMessageBox operations while keeping real Qt widgets."""
    # Setup
    message_box_types: Final[tuple[str, ...]] = (
        "critical",
        "information",
        "question",
        "warning",
        "exec",
    )
    mocks = {
        box_type: mocker.patch.object(
            QMessageBox,
            box_type,
            autospec=True,
        )
        for box_type in message_box_types
    }

    return QtMessageBoxMocks(**mocks)
