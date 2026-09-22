"""Unit tests for :class:`AppLifecycle`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.core.app_lifecycle import (
    AppLifecycle,
    AppState,
    LifecycleTransitionInProgressError,
    LifecycleTransitionNotAllowedError,
    Transition,
)

# Third-party
import pytest

# Standard library
import re


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestAppLifecycleConstruction:
    """Unit tests for :class:`AppLifecycle` construction."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_new_instance_starts_in_created_state(self) -> None:
        """A newly constructed lifecycle exposes the created state."""
        # Arrange
        lifecycle = AppLifecycle()

        # Act
        state = lifecycle.state

        # Assert
        assert state is AppState.CREATED


###############################################################################
class TestAppLifecycleTransitions:
    """Cover the observable state and transition behavior of AppLifecycle."""

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        (
            "transition_history",
            "source_state",
            "transition",
            "target_state",
        ),
        [
            pytest.param(
                (),
                AppState.CREATED,
                Transition.INITIALIZE,
                AppState.INITIALIZED,
                id="created-initialize",
                marks=pytest.mark.scenario_happy_path,
            ),
            pytest.param(
                (),
                AppState.CREATED,
                Transition.DISPOSE,
                AppState.DISPOSED,
                id="created-dispose",
                marks=pytest.mark.scenario_alternate_path,
            ),
            pytest.param(
                (Transition.INITIALIZE,),
                AppState.INITIALIZED,
                Transition.RUN,
                AppState.RUNNING,
                id="initialized-run",
                marks=pytest.mark.scenario_happy_path,
            ),
            pytest.param(
                (Transition.INITIALIZE,),
                AppState.INITIALIZED,
                Transition.DISPOSE,
                AppState.DISPOSED,
                id="initialized-dispose",
                marks=pytest.mark.scenario_alternate_path,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                ),
                AppState.RUNNING,
                Transition.FINISH,
                AppState.FINISHED,
                id="running-finish",
                marks=pytest.mark.scenario_happy_path,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                    Transition.FINISH,
                ),
                AppState.FINISHED,
                Transition.DISPOSE,
                AppState.DISPOSED,
                id="finished-dispose",
                marks=pytest.mark.scenario_happy_path,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                    Transition.FINISH,
                    Transition.DISPOSE,
                ),
                AppState.DISPOSED,
                Transition.INITIALIZE,
                AppState.INITIALIZED,
                id="disposed-initialize",
                marks=pytest.mark.scenario_happy_path,
            ),
        ],
    )
    def test_allowed_transition_completes_target_state(
        self,
        transition_history: tuple[Transition, ...],
        source_state: AppState,
        transition: Transition,
        target_state: AppState,
    ) -> None:
        """An allowed transition remains pending until it completes on context exit."""
        # Arrange
        lifecycle = AppLifecycle()

        for completed_transition in transition_history:
            with lifecycle.transition(completed_transition):
                pass

        assert lifecycle.state is source_state

        # Act
        with lifecycle.transition(transition):
            state_before_transition = lifecycle.state

        # Assert
        assert state_before_transition is source_state
        assert lifecycle.state is target_state

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        (
            "transition_history",
            "source_state",
            "transition",
        ),
        [
            pytest.param(
                (),
                AppState.CREATED,
                Transition.RUN,
                id="created-run",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (),
                AppState.CREATED,
                Transition.FINISH,
                id="created-finish",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (Transition.INITIALIZE,),
                AppState.INITIALIZED,
                Transition.INITIALIZE,
                id="initialized-initialize",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (Transition.INITIALIZE,),
                AppState.INITIALIZED,
                Transition.FINISH,
                id="initialized-finish",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                ),
                AppState.RUNNING,
                Transition.INITIALIZE,
                id="running-initialize",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                ),
                AppState.RUNNING,
                Transition.RUN,
                id="running-run",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                ),
                AppState.RUNNING,
                Transition.DISPOSE,
                id="running-dispose",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                    Transition.FINISH,
                ),
                AppState.FINISHED,
                Transition.INITIALIZE,
                id="finished-initialize",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                    Transition.FINISH,
                ),
                AppState.FINISHED,
                Transition.RUN,
                id="finished-run",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (
                    Transition.INITIALIZE,
                    Transition.RUN,
                    Transition.FINISH,
                ),
                AppState.FINISHED,
                Transition.FINISH,
                id="finished-finish",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (Transition.DISPOSE,),
                AppState.DISPOSED,
                Transition.RUN,
                id="disposed-run",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (Transition.DISPOSE,),
                AppState.DISPOSED,
                Transition.FINISH,
                id="disposed-finish",
                marks=pytest.mark.scenario_invalid_input,
            ),
            pytest.param(
                (Transition.DISPOSE,),
                AppState.DISPOSED,
                Transition.DISPOSE,
                id="disposed-dispose",
                marks=pytest.mark.scenario_invalid_input,
            ),
        ],
    )
    def test_disallowed_transition_raises_not_allowed_error_and_preserves_state(
        self,
        transition_history: tuple[Transition, ...],
        source_state: AppState,
        transition: Transition,
    ) -> None:
        """A disallowed state-transition pair raises and leaves state unchanged."""
        # Arrange
        lifecycle = AppLifecycle()

        for completed_transition in transition_history:
            with lifecycle.transition(completed_transition):
                pass

        assert lifecycle.state is source_state

        # Act
        with (
            pytest.raises(LifecycleTransitionNotAllowedError) as exc_info,
            lifecycle.transition(transition),
        ):
            pass

        # Assert
        assert exc_info.value.state is source_state
        assert exc_info.value.transition is transition
        assert re.search(
            rf"'{re.escape(transition.name)}'.*'{re.escape(source_state.name)}'",
            str(exc_info.value),
        )
        assert lifecycle.state is source_state

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    def test_nested_transition_raises_in_progress_error_without_affecting_outer_transition(
        self,
    ) -> None:
        """A nested request is rejected without preventing the outer transition from completing."""
        # Arrange
        lifecycle = AppLifecycle()

        # Act
        with lifecycle.transition(Transition.INITIALIZE):
            with (
                pytest.raises(LifecycleTransitionInProgressError) as exc_info,
                lifecycle.transition(Transition.DISPOSE),
            ):
                pass
            state_after_rejection = lifecycle.state

        state_after_outer_exit = lifecycle.state

        # Assert
        assert exc_info.value.transition is Transition.INITIALIZE
        assert Transition.INITIALIZE.name in str(exc_info.value)
        assert state_after_rejection is AppState.CREATED
        assert state_after_outer_exit is AppState.INITIALIZED

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "error_type",
        [
            pytest.param(
                ValueError,
                id="exception",
                marks=pytest.mark.scenario_failure_error_path,
            ),
            pytest.param(
                KeyboardInterrupt,
                id="base-exception",
                marks=pytest.mark.scenario_failure_error_path,
            ),
        ],
    )
    def test_transition_body_error_preserves_state_and_allows_retry(
        self,
        error_type: type[ValueError | KeyboardInterrupt],
    ) -> None:
        """A body error propagates while rollback leaves the transition reusable."""
        # Arrange
        lifecycle = AppLifecycle()
        source_state = lifecycle.state
        target_state = AppState.INITIALIZED
        raised_error = error_type("random error")

        # Act
        with (
            pytest.raises(error_type) as exc_info,
            lifecycle.transition(Transition.INITIALIZE),
        ):
            raise raised_error

        state_after_error = lifecycle.state

        with lifecycle.transition(Transition.INITIALIZE):
            pass

        state_after_retry = lifecycle.state

        # Assert
        assert exc_info.value is raised_error
        assert state_after_error is source_state
        assert state_after_retry is target_state
