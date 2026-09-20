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
from packy.core.app_lifecycle import (
    AppLifecycle,
    AppState,
    LifecycleTransitionNotAllowedError,
    Transition,
)

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
    from collections.abc import Generator
    from pathlib import Path
    from unittest.mock import MagicMock, Mock, NonCallableMagicMock


###############################################################################
### Helpers
###############################################################################
# -----------------------------------------------------------------------------
def reset_lifecycle_mock_calls(context: AppContext) -> None:
    """Clear lifecycle interaction history without changing configured behavior."""
    context.lifecycle_mock.transition.reset_mock()


###############################################################################
### Test Contexts
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AppContext:
    """Expose an application with its isolated lifecycle dependency."""

    app: App
    lifecycle_mock: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class InitializedAppContext:
    """Expose an initialized application and its isolated dependencies."""

    app_context: AppContext
    app_config: AppConfig
    dependency_mocks: AppDependencyMocks


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
class ConfigurationError(BaseException):
    """Represent a configuration failure outside the Exception hierarchy."""


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AppDependencyMocks:
    """Expose patched App dependency constructors and their mock instances."""

    localization_cls: Mock
    localization: Mock
    settings_cls: Mock
    settings: Mock
    main_window_cls: Mock
    main_window: Mock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def app_context(
    app: App,
    mocker: MockerFixture,
) -> Generator[AppContext]:
    """Replace the shared application's real lifecycle with an isolated mock."""
    # Setup
    lifecycle_mock: NonCallableMagicMock = mocker.create_autospec(
        AppLifecycle,
        instance=True,
        spec_set=True,
    )
    transition_mock: MagicMock = mocker.MagicMock(
        name="app_lifecycle_transition",
    )
    transition_mock.__exit__.return_value = False

    lifecycle_mock.state = AppState.CREATED
    lifecycle_mock.transition.return_value = transition_mock

    mocker.patch.object(
        app,
        "_lifecycle",
        lifecycle_mock,
    )

    try:
        yield AppContext(
            app=app,
            lifecycle_mock=lifecycle_mock,
        )
    finally:
        # Teardown
        lifecycle_mock.state = AppState.DISPOSED
        lifecycle_mock.transition.side_effect = None


# -----------------------------------------------------------------------------
@pytest.fixture
def dependency_mocks(mocker: MockerFixture, tmp_path: Path) -> AppDependencyMocks:
    """Replace App dependencies with isolated mocks."""
    # Setup
    localization_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "Localization",
        autospec=True,
        spec_set=True,
    )
    localization_mock: NonCallableMagicMock = localization_cls_mock.return_value

    settings_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "UserSettings",
        autospec=True,
        spec_set=True,
    )
    settings_mock: NonCallableMagicMock = settings_cls_mock.return_value
    settings_mock.file_path = tmp_path / "fake-settings.ini"

    main_window_cls_mock: MagicMock = mocker.patch.object(
        app_module,
        "MainWindow",
        autospec=True,
        spec_set=True,
    )
    main_window_mock: NonCallableMagicMock = main_window_cls_mock.return_value
    main_window_mock.isVisible.return_value = False

    return AppDependencyMocks(
        localization_cls=localization_cls_mock,
        localization=localization_mock,
        settings_cls=settings_cls_mock,
        settings=settings_mock,
        main_window_cls=main_window_cls_mock,
        main_window=main_window_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def initialized_app_context(
    app_context: AppContext,
    app_config: AppConfig,
    dependency_mocks: AppDependencyMocks,
) -> InitializedAppContext:
    """Provide an initialized App with lifecycle calls reset for the next action."""
    # Setup
    app_context.app.initialize(app_config)
    app_context.lifecycle_mock.state = AppState.INITIALIZED
    reset_lifecycle_mock_calls(app_context)

    return InitializedAppContext(
        app_context=app_context,
        app_config=app_config,
        dependency_mocks=dependency_mocks,
    )


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestAppConstruction:
    """Verify the application's initial identity and public properties."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_exposes_lifecycle_state_and_empty_services(
        self,
        app_context: AppContext,
    ) -> None:
        """The application exposes lifecycle state and initially empty services."""
        # Assert
        assert app_context.app.objectName() == "App"
        assert app_context.app.state is AppState.CREATED
        assert app_context.app.localization is None
        assert app_context.app.settings is None
        assert app_context.app.main_window is None


###############################################################################
class TestAppLaunch:
    """Cover complete lifecycle orchestration performed by ``App.launch``."""

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
    def test_configuration_error_propagates_after_disposal(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A configuration construction error propagates after disposal."""
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
    def test_initialization_error_propagates_after_disposal(
        self,
        mocker: MockerFixture,
    ) -> None:
        """An initialization error propagates after disposal and skips run."""
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
        with pytest.raises(RuntimeError, match=r"^Initialization failed$"):
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
    def test_execution_error_propagates_after_disposal(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A run exception propagates after disposal."""
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
        with pytest.raises(RuntimeError, match=r"^Execution failed$"):
            App.launch(app_mock)

        assert app_mock.method_calls == [
            mocker.call.initialize(config),
            mocker.call.run(),
            mocker.call.dispose(),
        ]


###############################################################################
class TestAppInitialize:
    """Cover application initialization and lifecycle-boundary interactions."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_state_transition
    def test_valid_config_initializes_metadata_services_and_settings(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """A valid configuration initializes Qt metadata and PackY services."""
        # Arrange
        app = app_context.app
        lifecycle_mock = app_context.lifecycle_mock

        # Act
        app.initialize(app_config)

        # Assert
        lifecycle_mock.transition.assert_called_once_with(Transition.INITIALIZE)

        assert app.organizationName() == "PackY"
        assert app.organizationDomain() == "packy.com"
        assert app.applicationName() == "PackY"
        assert app.applicationDisplayName() == "PackY"
        assert app.applicationVersion() == app_config.VERSION

        assert app.localization is dependency_mocks.localization
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )

        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert app.settings is dependency_mocks.settings
        dependency_mocks.settings_cls.assert_called_once_with(app)

        assert app.main_window is None
        dependency_mocks.main_window_cls.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_second_initialization_propagates_lifecycle_error_without_replacing_services(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """A rejected second initialization preserves existing services."""
        # Arrange
        app = app_context.app
        lifecycle_mock = app_context.lifecycle_mock

        app.initialize(app_config)
        error = LifecycleTransitionNotAllowedError(
            Transition.INITIALIZE,
            AppState.INITIALIZED,
        )
        lifecycle_mock.transition.side_effect = error

        localization_before = app.localization
        settings_before = app.settings
        reset_lifecycle_mock_calls(app_context)

        # Act / Assert
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            app.initialize(app_config)

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.INITIALIZE)

        assert app.localization is localization_before
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )

        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert app.settings is settings_before
        dependency_mocks.settings_cls.assert_called_once_with(app)

        assert app.main_window is None
        dependency_mocks.main_window_cls.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_localization_error_propagates_without_creating_settings(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """A localization failure propagates before settings are created."""
        # Arrange
        app = app_context.app
        lifecycle_mock = app_context.lifecycle_mock

        error = RuntimeError("Translation installation failed")
        dependency_mocks.localization.install_translators.side_effect = error

        # Act / Assert
        with pytest.raises(RuntimeError) as exc_info:
            app.initialize(app_config)

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.INITIALIZE)
        assert app.state is AppState.CREATED

        assert app.localization is dependency_mocks.localization
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )

        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        dependency_mocks.settings_cls.assert_not_called()

        assert app.main_window is None
        dependency_mocks.main_window_cls.assert_not_called()


