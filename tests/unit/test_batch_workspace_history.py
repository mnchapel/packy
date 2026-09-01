"""Unit tests for :class:`BatchWorkspaceHistory`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.constants.settings_keys import WorkspaceSettings
from packy.core.app import UserSettings
from packy.core.batch_workspace import BatchWorkspaceHistory

# Third-party
import pytest
from PySide6.QtCore import QObject

# Standard library
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from collections.abc import Callable
    from pathlib import Path
    from unittest.mock import NonCallableMagicMock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def user_settings_mock(mocker: MockerFixture) -> NonCallableMagicMock:
    """Provide a strict test double for recent-history persistence."""
    # Setup
    user_settings_mock: NonCallableMagicMock = mocker.create_autospec(
        UserSettings,
        instance=True,
        spec_set=True,
    )

    def emit_change(
        _key: object,
        value: object,
        callback: Callable[[object], None],
    ) -> None:
        callback(value)

    user_settings_mock.set_value.side_effect = emit_change
    return user_settings_mock


# -----------------------------------------------------------------------------
@pytest.fixture
def workspace_history(
    user_settings_mock: NonCallableMagicMock,
) -> BatchWorkspaceHistory:
    """Provide an empty recent-batch history with the default test capacity."""
    # Setup
    parent = QObject()
    history = BatchWorkspaceHistory(
        max_recent_batches=2,
        settings=user_settings_mock,
        parent=parent,
    )
    history._qt_parent_ref = parent  # pyright: ignore[reportAttributeAccessIssue]
    return history


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestWorkspaceHistoryconstruction:
    """Cover BatchWorkspaceHistory construction and collaborator wiring."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_initializes_empty_with_qobject_identity(
        self,
        workspace_history: BatchWorkspaceHistory,
    ) -> None:
        """Construction preserves Qt identity and exposes an empty public history."""
        # Assert
        assert isinstance(workspace_history.parent(), QObject)
        assert workspace_history.objectName() == "BatchWorkspaceHistory"
        assert workspace_history.recently_opened == ()
        assert workspace_history.latest_opened is None


###############################################################################
class TestWorkspaceHistoryRecentlyOpened:
    """Cover recently opened property."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_property_returns_immutable_value(
        self,
        workspace_history: BatchWorkspaceHistory,
        tmp_path: Path,
    ) -> None:
        """The recently opened property returns a snapshot unaffected by later changes."""
        # Arrange
        newest_batch_path = (tmp_path / "newest.json").resolve()
        recent_batches_paths = [
            (tmp_path / "current.json").resolve(),
            (tmp_path / "oldest.json").resolve(),
        ]
        workspace_history._recent_batches = list(recent_batches_paths)  # pyright: ignore[reportPrivateUsage]
        original_recent_batches = workspace_history.recently_opened

        # Act
        workspace_history._recent_batches.append(newest_batch_path)  # pyright: ignore[reportPrivateUsage]

        # Assert
        assert original_recent_batches == tuple(recent_batches_paths)
        assert workspace_history.recently_opened == (
            *recent_batches_paths,
            newest_batch_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    def test_recently_opened_property_cannot_be_assigned(
        self,
        workspace_history: BatchWorkspaceHistory,
    ) -> None:
        """The recently opened property cannot be replaced directly by callers."""
        # Act / Assert
        with pytest.raises(AttributeError):
            workspace_history.recently_opened = None  # pyright: ignore[reportAttributeAccessIssue]


###############################################################################
class TestWorkspaceHistoryLatestOpened:
    """Cover lastest opened property."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_nonempty_history_returns_most_recent_path(
        self,
        workspace_history: BatchWorkspaceHistory,
        tmp_path: Path,
    ) -> None:
        """A populated history exposes its first path as the latest opened batch."""
        # Arrange
        recent_batches_paths = [
            (tmp_path / "current.json").resolve(),
            (tmp_path / "oldest.json").resolve(),
        ]
        workspace_history._recent_batches = list(recent_batches_paths)  # pyright: ignore[reportPrivateUsage]
        assert len(workspace_history.recently_opened) > 1

        # Act
        latest_opened = workspace_history.latest_opened

        # Assert
        assert latest_opened == recent_batches_paths[0]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_empty_history_returns_none(
        self,
        workspace_history: BatchWorkspaceHistory,
    ) -> None:
        """An empty history has no latest opened batch."""
        # Act
        latest_opened = workspace_history.latest_opened
        assert workspace_history.recently_opened == ()

        # Assert
        assert latest_opened is None


