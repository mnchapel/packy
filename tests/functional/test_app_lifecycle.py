"""Functional tests for App lifecycle.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application

# Local application
from packy.core.app_lifecycle import AppState
from packy.core.archiver_config_model import (
    CompressionLevelLabel,
    CompressionMethodLabel,
    FormatLabel,
)
from tests.functional.qobject_inspector import capture_qobjects_state

# Third-party
import pytest
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QWidget

# Standard library
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Local application
    from packy.core.app import App
    from packy.ui.main_window import MainWindow
    from tests.conftest import QtMessageBoxMocks
    from tests.functional.conftest import SessionContext, Spies

    # Standard library
    from collections.abc import Callable


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def broken_previous_session(previous_session: SessionContext) -> SessionContext:
    """Remove the previous batch to simulate a broken previous session."""
    previous_batch = previous_session.previous_batch
    previous_batch.unlink()
    assert previous_batch.exists() is False

    return previous_session


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestAppStartup:
    """_summary_.

    See :doc:`docs/functional_test_case_scenarios` for a description of the
    scenarios.
    """

    # -------------------------------------------------------------------------
    def _arrange_startup_effect(
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        spies: Spies,
        launched_app: App,
    ) -> Callable[[], None]:
        """_summary_"""
        # Arrange
        message_box_quit_prompt_mock = qt_message_box_mocks.question
        message_box_quit_prompt_mock.return_value = QMessageBox.StandardButton.Yes

        restore_last_batch_spy = spies.main_window.restore_last_batch_spy
        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy
        close_current_batch_spy = spies.batch_workspace.close_current_batch_spy

        main_window = launched_app.main_window
        config = launched_app._config  # pyright: ignore[reportPrivateUsage]
        settings = launched_app.settings
        localization = launched_app.localization
        assert main_window is not None
        assert config is not None
        assert settings is not None
        assert localization is not None

        batch_workspace = main_window.batch_workspace

        archiver_config_panel = main_window.archiver_config_panel
        archiver_config_model = archiver_config_panel.model

        def assert_startup_effect() -> None:
            # Act/Assert - Metadata
            assert launched_app.state is AppState.RUNNING
            assert launched_app.organizationName() == "PackY"
            assert launched_app.organizationDomain() == "packy.com"
            assert launched_app.applicationName() == "PackY"
            assert launched_app.applicationDisplayName() == "PackY"
            assert launched_app.applicationVersion() == config.VERSION

            # Act/Assert - Localization
            assert localization.current_language == config.DEFAULT_LANGUAGE_CODE

            # Act/Assert - Batch Workspace
            open_last_batch_spy.assert_called_once_with(batch_workspace)
            close_current_batch_spy.assert_not_called()

            # Act/Assert - Main Window
            restore_last_batch_spy.assert_called_once_with(main_window)
            window_state = capture_qobjects_state(main_window)
            assert window_state["MainWindow"]["visible"] is True
            assert window_state["MainWindow"]["windowModified"] is False

            open_recent_actions = window_state["menu_open_recent"].as_type(QWidget).actions()
            assert len(open_recent_actions) == 2 + config.MAX_RECENT_BATCHES
            assert open_recent_actions[-2].isSeparator()
            assert open_recent_actions[-2].isEnabled() is True
            assert open_recent_actions[-2].isVisible() is True
            assert open_recent_actions[-1].text() == "Clear List"
            assert open_recent_actions[-1].isEnabled() is True
            assert open_recent_actions[-1].isVisible() is True

            # Act/Assert - Main Window / Job Queue
            assert window_state["job_queue_table_view"]["enabled"] is False
            assert window_state["remove_job_button"]["enabled"] is False
            assert window_state["save_job_button"]["enabled"] is False
            assert window_state["move_up_job_button"]["enabled"] is False
            assert window_state["move_down_job_button"]["enabled"] is False
            assert window_state["run_all_jobs_button"]["enabled"] is False
            assert window_state["cancel_jobs_button"]["enabled"] is False

            # Act/Assert - Main Window / Other Groups
            assert window_state["statistics_group"]["enabled"] is False
            assert window_state["file_selection_group"]["enabled"] is False
            assert window_state["output_group"]["enabled"] is False

            # Act/Assert - Main Window / Archiver Config Group
            assert (
                window_state["FormatGroupWidget"]["selected_button"]
                == archiver_config_model.format_label.int_value
            )
            assert (
                window_state["compression_method"]["currentIndex"]
                == archiver_config_model.compression_method_label.int_value
            )
            assert (
                window_state["compression_level"]["currentIndex"]
                == archiver_config_model.compression_level_label.int_value
            )

        return assert_startup_effect

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_startup_when_no_previous_session_exists(
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        spies: Spies,
        launched_app: App,
    ) -> None:
        """_summary_"""
        # Arrange
        assert_startup_effect = self._arrange_startup_effect(
            qt_message_box_mocks,
            spies,
            launched_app,
        )

        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy

        main_window = launched_app.main_window
        config = launched_app._config  # pyright: ignore[reportPrivateUsage]
        settings = launched_app.settings
        assert main_window is not None
        assert config is not None
        assert settings is not None

        batch_workspace = main_window.batch_workspace

        archiver_config_panel = main_window.archiver_config_panel
        archiver_config_model = archiver_config_panel.model

        # Act/Assert
        assert_startup_effect()

        # Act/Assert - Settings
        assert settings.file_path.exists() is False

        # Act/Assert - Batch Workspace
        assert batch_workspace.current_batch is None
        assert batch_workspace.batch_history == ()
        assert open_last_batch_spy.spy_return is False

        # Act/Assert - Main Window
        window_state = capture_qobjects_state(main_window)
        assert window_state["MainWindow"]["windowTitle"] == "PackY"
        assert window_state["MainWindow"]["windowFilePath"] == ""

        assert window_state["menu_open_recent"]["enabled"] is False
        open_recent_actions = window_state["menu_open_recent"].as_type(QWidget).actions()
        for recent_batch_action in open_recent_actions[:-2]:
            assert recent_batch_action.isEnabled() is False
            assert recent_batch_action.isVisible() is False

        assert window_state["action_save_batch"]["enabled"] is False
        assert window_state["action_save_batch_as"]["enabled"] is False
        assert window_state["action_close_batch"]["enabled"] is False

        # Act/Assert - Main Window / Job Queue
        assert window_state["create_job_button"]["enabled"] is False

        # Act/Assert - Main Window / Archiver Config Group
        assert window_state["archiver_config_group"]["enabled"] is False

        # Act/Assert - Archiver Config Panel
        assert archiver_config_model.current_batch is None
        assert archiver_config_model.format_label == FormatLabel.ZIP
        assert archiver_config_model.compression_method_label == CompressionMethodLabel.STORE
        assert archiver_config_model.compression_level_label == CompressionLevelLabel.NORMAL

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    def test_startup_when_previous_batch_is_found(  # noqa: PLR0915
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        previous_session: SessionContext,
        spies: Spies,
        launched_app: App,
    ) -> None:
        """_summary_"""
        # Arrange
        assert_startup_effect = self._arrange_startup_effect(
            qt_message_box_mocks,
            spies,
            launched_app,
        )
        message_box_open_last_success_mock = qt_message_box_mocks.information
        recent_batches = previous_session.recent_batches
        previous_batch = previous_session.previous_batch

        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy
        activate_batch_spy = spies.batch_workspace.activate_batch_spy
        load_batch_spy = spies.batch.load_spy

        main_window = launched_app.main_window
        config = launched_app._config  # pyright: ignore[reportPrivateUsage]
        settings = launched_app.settings
        assert main_window is not None
        assert config is not None
        assert settings is not None

        batch_workspace = main_window.batch_workspace
        current_batch = batch_workspace.current_batch

        archiver_config_panel = main_window.archiver_config_panel
        archiver_config_model = archiver_config_panel.model

        # Act/Assert
        assert_startup_effect()

        # Act/Assert - Settings
        assert settings.file_path.exists() is True

        # Act/Assert - Batch Workspace
        assert current_batch is not None
        assert current_batch.file_path == previous_batch
        assert batch_workspace.batch_history == tuple(recent_batches)
        assert open_last_batch_spy.spy_return is True

        activate_batch_spy.assert_called_once_with(batch_workspace, current_batch)
        assert activate_batch_spy.spy_return is True

        message_box_open_last_success_mock.assert_called_once()
        args = message_box_open_last_success_mock.call_args.args
        assert args[0] == main_window
        assert current_batch.display_name in args[2]

        # Act/Assert - Batch
        load_batch_spy.assert_called_once_with(previous_batch)
        assert load_batch_spy.spy_return == (current_batch, "")

        # Act/Assert - Main Window
        window_state = capture_qobjects_state(main_window)
        assert window_state["MainWindow"]["windowTitle"] == (
            f"{current_batch.display_name} - PackY"
        )
        assert window_state["MainWindow"]["windowFilePath"] == str(current_batch.file_path)

        assert window_state["menu_open_recent"]["enabled"] is True
        open_recent_actions = window_state["menu_open_recent"].as_type(QWidget).actions()
        assert open_recent_actions[0].text() == current_batch.display_name
        assert open_recent_actions[0].isEnabled() is True
        assert open_recent_actions[0].isVisible() is True
        for recent_batch_action in open_recent_actions[1:-2]:
            assert recent_batch_action.isEnabled() is False
            assert recent_batch_action.isVisible() is False

        assert window_state["action_save_batch"]["enabled"] is True
        assert window_state["action_save_batch_as"]["enabled"] is True
        assert window_state["action_close_batch"]["enabled"] is True

        # Act/Assert - Main Window / Job Queue
        assert window_state["create_job_button"]["enabled"] is True

        # Act/Assert - Main Window / Archiver Config Group
        assert window_state["archiver_config_group"]["enabled"] is True

        # Act/Assert - Archiver Config Panel
        assert archiver_config_model.current_batch is current_batch
        assert archiver_config_model.format_label.format == current_batch.archiver_format
        assert (
            archiver_config_model.compression_method_label.compression_method
            == current_batch.archiver_compression_method
        )
        assert (
            archiver_config_model.compression_level_label.compression_level
            == current_batch.archiver_compression_level
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    def test_startup_when_previous_batch_is_missing(
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        broken_previous_session: SessionContext,
        spies: Spies,
        launched_app: App,
    ) -> None:
        """_summary_"""
        # Arrange
        assert_startup_effect = self._arrange_startup_effect(
            qt_message_box_mocks,
            spies,
            launched_app,
        )
        message_box_open_failed_mock = qt_message_box_mocks.warning
        recent_batches = broken_previous_session.recent_batches
        previous_batch = broken_previous_session.previous_batch

        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy
        activate_batch_spy = spies.batch_workspace.activate_batch_spy
        load_batch_spy = spies.batch.load_spy

        main_window = launched_app.main_window
        config = launched_app._config  # pyright: ignore[reportPrivateUsage]
        settings = launched_app.settings
        assert main_window is not None
        assert config is not None
        assert settings is not None

        batch_workspace = main_window.batch_workspace

        archiver_config_panel = main_window.archiver_config_panel
        archiver_config_model = archiver_config_panel.model

        # Act/Assert
        assert_startup_effect()

        # Act/Assert - Settings
        assert settings.file_path.exists() is True

        # Act/Assert - Batch Workspace
        assert batch_workspace.current_batch is None
        assert batch_workspace.batch_history == tuple(recent_batches)
        assert open_last_batch_spy.spy_return is False

        activate_batch_spy.assert_not_called()

        message_box_open_failed_mock.assert_called_once()
        args = message_box_open_failed_mock.call_args.args
        assert args[0] == main_window
        assert previous_batch.name in args[2]

        # Act/Assert - Batch
        load_batch_spy.assert_called_once_with(previous_batch)
        load_result = load_batch_spy.spy_return
        assert load_result[0] is None
        assert str(previous_batch) in load_result[1]

        # Act/Assert - Main Window
        window_state = capture_qobjects_state(main_window)
        assert window_state["MainWindow"]["windowTitle"] == "PackY"
        assert window_state["MainWindow"]["windowFilePath"] == ""

        assert window_state["menu_open_recent"]["enabled"] is True
        open_recent_actions = window_state["menu_open_recent"].as_type(QWidget).actions()
        assert open_recent_actions[0].text() == previous_batch.name
        assert open_recent_actions[0].isEnabled() is True
        assert open_recent_actions[0].isVisible() is True
        for recent_batch_action in open_recent_actions[1:-2]:
            assert recent_batch_action.isEnabled() is False
            assert recent_batch_action.isVisible() is False

        assert window_state["action_save_batch"]["enabled"] is False
        assert window_state["action_save_batch_as"]["enabled"] is False
        assert window_state["action_close_batch"]["enabled"] is False

        # Act/Assert - Main Window / Job Queue
        assert window_state["create_job_button"]["enabled"] is False

        # Act/Assert - Main Window / Archiver Config Group
        assert window_state["archiver_config_group"]["enabled"] is False

        # Act/Assert - Archiver Config Panel
        assert archiver_config_model.current_batch is None
        assert archiver_config_model.format_label == FormatLabel.ZIP
        assert archiver_config_model.compression_method_label == CompressionMethodLabel.STORE
        assert archiver_config_model.compression_level_label == CompressionLevelLabel.NORMAL


###############################################################################
class TestAppShutdown:
    """_summary_

    See :doc:`docs/functional_test_case_scenarios` for a description of the
    scenarios.
    """

    # -------------------------------------------------------------------------
    def _act_shutdown_app(
        self,
        launched_app: App,
        main_window: MainWindow,
    ) -> None:
        """_summary_"""
        # Arrange
        window_state = capture_qobjects_state(main_window)
        action_exit = window_state["action_exit"].as_type(QAction)

        # Act
        action_exit.trigger()
        launched_app.aboutToQuit.emit()  # This call is needed to simulate an exit because exec() is mocked.  # noqa: E501

    # -------------------------------------------------------------------------
    def _arrange_shutdown_effect(
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        spies: Spies,
        launched_app: App,
    ) -> Callable[[], None]:
        """_summary_"""
        # Arrange
        message_box_quit_prompt_mock = qt_message_box_mocks.question
        message_box_quit_prompt_mock.return_value = QMessageBox.StandardButton.Yes

        close_event_spy = spies.main_window.close_event_spy
        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy
        close_current_batch_spy = spies.batch_workspace.close_current_batch_spy
        post_run_spy = spies.app.post_run_spy
        dispose_spy = spies.app.dispose_spy

        main_window = launched_app.main_window
        assert main_window is not None

        batch_workspace = main_window.batch_workspace

        def assert_shutdown_effect() -> None:
            # Assert - Main Window
            close_event_spy.assert_called_once()
            message_box_quit_prompt_mock.assert_called_once()
            window_state = capture_qobjects_state(main_window)
            assert window_state["MainWindow"]["visible"] is False

            # Assert - Batch Workspace
            assert batch_workspace.current_batch is None
            open_last_batch_spy.assert_called_once_with(batch_workspace)
            close_current_batch_spy.assert_called_once_with(batch_workspace)

            # Assert - App
            post_run_spy.assert_called_once_with(launched_app)
            dispose_spy.assert_not_called()
            assert launched_app.state is AppState.FINISHED

        return assert_shutdown_effect

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_shutdown_without_batch_loaded(
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        spies: Spies,
        launched_app: App,
    ) -> None:
        """_summary_"""
        # Arrange
        assert_shutdown_effect = self._arrange_shutdown_effect(
            qt_message_box_mocks,
            spies,
            launched_app,
        )

        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy
        close_current_batch_spy = spies.batch_workspace.close_current_batch_spy

        main_window = launched_app.main_window
        assert main_window is not None

        batch_workspace = main_window.batch_workspace
        assert batch_workspace.current_batch is None
        assert batch_workspace.batch_history == ()

        # Act
        self._act_shutdown_app(launched_app, main_window)

        # Assert
        assert_shutdown_effect()

        # Assert - Batch Workspace
        assert batch_workspace.batch_history == ()
        assert open_last_batch_spy.spy_return is False
        assert close_current_batch_spy.spy_return is True

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_shutdown_with_batch_loaded(
        self,
        qt_message_box_mocks: QtMessageBoxMocks,
        previous_session: SessionContext,
        spies: Spies,
        launched_app: App,
    ) -> None:
        """_summary_"""
        # Arrange
        assert_shutdown_effect = self._arrange_shutdown_effect(
            qt_message_box_mocks,
            spies,
            launched_app,
        )
        recent_batches = previous_session.recent_batches

        open_last_batch_spy = spies.batch_workspace.open_last_batch_spy
        close_current_batch_spy = spies.batch_workspace.close_current_batch_spy

        main_window = launched_app.main_window
        assert main_window is not None

        batch_workspace = main_window.batch_workspace
        assert batch_workspace.current_batch is not None
        assert batch_workspace.batch_history == tuple(recent_batches)

        # Act
        self._act_shutdown_app(launched_app, main_window)

        # Assert
        assert_shutdown_effect()

        # Assert - Batch Workspace
        assert batch_workspace.batch_history == tuple(recent_batches)
        assert open_last_batch_spy.spy_return is True
        assert close_current_batch_spy.spy_return is True