###############################################################################
class TestAppRun:
    """Cover main-window restoration, event-loop entry and its initialization prerequisite."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_run_initialized_app_restores_window_and_returns_event_loop_exit_code(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Running an initialized application restores and shows its window before returning."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        app_config = initialized_app_context.app_config
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock

        app_exec_mock = mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )
        call_stack_mock = mocker.Mock(name="app_run_call_stack")
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
        lifecycle_mock.transition.assert_called_once_with(Transition.RUN)
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
    def test_run_before_initialization_propagates_lifecycle_error(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        mocker: MockerFixture,
    ) -> None:
        """Running before initialization is rejected without creating a window or calling exec."""
        # Arrange
        app = app_context.app
        lifecycle_mock = app_context.lifecycle_mock

        error = LifecycleTransitionNotAllowedError(
            Transition.RUN,
            AppState.CREATED,
        )
        lifecycle_mock.transition.side_effect = error
        app_exec_mock = mocker.patch.object(
            app,
            "exec",
            autospec=True,
        )

        # Act / Assert
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            app.run()

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.RUN)
        assert app.state is AppState.CREATED

        assert app.localization is None
        dependency_mocks.localization_cls.assert_not_called()

        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        dependency_mocks.settings_cls.assert_not_called()

        assert app.main_window is None
        dependency_mocks.main_window_cls.assert_not_called()

        app_exec_mock.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_main_window_restoration_error_propagates_without_entering_event_loop(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """A main window restoration error propagates before event-loop entry."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        app_config = initialized_app_context.app_config
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock

        error = RuntimeError("Restoration failed")
        dependency_mocks.main_window.restore_last_batch.side_effect = error
        app_exec_mock = mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
        )
        call_stack_mock = mocker.Mock(name="app_run_call_stack")
        call_stack_mock.attach_mock(
            dependency_mocks.main_window_cls,
            "main_window_cls",
        )
        call_stack_mock.attach_mock(
            dependency_mocks.main_window,
            "main_window",
        )
        call_stack_mock.attach_mock(app_exec_mock, "exec")

        # Act / Assert
        with pytest.raises(RuntimeError) as exc_info:
            initialized_app.run()

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.RUN)

        assert initialized_app.main_window is dependency_mocks.main_window
        assert call_stack_mock.mock_calls == [
            mocker.call.main_window_cls(
                app_config,
                initialized_app.settings,
            ),
            mocker.call.main_window.load_settings(),
            mocker.call.main_window.show(),
            mocker.call.main_window.restore_last_batch(),
        ]
        app_exec_mock.assert_not_called()


