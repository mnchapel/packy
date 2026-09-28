"""Fixtures shared by the test suite.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.constants.settings_keys import WorkspaceSettings
from packy.core.app import App
from packy.core.app_lifecycle import AppLifecycle, AppState
from packy.core.batch import Batch
from packy.core.batch_workspace import Batch, BatchWorkspace
from packy.core.logger import Logger
from packy.ui.main_window import MainWindow
from tests.unit.test_batch_workspace import (
    batch_workspace_dialogs_mocks,  # pyright: ignore[reportUnusedImport] # noqa: F401 Fixture for tests
)

# Third-party
import pytest
from PySide6 import QtCore
from PySide6.QtCore import QSettings

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Local application
    from packy.core.app_config import AppConfig

    # Third-party
    from PySide6.QtWidgets import QApplication
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from collections.abc import Generator
    from pathlib import Path
    from unittest.mock import MagicMock


###############################################################################
### Test Contexts
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class SessionContext:
    """_summary_"""

    recent_batches: list[Path]
    previous_batch: Path


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class Spies:
    """_summary_"""

    app: AppSpies
    main_window: MainWindowSpies
    batch_workspace: BatchWorkspaceSpies
    batch: BatchSpies


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AppSpies:
    """_summary_"""

    initialize_spy: MagicMock
    run_spy: MagicMock
    post_run_spy: MagicMock
    dispose_spy: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class MainWindowSpies:
    """_summary_"""

    restore_last_batch_spy: MagicMock
    new_batch_spy: MagicMock
    open_batch_spy: MagicMock
    open_recent_batch_spy: MagicMock
    save_batch_spy: MagicMock
    save_as_batch_spy: MagicMock
    close_batch_spy: MagicMock
    close_event_spy: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class BatchWorkspaceSpies:
    """_summary_"""

    create_batch_spy: MagicMock
    open_last_batch_spy: MagicMock
    open_recent_batch_spy: MagicMock
    open_batch_spy: MagicMock
    activate_batch_spy: MagicMock
    save_current_batch_spy: MagicMock
    save_current_batch_as_spy: MagicMock
    close_current_batch_spy: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class BatchSpies:
    """_summary_"""

    batch_spy: MagicMock
    save_spy: MagicMock
    load_spy: MagicMock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def launched_app(
    qapp: QApplication,
    app_config: AppConfig,
    mocker: MockerFixture,
    qtbot: QtBot,
    spies: Spies,  # noqa: ARG001 needed as dependency
) -> Generator[App]:
    """Run a fully initialized application with a logger and a main window."""
    # Setup
    assert isinstance(qapp, App)
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
        assert qapp.state is AppState.CREATED
        qapp.initialize(app_config)
        exit_code = qapp.run()
        assert qapp.state is AppState.RUNNING
        assert exit_code == 0
        app_exec_mock.assert_called_once_with()

        assert qapp.main_window is not None
        qtbot.waitUntil(qapp.main_window.isVisible)

        yield qapp
    finally:
        # Teardown
        if qapp.state is AppState.RUNNING:
            assert qapp.main_window is not None
            qapp.main_window.close()
            qapp.aboutToQuit.emit()  # It simulates a user pressing the close button to trigger QApplication.exit(), then call app.post_run() and the FINISH transition
            assert qapp.state is AppState.FINISHED
        qapp.dispose()
        has_stopped = Logger.stop()
        if not has_stopped:
            QtCore.qWarning("Debug logger cannot be stopped!")
            pytest.fail("Debug logger cannot be stopped")

        assert qapp.state is AppState.DISPOSED
        qapp._lifecycle = AppLifecycle()  # pyright: ignore[reportAttributeAccessIssue, reportPrivateUsage] Forces the app to be in the first state to be in a fresh state for the next tests.


# -----------------------------------------------------------------------------
@pytest.fixture
def previous_session(tmp_path: Path) -> SessionContext:
    """_summary_"""
    # Setup
    batch_path = (tmp_path / "default-batch.json").resolve()
    batch = Batch(batch_path)
    batch.save()
    assert batch_path.exists() is True

    recent_batches: list[Path] = []
    recent_batches.insert(0, batch.file_path)

    settings = QSettings()
    settings.beginGroup(WorkspaceSettings.SETTINGS_GROUP)
    settings.setValue(
        WorkspaceSettings.RECENT_BATCHES,
        recent_batches,
    )
    settings.endGroup()

    return SessionContext(
        recent_batches=recent_batches,
        previous_batch=batch.file_path,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def spies(mocker: MockerFixture) -> Spies:
    """_summary_"""
    return Spies(
        app=AppSpies(
            initialize_spy=mocker.spy(App, "initialize"),
            run_spy=mocker.spy(App, "run"),
            post_run_spy=mocker.spy(App, "post_run"),
            dispose_spy=mocker.spy(App, "dispose"),
        ),
        main_window=MainWindowSpies(
            restore_last_batch_spy=mocker.spy(MainWindow, "restore_last_batch"),
            new_batch_spy=mocker.spy(MainWindow, "_new_batch"),
            open_batch_spy=mocker.spy(MainWindow, "_open_batch"),
            open_recent_batch_spy=mocker.spy(MainWindow, "_open_recent_batch"),
            save_batch_spy=mocker.spy(MainWindow, "_save_batch"),
            save_as_batch_spy=mocker.spy(MainWindow, "_save_batch_as"),
            close_batch_spy=mocker.spy(MainWindow, "_close_batch"),
            close_event_spy=mocker.spy(MainWindow, "closeEvent"),
        ),
        batch_workspace=BatchWorkspaceSpies(
            create_batch_spy=mocker.spy(BatchWorkspace, "create_batch"),
            open_last_batch_spy=mocker.spy(BatchWorkspace, "open_last_batch"),
            open_recent_batch_spy=mocker.spy(BatchWorkspace, "open_recent_batch"),
            open_batch_spy=mocker.spy(BatchWorkspace, "open_batch"),
            activate_batch_spy=mocker.spy(BatchWorkspace, "activate_batch"),
            save_current_batch_spy=mocker.spy(BatchWorkspace, "save_current_batch"),
            save_current_batch_as_spy=mocker.spy(BatchWorkspace, "save_current_batch_as"),
            close_current_batch_spy=mocker.spy(BatchWorkspace, "close_current_batch"),
        ),
        batch=BatchSpies(
            batch_spy=mocker.spy(Batch, "__init__"),
            save_spy=mocker.spy(Batch, "save"),
            load_spy=mocker.spy(Batch, "load"),
        ),
    )