###############################################################################
class TestWorkspaceHistoryAddRecentlyOpened:
    """Cover ordering, deduplication, capacity, and persistence when adding paths."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_new_path_becomes_latest_and_is_persisted(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        qtbot: QtBot,
        tmp_path: Path,
    ) -> None:
        """Adding the first path makes it latest, persists it, and emits it."""
        # Arrange
        new_batch_path = (tmp_path / "newest.json").resolve()

        def check_recent_batches_signal(recent_batch_paths: list[Path]) -> bool:
            return recent_batch_paths == [new_batch_path]

        # Act
        with qtbot.waitSignal(
            workspace_history.recent_batches_changed,
            check_params_cb=check_recent_batches_signal,
        ):
            workspace_history.add_recently_opened(new_batch_path)

        # Assert
        assert workspace_history.recently_opened == (new_batch_path,)
        assert workspace_history.latest_opened == new_batch_path
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.set_value(
                WorkspaceSettings.RECENT_BATCHES,
                [new_batch_path],
                workspace_history.recent_batches_changed.emit,
            ),
            mocker.call.end_group(),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_existing_path_moves_to_front_without_duplication(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Reopening an existing path moves it to the front exactly once."""
        # Arrange
        first_batch_path = (tmp_path / "first.json").resolve()
        second_batch_path = (tmp_path / "second.json").resolve()
        workspace_history.add_recently_opened(first_batch_path)
        workspace_history.add_recently_opened(second_batch_path)

        assert workspace_history.recently_opened == (second_batch_path, first_batch_path)
        assert workspace_history.latest_opened == second_batch_path

        user_settings_mock.reset_mock()

        # Act
        workspace_history.add_recently_opened(first_batch_path)

        # Assert
        assert workspace_history.recently_opened == (first_batch_path, second_batch_path)
        assert workspace_history.latest_opened == first_batch_path
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.set_value(
                WorkspaceSettings.RECENT_BATCHES,
                [first_batch_path, second_batch_path],
                workspace_history.recent_batches_changed.emit,
            ),
            mocker.call.end_group(),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_boundary_value_analysis
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_capacity_overflow_discards_oldest_path(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Adding beyond capacity removes the oldest path and persists the rest."""
        # Arrange
        newest_batch_path = (tmp_path / "newest.json").resolve()
        current_batch_path = (tmp_path / "current.json").resolve()
        oldest_batch_path = (tmp_path / "oldest.json").resolve()
        workspace_history.add_recently_opened(oldest_batch_path)
        workspace_history.add_recently_opened(current_batch_path)

        user_settings_mock.reset_mock()

        # Act
        workspace_history.add_recently_opened(newest_batch_path)

        # Assert
        assert workspace_history.recently_opened == (newest_batch_path, current_batch_path)
        assert workspace_history.latest_opened == newest_batch_path
        assert oldest_batch_path not in workspace_history.recently_opened
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.set_value(
                WorkspaceSettings.RECENT_BATCHES,
                [newest_batch_path, current_batch_path],
                workspace_history.recent_batches_changed.emit,
            ),
            mocker.call.end_group(),
        ]


###############################################################################
class TestWorkspaceHistoryClearRecentlyOpened:
    """Cover clearing the history and persisting the resulting empty state."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_nonempty_history_persists_and_emits_empty_state(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Clearing populated history persists and emits the resulting empty state."""
        # Arrange
        new_batch_path = (tmp_path / "newest.json").resolve()
        workspace_history._recent_batches = [new_batch_path]  # pyright: ignore[reportPrivateUsage]
        user_settings_mock.reset_mock()

        def check_recent_batches_signal(recent_batch_paths: list[Path]) -> bool:
            return recent_batch_paths == []

        # Act
        with qtbot.waitSignal(
            workspace_history.recent_batches_changed,
            check_params_cb=check_recent_batches_signal,
        ):
            workspace_history.clear_recently_opened()

        # Assert
        assert workspace_history.recently_opened == ()
        assert workspace_history.latest_opened is None
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.set_value(
                WorkspaceSettings.RECENT_BATCHES,
                [],
                workspace_history.recent_batches_changed.emit,
            ),
            mocker.call.end_group(),
        ]


