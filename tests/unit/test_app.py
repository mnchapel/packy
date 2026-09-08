"""Unit tests for :class:`App`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Future library
from __future__ import annotations

# Local application
import packy.core.app as app_module
from packy.core.app import App

# Third-party
import pytest

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Local application
    from packy.core.app_config import AppConfig

    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from pathlib import Path
    from unittest.mock import MagicMock, Mock, NonCallableMagicMock


###############################################################################
### Helpers
###############################################################################
# -----------------------------------------------------------------------------
class ConfigurationError(BaseException):
    """Represent a non-Exception during configuration."""


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AppDependencyMocks:
    """Expose patched App dependency constructors and their mock instances."""

    localization_cls: Mock
    localization: Mock
    config_cls: Mock
    config: Mock
    settings_cls: Mock
    settings: Mock
    main_window_cls: Mock
    main_window: Mock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def dependency_mocks(mocker: MockerFixture, tmp_path: Path) -> AppDependencyMocks:
    """Replace App dependencies with isolated mocks for each test."""
    # Setup
    localization_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "Localization",
        autospec=True,
        spec_set=True,
    )
    localization_mock: NonCallableMagicMock = localization_cls_mock.return_value
    config_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "AppConfig",
        autospec=True,
        spec_set=True,
    )
    config_mock: NonCallableMagicMock = config_cls_mock.return_value
    settings_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "UserSettings",
        autospec=True,
        spec_set=True,
    )
    settings_mock: NonCallableMagicMock = settings_cls_mock.return_value
    settings_mock.file_path = tmp_path / "fake-file.ini"
    main_window_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "MainWindow",
        autospec=True,
        spec_set=True,
    )
    main_window_mock: NonCallableMagicMock = main_window_cls_mock.return_value

    return AppDependencyMocks(
        localization_cls=localization_cls_mock,
        localization=localization_mock,
        config_cls=config_cls_mock,
        config=config_mock,
        settings_cls=settings_cls_mock,
        settings=settings_mock,
        main_window_cls=main_window_cls_mock,
        main_window=main_window_mock,
    )


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestAppConstruction:
    """Verify the application's initial identity and uninitialized state."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_sets_identity_and_empty_settings(self, app: App) -> None:
        """Expose the expected object name and no settings before initialization."""
        # Assert
        assert app.objectName() == "App"
        assert app.settings is None


