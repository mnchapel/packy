"""Define application lifecycle states and validated transitions.

The :meth:`AppLifecycle.transition` context manager commits a state change
only when the transition context exits without an exception.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Future library
from __future__ import annotations

# Standard library
from contextlib import contextmanager
from enum import IntEnum, auto, unique
from typing import TYPE_CHECKING, Final, final

if TYPE_CHECKING:
    # Standard library
    from collections.abc import Generator

###############################################################################
type TransitionTargets = dict[Transition, AppState]
type TransitionTable = dict[AppState, TransitionTargets]


###############################################################################
@final
@unique
class AppState(IntEnum):
    """Represent the states in an application lifecycle."""

    CREATED = auto()
    INITIALIZED = auto()
    RUNNING = auto()
    FINISHED = auto()
    DISPOSED = auto()


###############################################################################
@final
@unique
class Transition(IntEnum):
    """Represent application lifecycle transitions."""

    INITIALIZE = auto()
    RUN = auto()
    FINISH = auto()
    DISPOSE = auto()


###############################################################################
class LifecycleError(RuntimeError):
    """Indicate an invalid application lifecycle transition."""


###############################################################################
class LifecycleTransitionInProgressError(LifecycleError):
    """Indicate that another lifecycle transition is already in progress."""

    def __init__(self, transition: Transition) -> None:
        """Initialize the error for an active lifecycle transition.

        Args:
            transition (Transition): Transition already in progress.
        """
        msg = f"Lifecycle transition '{transition.name}' is already in progress."
        super().__init__(msg)


###############################################################################
class LifecycleTransitionNotAllowedError(LifecycleError):
    """Indicate that a lifecycle transition is not allowed from the current state."""

    def __init__(
        self,
        transition: Transition,
        state: AppState,
    ) -> None:
        """Initialize the error for a disallowed lifecycle transition.

        Args:
            transition (Transition): Transition that was requested.
            state (AppState): State from which the transition was requested.
        """
        msg = f"Transition '{transition.name}' is not allowed from state '{state.name}'."
        super().__init__(msg)


###############################################################################
@final
class AppLifecycle:
    """Track the state of an application lifecycle.

    A lifecycle starts in :attr:`AppState.CREATED`. A transition changes the
    state only when its context exits without an exception.

    The allowed transitions are:

    +-----------------+------------+-----------------+
    | Source state    | Transition | Target state    |
    +=================+============+=================+
    | ``CREATED``     | ``INITIALIZE`` | ``INITIALIZED`` |
    +-----------------+-------------+-----------------+
    | ``CREATED``     | ``DISPOSE`` | ``DISPOSED``   |
    +-----------------+-------------+----------------+
    | ``INITIALIZED`` | ``RUN``     | ``RUNNING``    |
    +-----------------+-------------+----------------+
    | ``INITIALIZED`` | ``DISPOSE`` | ``DISPOSED``   |
    +-----------------+-------------+----------------+
    | ``RUNNING``     | ``FINISH``  | ``FINISHED``   |
    +-----------------+-------------+----------------+
    | ``FINISHED``    | ``DISPOSE`` | ``DISPOSED``   |
    +-----------------+-------------+----------------+
    | ``DISPOSED``    | ``INITIALIZE`` | ``INITIALIZED`` |
    +-----------------+-------------+----------------+
    """

    _TRANSITIONS: Final[TransitionTable] = {
        AppState.CREATED: {
            Transition.INITIALIZE: AppState.INITIALIZED,
            Transition.DISPOSE: AppState.DISPOSED,
        },
        AppState.INITIALIZED: {
            Transition.RUN: AppState.RUNNING,
            Transition.DISPOSE: AppState.DISPOSED,
        },
        AppState.RUNNING: {
            Transition.FINISH: AppState.FINISHED,
        },
        AppState.FINISHED: {
            Transition.DISPOSE: AppState.DISPOSED,
        },
        AppState.DISPOSED: {
            Transition.INITIALIZE: AppState.INITIALIZED,
        },
    }

    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """Initialize the lifecycle in :attr:`AppState.CREATED`."""
        self._state = AppState.CREATED
        self._transition: Transition | None = None

    # -------------------------------------------------------------------------
    @property
    def state(self) -> AppState:
        """The current application lifecycle state."""
        return self._state

    # -------------------------------------------------------------------------
    @contextmanager
    def transition(self, transition: Transition) -> Generator[None]:
        """Provide a context for applying a lifecycle transition.

        The state changes to the transition's target state when the context
        exits without an exception. If the context exits with an exception,
        the state remains unchanged.

        Args:
            transition (Transition): Transition to apply.

        Raises:
            LifecycleTransitionInProgressError: Another lifecycle transition
              is already in progress.
            LifecycleTransitionNotAllowedError: The transition is not allowed
              from the current state.
        """
        if self._transition is not None:
            raise LifecycleTransitionInProgressError(self._transition)

        try:
            target_state = self._TRANSITIONS[self._state][transition]
        except KeyError:
            raise LifecycleTransitionNotAllowedError(
                transition,
                self._state,
            ) from None

        self._transition = transition

        try:
            yield
        except BaseException:
            self._transition = None
            raise
        else:
            self._state = target_state
            self._transition = None