###############################################################################
class TestWorkspaceHistoryLoadFromSettings:
    """Cover populated and absent recent-history values loaded from settings."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_state_transition
    def test_stored_paths_replace_history_and_are_emitted(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        qtbot: QtBot,
        tmp_path: Path,
    ) -> None:
        """Loading stored paths replaces public history and emits the loaded order."""
        # Arrange
        recent_batches_paths = [
            (tmp_path / "newest.json").resolve(),
            (tmp_path / "oldest.json").resolve(),
        ]
        user_settings_mock.value.return_value = recent_batches_paths

        def check_recent_batches_signal(recent_batch_paths: list[Path]) -> bool:
            return recent_batch_paths == recent_batches_paths

        # Act
        with qtbot.waitSignal(
            workspace_history.recent_batches_changed,
            check_params_cb=check_recent_batches_signal,
        ):
            workspace_history.load_from_settings(user_settings_mock)

        # Assert
        assert workspace_history.recently_opened == tuple(recent_batches_paths)
        assert workspace_history.latest_opened == recent_batches_paths[0]
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.value(
                WorkspaceSettings.RECENT_BATCHES,
                [],
            ),
            mocker.call.end_group(),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    def test_missing_setting_loads_and_emits_empty_history(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        qtbot: QtBot,
    ) -> None:
        """An absent stored value uses and emits the supplied empty default."""
        # Arrange
        user_settings_mock.value.return_value = []

        def check_recent_batches_signal(recent_batch_paths: list[Path]) -> bool:
            return recent_batch_paths == []

        # Act
        with qtbot.waitSignal(
            workspace_history.recent_batches_changed,
            check_params_cb=check_recent_batches_signal,
        ):
            workspace_history.load_from_settings(user_settings_mock)

        # Assert
        assert workspace_history.recently_opened == ()
        assert workspace_history.latest_opened is None
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.value(
                WorkspaceSettings.RECENT_BATCHES,
                [],
            ),
            mocker.call.end_group(),
        ]


###############################################################################
class TestWorkspaceHistorySaveToSettings:
    """Cover saving the current history to settings."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_save_to_settings_persists_current_history_and_routes_change_signal(
        self,
        user_settings_mock: NonCallableMagicMock,
        workspace_history: BatchWorkspaceHistory,
        mocker: MockerFixture,
        qtbot: QtBot,
        tmp_path: Path,
    ) -> None:
        """Saving writes current paths and routes confirmed changes through the signal."""
        # Arrange
        recent_batches_paths = [
            (tmp_path / "newest.json").resolve(),
            (tmp_path / "oldest.json").resolve(),
        ]
        workspace_history._recent_batches = list(recent_batches_paths)  # pyright: ignore[reportPrivateUsage]
        user_settings_mock.value.return_value = recent_batches_paths
        user_settings_mock.reset_mock()

        def check_recent_batches_signal(recent_batch_paths: list[Path]) -> bool:
            return recent_batch_paths == recent_batches_paths

        # Act
        with qtbot.waitSignal(
            workspace_history.recent_batches_changed,
            check_params_cb=check_recent_batches_signal,
        ):
            workspace_history.save_to_settings(user_settings_mock)

        # Assert
        assert user_settings_mock.method_calls == [
            mocker.call.begin_group(WorkspaceSettings.SETTINGS_GROUP),
            mocker.call.set_value(
                WorkspaceSettings.RECENT_BATCHES,
                recent_batches_paths,
                workspace_history.recent_batches_changed.emit,
            ),
            mocker.call.end_group(),
        ]
