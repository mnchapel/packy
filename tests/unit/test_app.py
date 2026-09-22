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
    AppState,
    LifecycleTransitionNotAllowedError,
    Transition,
)

# Third-party
import pytest

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING
from unittest.mock import call

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
### Test Contexts
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AppContext:
    """Expose an application with its isolated lifecycle dependency."""

    app: App
    lifecycle_transition_spy: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class InitializedAppContext:
    """Expose an initialized application with its configuration and isolated dependencies."""

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
) -> AppContext:
    """Replace the shared application's real lifecycle with an isolated mock."""
    # Setup
    lifecycle_transition_spy = mocker.spy(app._lifecycle, "transition")  # pyright: ignore[reportPrivateUsage]

    return AppContext(
        app=app,
        lifecycle_transition_spy=lifecycle_transition_spy,
    )


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
    """Provide an initialized application and its isolated dependencies."""
    # Setup
    app_context.app.initialize(app_config)

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
        app: App,
    ) -> None:
        """The application exposes lifecycle state and initially empty services."""
        # Assert
        assert app.objectName() == "App"
        assert app.state is AppState.CREATED
        assert app.localization is None
        assert app.settings is None
        assert app.main_window is None


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
        """A valid configuration initializes Qt metadata and services."""
        # Arrange
        app = app_context.app
        lifecycle_transition_spy: MagicMock = app_context.lifecycle_transition_spy

        # Act
        app.initialize(app_config)

        # Assert
        assert app.state is AppState.INITIALIZED
        lifecycle_transition_spy.assert_called_once_with(Transition.INITIALIZE)

        assert app.organizationName() == "PackY"
        assert app.organizationDomain() == "packy.com"
        assert app.applicationName() == "PackY"
        assert app.applicationDisplayName() == "PackY"
        assert app.applicationVersion() == app_config.VERSION

        assert app.localization is dependency_mocks.localization
        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert app.settings is dependency_mocks.settings
        assert app.main_window is None
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )
        dependency_mocks.settings_cls.assert_called_once_with(app)
        dependency_mocks.main_window_cls.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_second_initialization_raises_lifecycle_error_without_replacing_services(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """Repeated initialization is rejected without replacing services."""
        # Arrange
        app = app_context.app
        lifecycle_transition_spy = app_context.lifecycle_transition_spy

        app.initialize(app_config)
        localization_before = app.localization
        settings_before = app.settings

        # Act
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            app.initialize(app_config)

        # Assert
        assert exc_info.value.state is AppState.INITIALIZED
        assert exc_info.value.transition is Transition.INITIALIZE
        assert app.state is AppState.INITIALIZED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.INITIALIZE),
        ]

        assert app.localization is localization_before
        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert app.settings is settings_before
        assert app.main_window is None
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )
        dependency_mocks.settings_cls.assert_called_once_with(app)
        dependency_mocks.main_window_cls.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_dependency_error_keep_created_state_and_allows_retry(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """A localization error rolls back the transition and permits retry."""
        # Arrange
        app = app_context.app
        lifecycle_transition_spy = app_context.lifecycle_transition_spy

        error = RuntimeError("Translation installation failed")
        dependency_mocks.localization.install_translators.side_effect = [error, None]

        # Act - First try
        with pytest.raises(RuntimeError) as exc_info:
            app.initialize(app_config)

        # Assert - First try
        assert exc_info.value is error
        assert app.state is AppState.CREATED
        lifecycle_transition_spy.assert_called_once_with(Transition.INITIALIZE)

        assert app.localization is dependency_mocks.localization
        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        assert app.main_window is None
        dependency_mocks.localization_cls.assert_called_once_with()
        dependency_mocks.localization.install_translators.assert_called_once_with(
            app_config.DEFAULT_LANGUAGE_CODE,
        )
        dependency_mocks.settings_cls.assert_not_called()
        dependency_mocks.main_window_cls.assert_not_called()

        # Act - Second try
        app.initialize(app_config)

        # Assert - Second try
        assert app.state is AppState.INITIALIZED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.INITIALIZE),
        ]

        assert app.localization is dependency_mocks.localization
        assert app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert app.settings is dependency_mocks.settings
        assert app.main_window is None
        assert dependency_mocks.localization_cls.call_args_list == [
            call(),
            call(),
        ]
        assert dependency_mocks.localization.install_translators.call_args_list == [
            call(app_config.DEFAULT_LANGUAGE_CODE),
            call(app_config.DEFAULT_LANGUAGE_CODE),
        ]
        dependency_mocks.settings_cls.assert_called_once_with(app)
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
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy

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
        assert exit_code == 2
        assert initialized_app.state is AppState.RUNNING
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
        ]
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
    def test_run_before_initialization_raises_lifecycle_error(
        self,
        app_context: AppContext,
        dependency_mocks: AppDependencyMocks,
        mocker: MockerFixture,
    ) -> None:
        """Running before initialization is rejected without creating a window and calling exec."""
        # Arrange
        app = app_context.app
        lifecycle_transition_spy = app_context.lifecycle_transition_spy

        app_exec_mock = mocker.patch.object(
            app,
            "exec",
            autospec=True,
            return_value=2,
        )

        # Act
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            app.run()

        # Assert
        assert exc_info.value.state is AppState.CREATED
        assert exc_info.value.transition is Transition.RUN
        assert app.state is AppState.CREATED
        lifecycle_transition_spy.assert_called_once_with(Transition.RUN)

        assert app.localization is None
        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        assert app.main_window is None
        dependency_mocks.localization_cls.assert_not_called()
        dependency_mocks.settings_cls.assert_not_called()
        dependency_mocks.main_window_cls.assert_not_called()
        app_exec_mock.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_restoration_error_keeps_initialized_state_and_allows_retry(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """A main window restoration error raises before event-loop entry."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        app_config = initialized_app_context.app_config
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy

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

        error = RuntimeError("Restoration failed")
        dependency_mocks.main_window.restore_last_batch.side_effect = [error, None]

        # Act - First try
        with pytest.raises(RuntimeError) as exc_info:
            initialized_app.run()

        # Assert - First try
        assert exc_info.value is error
        assert initialized_app.state is AppState.INITIALIZED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
        ]

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

        # Act - Second try
        exit_code = initialized_app.run()

        # Assert - Second try
        assert exit_code == 2
        assert initialized_app.state is AppState.RUNNING
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
            call(Transition.RUN),
        ]

        assert initialized_app.main_window is dependency_mocks.main_window
        assert call_stack_mock.mock_calls == [
            mocker.call.main_window_cls(
                app_config,
                initialized_app.settings,
            ),
            mocker.call.main_window.load_settings(),
            mocker.call.main_window.show(),
            mocker.call.main_window.restore_last_batch(),
            mocker.call.main_window_cls(
                app_config,
                initialized_app.settings,
            ),
            mocker.call.main_window.load_settings(),
            mocker.call.main_window.show(),
            mocker.call.main_window.restore_last_batch(),
            mocker.call.exec(),
        ]
        app_exec_mock.assert_called_once_with()


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
        """The Qt quit signal saves app state, settings and enters in FINISHED state."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy
        save_app_state_spy = mocker.spy(initialized_app, "_save_app_state")

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )

        initialized_app.run()

        # Act
        with qtbot.waitSignal(initialized_app.aboutToQuit):
            initialized_app.aboutToQuit.emit()

        # Assert
        assert initialized_app.state is AppState.FINISHED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
            call(Transition.FINISH),
        ]
        save_app_state_spy.assert_called_once_with()
        dependency_mocks.main_window.save_settings.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_post_run_before_run_raises_lifecycle_error(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Launching post-run before run is rejected without change the application state."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy
        save_app_state_spy = mocker.spy(initialized_app, "_save_app_state")

        # Act
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            initialized_app.post_run()

        # Assert
        assert exc_info.value.state is AppState.INITIALIZED
        assert exc_info.value.transition is Transition.FINISH
        assert initialized_app.state is AppState.INITIALIZED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.FINISH),
        ]
        save_app_state_spy.assert_not_called()
        dependency_mocks.main_window.save_settings.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_save_app_error_keeps_running_state_and_allows_retry(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """A save error rolls back finish and permits a subsequent retry."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy
        save_app_state_spy = mocker.spy(initialized_app, "_save_app_state")

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )

        initialized_app.run()
        error = RuntimeError("State save failed")
        dependency_mocks.main_window.save_settings.side_effect = [error, None]

        # Act - First try
        with pytest.raises(RuntimeError) as exc_info:
            initialized_app.post_run()

        # Assert - First try
        assert exc_info.value is error
        assert initialized_app.state is AppState.RUNNING
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
            call(Transition.FINISH),
        ]
        save_app_state_spy.assert_called_once_with()
        dependency_mocks.main_window.save_settings.assert_called_once_with()

        # Act - Second try
        initialized_app.post_run()

        # Assert - Second try
        assert initialized_app.state is AppState.FINISHED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
            call(Transition.FINISH),
            call(Transition.FINISH),
        ]
        assert save_app_state_spy.call_count == 2
        assert dependency_mocks.main_window.save_settings.call_args_list == [
            call(),
            call(),
        ]


###############################################################################
class TestAppDispose:
    """Cover accepted, skipped, and rejected disposal behavior."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_finished_app_clears_services_and_window_reference(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Disposal from FINISHED clears the window and service references."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )

        initialized_app.run()
        initialized_app.post_run()

        # Act
        initialized_app.dispose()

        # Assert
        assert initialized_app.state is AppState.DISPOSED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
            call(Transition.FINISH),
            call(Transition.DISPOSE),
        ]
        assert initialized_app.localization is None
        assert initialized_app._config is None  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_initialized_app_clears_services_and_enters_disposed_state(
        self,
        initialized_app_context: InitializedAppContext,
    ) -> None:
        """Disposal from INITIALIZED clears all service references and becomes terminal."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy

        # Act
        initialized_app.dispose()

        # Assert
        assert initialized_app.state is AppState.DISPOSED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.DISPOSE),
        ]
        assert initialized_app.localization is None
        assert initialized_app._config is None  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_branch
    @pytest.mark.technique_state_transition
    def test_repeated_disposal_is_idempotent_from_created_state(
        self,
        app_context: AppContext,
    ) -> None:
        """Repeated disposal just returns without changing the app state or any services."""
        # Arrange
        app = app_context.app
        lifecycle_transition_spy = app_context.lifecycle_transition_spy

        assert app.state is AppState.CREATED
        assert app.localization is None
        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        assert app.main_window is None

        # Act
        app.dispose()
        assert app.state is AppState.DISPOSED
        app.dispose()

        # Assert
        assert app.state is AppState.DISPOSED
        lifecycle_transition_spy.assert_called_once_with(Transition.DISPOSE)

        assert app.localization is None
        assert app._config is None  # pyright: ignore[reportPrivateUsage]
        assert app.settings is None
        assert app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_disposed_state_allows_initialization(
        self,
        initialized_app_context: InitializedAppContext,
        dependency_mocks: AppDependencyMocks,
        app_config: AppConfig,
    ) -> None:
        """An already-disposed application can be reinitialized."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        dependency_mocks = initialized_app_context.dependency_mocks
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy

        initialized_app.dispose()
        assert initialized_app.state is AppState.DISPOSED
        assert initialized_app.localization is None
        assert initialized_app._config is None  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is None
        assert initialized_app.main_window is None

        # Act
        initialized_app.initialize(app_config)

        # Assert
        assert initialized_app.state is AppState.INITIALIZED
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.DISPOSE),
            call(Transition.INITIALIZE),
        ]
        assert initialized_app.localization is dependency_mocks.localization
        assert initialized_app._config is app_config  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is dependency_mocks.settings
        assert initialized_app.main_window is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_state_transition
    def test_disposal_while_running_raises_lifecycle_error_and_preserves_services(
        self,
        initialized_app_context: InitializedAppContext,
        mocker: MockerFixture,
    ) -> None:
        """Rejected disposal while running preserves existing application services."""
        # Arrange
        initialized_app = initialized_app_context.app_context.app
        lifecycle_transition_spy = initialized_app_context.app_context.lifecycle_transition_spy

        mocker.patch.object(
            initialized_app,
            "exec",
            autospec=True,
            return_value=2,
        )
        initialized_app.run()

        localization_before = initialized_app.localization
        app_config_before = initialized_app._config  # pyright: ignore[reportPrivateUsage]
        settings_before = initialized_app.settings
        main_window_before = initialized_app.main_window

        # Act
        with pytest.raises(LifecycleTransitionNotAllowedError) as exc_info:
            initialized_app.dispose()

        # Assert
        assert exc_info.value.state is AppState.RUNNING
        assert exc_info.value.transition is Transition.DISPOSE
        assert initialized_app.state is AppState.RUNNING
        assert lifecycle_transition_spy.call_args_list == [
            call(Transition.INITIALIZE),
            call(Transition.RUN),
            call(Transition.DISPOSE),
        ]

        assert initialized_app.localization is localization_before
        assert initialized_app._config is app_config_before  # pyright: ignore[reportPrivateUsage]
        assert initialized_app.settings is settings_before
        assert initialized_app.main_window is main_window_before