###############################################################################
class TestAppLaunch:
    """Cover lifecycle orchestration performed by App.launch."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    def test_success_returns_run_exit_code_and_disposes(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Successful launch returns the run result and disposes the application."""
        # Arrange
        config = mocker.sentinel.config
        app_config_cls_mock = mocker.patch.object(
            app_module,
            "AppConfig",
            autospec=True,
            spec_set=True,
            return_value=config,
        )
        app_mock = mocker.create_autospec(
            App,
            instance=True,
            spec_set=True,
        )
        app_mock.run.return_value = 2

        # Act
        exit_code = App.launch(app_mock)

        # Assert
        assert exit_code == 2
        app_config_cls_mock.assert_called_once_with()
        assert app_mock.method_calls == [
            mocker.call.initialize(config),
            mocker.call.run(),
            mocker.call.dispose(),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    def test_configuration_error_propagates_runtime_error_after_disposal(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A configuration construction error propagates while disposal still occurs."""
        # Arrange
        error = ConfigurationError("Configuration failed")
        app_config_cls_mock = mocker.patch.object(
            app_module,
            "AppConfig",
            autospec=True,
            spec_set=True,
            side_effect=error,
        )
        app_mock = mocker.create_autospec(
            App,
            instance=True,
            spec_set=True,
        )

        # Act / Assert
        with pytest.raises(ConfigurationError) as exc_info:
            App.launch(app_mock)

        assert exc_info.value is error
        app_config_cls_mock.assert_called_once_with()
        app_mock.dispose.assert_called_once_with()
        app_mock.initialize.assert_not_called()
        app_mock.run.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    def test_initialization_error_propagates_runtime_error_after_disposal(
        self,
        mocker: MockerFixture,
    ) -> None:
        """An initialization error propagates while disposal still occurs."""
        # Arrange
        config = mocker.sentinel.config
        app_config_cls_mock = mocker.patch.object(
            app_module,
            "AppConfig",
            autospec=True,
            spec_set=True,
            return_value=config,
        )
        app_mock = mocker.create_autospec(
            App,
            instance=True,
            spec_set=True,
        )
        app_mock.initialize.side_effect = RuntimeError("Initialization failed")

        # Act / Assert
        with pytest.raises(RuntimeError, match="Initialization failed"):
            App.launch(app_mock)

        app_config_cls_mock.assert_called_once_with()
        assert app_mock.method_calls == [
            mocker.call.initialize(config),
            mocker.call.dispose(),
        ]
        app_mock.run.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    def test_execution_error_propagates_runtime_error_after_disposal(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A run exception propagates while disposal still occurs."""
        # Arrange
        config = mocker.sentinel.config
        mocker.patch.object(
            app_module,
            "AppConfig",
            autospec=True,
            spec_set=True,
            return_value=config,
        )
        app_mock = mocker.create_autospec(
            App,
            instance=True,
            spec_set=True,
        )
        app_mock.run.side_effect = RuntimeError("Execution failed")

        # Act / Assert
        with pytest.raises(RuntimeError, match="Execution failed"):
            App.launch(app_mock)

        assert app_mock.method_calls == [
            mocker.call.initialize(config),
            mocker.call.run(),
            mocker.call.dispose(),
        ]


###############################################################################
class TestAppInitialize:
    """Cover application initialization and its lifecycle guard."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_valid_config_initializes_metadata_services_and_settings(
        self,
        dependency_mocks: AppDependencyMocks,
        app: App,
        app_config: AppConfig,
    ) -> None:
        """A valid configuration initializes Qt metadata and PackY services."""
        # Act
        app.initialize(app_config)

        # Assert - Metadata
        assert app.is_initialized is True
        assert app.organizationName() == "PackY"
        assert app.organizationDomain() == "packy.com"
        assert app.applicationName() == "PackY"
        assert app.applicationDisplayName() == "PackY"
        assert app.applicationVersion() == app_config.VERSION

        # Assert - Localization
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )

        # Assert - Configuration
        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]

        # Assert - Settings
        dependency_mocks.settings_cls.assert_called_once_with(app)
        assert app.settings is dependency_mocks.settings

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_second_initialization_raises_runtime_error_without_replacing_settings(
        self,
        dependency_mocks: AppDependencyMocks,
        app: App,
        app_config: AppConfig,
    ) -> None:
        """Reinitializing an initialized application is rejected without replacing settings."""
        # Arrange
        app.initialize(app_config)

        # Act / Assert
        with pytest.raises(RuntimeError, match="Application already initialized"):
            app.initialize(app_config)

        assert app.is_initialized is True
        dependency_mocks.localization_cls.assert_called_once_with()
        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]
        dependency_mocks.settings_cls.assert_called_once_with(app)


###############################################################################
class TestAppRun:
    """Cover event-loop entry and its initialization prerequisite."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_initialized_app_restores_window_and_returns_event_loop_exit_code(
        self,
        dependency_mocks: AppDependencyMocks,
        initialized_app: App,
        app_config: AppConfig,
        mocker: MockerFixture,
    ) -> None:
        """Running an initialized application restores and shows its window before returning."""
        # Arrange
        app_exec_mock = mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )
        call_stack_mock = mocker.Mock(name="call_stack_mock")
        call_stack_mock.attach_mock(
            dependency_mocks.main_window_cls,
            "main_window_cls",
        )
        call_stack_mock.attach_mock(
            dependency_mocks.main_window,
            "main_window",
        )
        call_stack_mock.attach_mock(app_exec_mock, "exec")

        # Act
        exit_code = initialized_app.run()

        # Assert
        assert exit_code == 2
        assert initialized_app.main_window is dependency_mocks.main_window
        assert call_stack_mock.mock_calls == [
            mocker.call.main_window_cls(
                app_config,
                initialized_app.settings,
            ),
            mocker.call.main_window.load_settings(),
            mocker.call.main_window.show(),
            mocker.call.main_window.restore_last_batch(),
            mocker.call.exec(),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_run_before_initialization_raises_runtime_error(
        self,
        app: App,
    ) -> None:
        """Running before initialization is rejected with the documented lifecycle error."""
        # Act / Assert
        with pytest.raises(RuntimeError, match="Application is not initialized"):
            app.run()
        assert app.is_initialized is False


###############################################################################
class TestAppShutdown:
    """Cover settings persistence triggered by the Qt shutdown lifecycle."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_about_to_quit_after_run_saves_main_window_settings(
        self,
        dependency_mocks: AppDependencyMocks,
        initialized_app: App,
        mocker: MockerFixture,
        qtbot: QtBot,
    ) -> None:
        """The Qt quit signal saves settings when the application has a main window."""
        # Arrange
        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=0,
        )
        exit_code = initialized_app.run()

        assert initialized_app.main_window is dependency_mocks.main_window

        # Act
        with qtbot.waitSignal(initialized_app.aboutToQuit):
            initialized_app.aboutToQuit.emit()

        # Assert
        assert exit_code == 0
        dependency_mocks.main_window.save_settings.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_branch
    def test_about_to_quit_before_run_preserves_empty_window_state(
        self,
        initialized_app: App,
    ) -> None:
        """The Qt quit signal is safe when no main window has been created."""
        # Arrange
        assert initialized_app.main_window is None

        # Act
        initialized_app.aboutToQuit.emit()

        # Assert
        assert initialized_app.main_window is None


###############################################################################
class TestAppDispose:
    """Cover disposal from initialized and running application states."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_with_main_window_closes_window_and_clears_public_state(
        self,
        dependency_mocks: AppDependencyMocks,
        initialized_app: App,
        mocker: MockerFixture,
    ) -> None:
        """Disposal after running closes the window and clears exposed lifecycle state."""
        # Arrange
        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )
        initialized_app.run()

        # Act
        initialized_app.dispose()

        # Assert
        dependency_mocks.main_window.close.assert_called_once_with()
        assert initialized_app.main_window is None
        assert initialized_app.settings is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_without_main_window_resets_state_and_allows_reinitialization(
        self,
        initialized_app: App,
        app_config: AppConfig,
    ) -> None:
        """Disposal before running clears public state and permits initialization again."""
        # Act
        initialized_app.dispose()

        # Assert
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

        # Act
        initialized_app.initialize(app_config)

        # Assert
        assert initialized_app.settings is not None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_repeated_disposal_allows_reinitialization(
        self,
        dependency_mocks: AppDependencyMocks,
        initialized_app: App,
        app_config: AppConfig,
    ) -> None:
        """Repeated disposal leaves the application eligible for initialization again."""
        # Act
        initialized_app.dispose()
        initialized_app.dispose()
        initialized_app.initialize(app_config)

        # Assert
        assert initialized_app.main_window is None
        assert initialized_app.settings is dependency_mocks.settings

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_disposal_closes_resources_and_allows_reinitialization(
        self,
        dependency_mocks: AppDependencyMocks,
        initialized_app: App,
        app_config: AppConfig,
        mocker: MockerFixture,
    ) -> None:
        """Disposal closes the running window and leaves the app eligible for initialization."""
        # Arrange
        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )
        initialized_app.run()

        # Act
        initialized_app.dispose()

        # Assert
        dependency_mocks.main_window.close.assert_called_once_with()
        assert initialized_app.main_window is None
        assert initialized_app.settings is None

        # Arrange
        localization_calls_before = dependency_mocks.localization_cls.call_count
        settings_calls_before = dependency_mocks.settings_cls.call_count

        # Act
        initialized_app.initialize(app_config)

        # Assert
        assert dependency_mocks.localization_cls.call_count == localization_calls_before + 1
        assert dependency_mocks.settings_cls.call_count == settings_calls_before + 1
        assert initialized_app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.main_window is None
        assert initialized_app.settings is dependency_mocks.settings