###############################################################################
class TestAppPostRun:
    """Cover state persistence performed when application execution finishes."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_about_to_quit_after_run_saves_app_state(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
        qtbot: QtBot,
    ) -> None:
        """The real quit signal requests FINISH and saves app state."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock
        save_app_state_spy = mocker.spy(initialized_app, "_save_app_state")

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )

        initialized_app.run()
        reset_lifecycle_mock_calls(initialized_app_context.app_context)

        # Act
        with qtbot.waitSignal(initialized_app.aboutToQuit):
            initialized_app.aboutToQuit.emit()

        # Assert
        lifecycle_mock.transition.assert_called_once_with(Transition.FINISH)
        save_app_state_spy.assert_called_once_with()
        dependency_mocks.main_window.save_settings.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_post_run_before_run_propagates_lifecycle_error(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Launching post-run before run is rejected without change the application state."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock
        save_app_state_spy = mocker.spy(initialized_app, "_save_app_state")

        error = LifecycleTransitionNotAllowedError(
            Transition.FINISH,
            AppState.INITIALIZED,
        )
        lifecycle_mock.transition.side_effect = error

        # Act / Assert
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            initialized_app.post_run()

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.FINISH)
        save_app_state_spy.assert_not_called()
        dependency_mocks.main_window.save_settings.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_save_app_state_error_propagates_from_post_run(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """A save app state error propagates after a successful transition."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock
        save_app_state_spy = mocker.spy(initialized_app, "_save_app_state")

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=0,
        )

        initialized_app.run()
        reset_lifecycle_mock_calls(initialized_app_context.app_context)

        error = RuntimeError("State save failed")
        dependency_mocks.main_window.save_settings.side_effect = error

        # Act / Assert
        with pytest.raises(RuntimeError) as exc_info:
            initialized_app.post_run()

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.FINISH)
        save_app_state_spy.assert_called_once_with()
        dependency_mocks.main_window.save_settings.assert_called_once_with()


###############################################################################
class TestAppDispose:
    """Cover accepted, skipped, and rejected disposal behavior."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_finished_app_clears_services_and_main_window(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Disposal after finishing clears the retained window reference."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )

        initialized_app.run()
        initialized_app.post_run()
        reset_lifecycle_mock_calls(initialized_app_context.app_context)

        # Act
        initialized_app.dispose()

        # Assert
        lifecycle_mock.transition.assert_called_once_with(Transition.DISPOSE)
        assert initialized_app.localization is None
        assert initialized_app._config is None  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_disposing_after_initializing_clears_services_and_main_window(
        self,
        initialized_app_context: InitializedAppContext,
    ) -> None:
        """Accepted disposal clears all application-owned service references."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock

        # Act
        initialized_app.dispose()

        # Assert
        lifecycle_mock.transition.assert_called_once_with(Transition.DISPOSE)
        assert initialized_app.localization is None
        assert initialized_app._config is None  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_branch
    @pytest.mark.technique_state_transition
    def test_disposing_on_already_disposed_has_no_effect(
        self,
        app_context: AppContext,
    ) -> None:
        """An already-disposed application returns without changing app state."""
        # Arrange
        app = app_context.app
        lifecycle_mock = app_context.lifecycle_mock
        lifecycle_mock.state = AppState.DISPOSED

        assert app.localization is None
        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        assert app.main_window is None

        # Act
        app.dispose()

        # Assert
        lifecycle_mock.transition.assert_not_called()
        assert app.localization is None
        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        assert app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_disposed_state_allows_reinitialization(
        self,
        initialized_app_context: InitializedAppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """An already-disposed application can be reinitialized."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock
        lifecycle_mock.state = AppState.FINISHED

        initialized_app.dispose()
        assert initialized_app.localization is None
        assert initialized_app._config is None  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

        reset_lifecycle_mock_calls(initialized_app_context.app_context)

        # Act
        initialized_app.initialize(app_config)

        # Assert
        lifecycle_mock.transition.assert_called_once_with(Transition.INITIALIZE)
        assert initialized_app.localization is dependency_mocks.localization
        assert initialized_app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is dependency_mocks.settings
        assert initialized_app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_disposal_while_running_propagates_lifecycle_error_and_preserves_services(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Rejected disposal while running preserves existing application services."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        lifecycle_mock = initialized_app_context.app_context.lifecycle_mock

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )
        initialized_app.run()
        error = LifecycleTransitionNotAllowedError(
            Transition.DISPOSE,
            AppState.RUNNING,
        )
        lifecycle_mock.transition.side_effect = error

        localization_before = initialized_app.localization
        app_config_before = initialized_app._config  # pyright: ignore[reportPrivateUsage]
        settings_before = initialized_app.settings
        main_window_before = initialized_app.main_window
        reset_lifecycle_mock_calls(initialized_app_context.app_context)

        # Act / Assert
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            initialized_app.dispose()

        assert exc_info.value is error
        lifecycle_mock.transition.assert_called_once_with(Transition.DISPOSE)
        assert initialized_app.localization is localization_before
        assert initialized_app._config is app_config_before  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is settings_before
        assert initialized_app.main_window is main_window_before
