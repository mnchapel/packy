"""Unit tests for :class:`BatchWorkspace`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
import packy.core.batch_workspace as batch_workspace_module
from packy.core.batch import Batch
from packy.core.batch_workspace import BatchWorkspace
from packy.core.batch_workspace_dialogs import SaveDecision

# Third-party
import pytest
from PySide6.QtWidgets import QWidget

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from collections.abc import Callable
    from pathlib import Path
    from unittest.mock import MagicMock, Mock, NonCallableMagicMock


###############################################################################
### Helpers
###############################################################################
# -----------------------------------------------------------------------------
def check_signal_without_args() -> bool:
    """Return a signal that carries no arguments."""
    return True


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class UserSettingsMocks:
    """Expose UserSettings dependency patched for BatchWorkspace tests."""

    cls: MagicMock
    instance: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class BatchMocks:
    """Expose Batch dependency patched for BatchWorkspace creation tests."""

    cls: MagicMock
    instance: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class BatchWorkspaceDialogsMocks:
    """Expose the dialog collaborator patched at the BatchWorkspace boundary."""

    cls: MagicMock
    instance: MagicMock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class BatchWorkspaceHistoryMocks:
    """Expose the recent-history collaborator patched at the BatchWorkspace boundary."""

    cls: MagicMock
    instance: MagicMock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def user_settings_mocks(mocker: MockerFixture) -> UserSettingsMocks:
    """Patch UserSettings construction performed by BatchWorkspace."""
    # Setup
    user_settings_cls_mock: MagicMock = mocker.patch.object(
        batch_workspace_module,
        "UserSettings",
        autospec=True,
        spec_set=True,
    )
    user_settings_mock: NonCallableMagicMock = user_settings_cls_mock.return_value

    return UserSettingsMocks(
        cls=user_settings_cls_mock,
        instance=user_settings_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_workspace_dialogs_mocks(
    mocker: MockerFixture,
) -> BatchWorkspaceDialogsMocks:
    """Patch the BatchWorkspace dialog collaborator without testing dialog internals."""
    # Setup
    dialogs_cls_mock: MagicMock = mocker.patch.object(
        batch_workspace_module,
        "BatchWorkspaceDialogs",
        autospec=True,
        spec_set=True,
    )
    dialogs_mock: NonCallableMagicMock = dialogs_cls_mock.return_value

    dialogs_mock.choose_new_batch_path.return_value = None
    dialogs_mock.choose_open_batch_path.return_value = None
    dialogs_mock.choose_save_batch_path.return_value = None
    dialogs_mock.confirm_unsaved_changes.return_value = SaveDecision.CANCEL

    return BatchWorkspaceDialogsMocks(
        cls=dialogs_cls_mock,
        instance=dialogs_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_workspace_history_mocks(
    mocker: MockerFixture,
) -> BatchWorkspaceHistoryMocks:
    """Patch recent-history behavior."""
    # Setup
    history_cls_mock: MagicMock = mocker.patch.object(
        batch_workspace_module,
        "BatchWorkspaceHistory",
        autospec=True,
        spec_set=True,
    )
    history_mock: NonCallableMagicMock = history_cls_mock.return_value

    history_mock.recent_batches_changed = mocker.Mock()
    history_mock.latest_opened = None
    history_mock.recently_opened = ()

    return BatchWorkspaceHistoryMocks(
        cls=history_cls_mock,
        instance=history_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_workspace(
    qtbot: QtBot,
    user_settings_mocks: UserSettingsMocks,  # noqa: ARG001 needed as dependency
    batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,  # noqa: ARG001 needed as dependency
    batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,  # noqa: ARG001 needed as dependency
) -> BatchWorkspace:
    """Provide a real workspace with dialog and history collaborators isolated."""
    # Setup
    parent = QWidget()
    qtbot.addWidget(parent)
    workspace = BatchWorkspace(max_recent_batches=3, parent=parent)
    workspace._qt_parent_ref = parent  # pyright: ignore[reportAttributeAccessIssue]
    return workspace


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_mock(mocker: MockerFixture) -> BatchMocks:
    """Replace Batch construction for create_batch scenarios without invoking Batch logic."""
    # Setup
    batch_cls_mock: MagicMock = mocker.patch.object(
        batch_workspace_module,
        "Batch",
        autospec=True,
        spec_set=True,
    )
    batch_cls_mock.default_filename.return_value = "default-batch.json"

    batch_mock: NonCallableMagicMock = batch_cls_mock.return_value
    batch_mock.save.return_value = (True, "")

    return BatchMocks(
        cls=batch_cls_mock,
        instance=batch_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def recent_batches(tmp_path: Path) -> list[Path]:
    """Provide two deterministic recent batch paths."""
    return [
        (tmp_path / "newest.json").resolve(),
        (tmp_path / "older.json").resolve(),
    ]


# -----------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def isolate_qstandard_paths(
    mocker: MockerFixture,
    tmp_path: Path,
) -> Path:
    """Provide a deterministic system documents directory for file dialogs."""
    # Setup
    documents_path = tmp_path / "documents"
    documents_path.mkdir()

    mocker.patch.object(
        batch_workspace_module.QStandardPaths,
        "writableLocation",
        autospec=True,
        return_value=str(documents_path),
    )
    return documents_path


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_factory(tmp_path: Path) -> Callable[[str], Batch]:
    """Provide real lightweight Batch objects with deterministic absolute paths."""

    def create_batch(file_name: str) -> Batch:
        return Batch((tmp_path / file_name).resolve())

    return create_batch


# -----------------------------------------------------------------------------
@pytest.fixture
def batch(batch_factory: Callable[[str], Batch]) -> Batch:
    """Provide a real lightweight batch for workspace state and Qt lifecycle tests."""
    return batch_factory("batch.json")


# -----------------------------------------------------------------------------
@pytest.fixture
def replacement_batch(batch_factory: Callable[[str], Batch]) -> Batch:
    """Provide a second real batch for replacement and transition scenarios."""
    return batch_factory("replacement.json")


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_is_unmodified_mock(mocker: MockerFixture) -> Mock:
    """Make real Batch instances report an unmodified state without using Batch logic."""
    # Setup
    return mocker.patch.object(
        Batch,
        "is_modified",
        new_callable=mocker.PropertyMock,
        return_value=False,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_is_modified_mock(mocker: MockerFixture) -> Mock:
    """Make real Batch instances report a modified state without using Batch logic."""
    # Setup
    return mocker.patch.object(
        Batch,
        "is_modified",
        new_callable=mocker.PropertyMock,
        return_value=True,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def active_batch(
    batch: Batch,
    batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
    batch_workspace: BatchWorkspace,
) -> Batch:
    """Provide a workspace containing one active real batch."""
    # Setup
    assert batch_workspace.activate_batch(batch) is True
    assert batch_workspace.current_batch is batch
    batch_workspace_history_mocks.instance.add_recently_opened.reset_mock()
    return batch


# -----------------------------------------------------------------------------
@pytest.fixture
def unmodified_active_batch(
    batch_is_unmodified_mock: Mock,  # noqa: ARG001 needed as dependency
    active_batch: Batch,
) -> Batch:
    """Provide an active batch observed by the workspace as unmodified."""
    return active_batch


# -----------------------------------------------------------------------------
@pytest.fixture
def modified_active_batch(
    batch_is_modified_mock: Mock,  # noqa: ARG001 needed as dependency
    active_batch: Batch,
) -> Batch:
    """Provide an active batch observed by the workspace as modified."""
    return active_batch


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_save_mock(mocker: MockerFixture) -> Mock:
    """Prevent Batch filesystem writes and default saves to successful completion."""
    # Setup
    return mocker.patch.object(
        batch_workspace_module.Batch,
        "save",
        autospec=True,
        return_value=(True, ""),
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def batch_load_mock(mocker: MockerFixture) -> Mock:
    """Prevent Batch filesystem reads and default loading to the provided real batch."""
    # Setup
    batch = mocker.sentinel.batch
    return mocker.patch.object(
        batch_workspace_module.Batch,
        "load",
        autospec=True,
        return_value=(batch, ""),
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def documents_directory(
    mocker: MockerFixture,
    tmp_path: Path,
) -> Path:
    """Provide a deterministic system documents directory."""
    # Setup
    documents_path = tmp_path / "documents"
    documents_path.mkdir()

    mocker.patch.object(
        batch_workspace_module.QStandardPaths,
        "writableLocation",
        return_value=str(documents_path),
    )
    return documents_path


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestBatchWorkspaceConstruction:
    """Cover workspace construction and collaborator wiring."""

    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_initializes_empty_state_and_qt_identity(
        self,
        user_settings_mocks: UserSettingsMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A new workspace is parented, inactive, and wires its two collaborators."""
        # Assert
        assert isinstance(batch_workspace.parent(), QWidget)
        assert batch_workspace.objectName() == "BatchWorkspace"
        assert batch_workspace.current_batch is None

        user_settings_mocks.cls.assert_called_once_with()
        batch_workspace_dialogs_mocks.cls.assert_called_once_with(batch_workspace.parent())
        batch_workspace_history_mocks.cls.assert_called_once_with(
            3,
            user_settings_mocks.instance,
            batch_workspace,
        )
        recent_batches_connect_mock = (
            batch_workspace_history_mocks.instance.recent_batches_changed.connect
        )
        recent_batches_connect_mock.assert_called_once_with(
            batch_workspace.recent_batches_changed,
        )


###############################################################################
class TestBatchWorkspaceSettings:
    """Cover loading and saving."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_load_settings_delegates_to_history(
        self,
        user_settings_mocks: UserSettingsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """Loading workspace settings delegates the supplied store to recent history."""
        # Act
        batch_workspace.load_settings(user_settings_mocks.instance)

        # Assert
        batch_workspace_history_mocks.instance.load_from_settings.assert_called_once_with(
            user_settings_mocks.instance,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_save_settings_delegates_to_history(
        self,
        user_settings_mocks: UserSettingsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """Saving workspace settings delegates the supplied store to recent history."""
        # Act
        batch_workspace.save_settings(user_settings_mocks.instance)

        # Assert
        batch_workspace_history_mocks.instance.save_to_settings.assert_called_once_with(
            user_settings_mocks.instance,
        )


###############################################################################
class TestBatchWorkspaceCreateBatch:
    """Cover creation orchestration, path normalization, cancellation, and save errors."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_existing_json_path_saves_new_batch(
        self,
        isolate_qstandard_paths: Path,
        batch_mock: BatchMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        tmp_path: Path,
    ) -> None:
        """A selected JSON path is used to construct and save a new batch."""
        # Arrange
        selected_file_path = (tmp_path / "new_batch.json").resolve()
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_new_batch_path.return_value = selected_file_path
        expected_suggested_file_path = (
            isolate_qstandard_paths / batch_mock.cls.default_filename.return_value
        )

        # Act
        created_batch = batch_workspace.create_batch()

        # Assert
        assert created_batch is batch_mock.instance
        batch_mock.cls.assert_called_once_with(selected_file_path)
        batch_mock.instance.save.assert_called_once_with()
        workspace_dialogs.choose_new_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_missing_json_suffix_is_appended_before_save(
        self,
        isolate_qstandard_paths: Path,
        batch_mock: BatchMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        tmp_path: Path,
    ) -> None:
        """A creation destination without .json is normalized by BatchWorkspace."""
        # Arrange
        selected_file_path = (tmp_path / "new_batch").resolve()
        expected_selected_file_path = selected_file_path.with_name("new_batch.json")
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_new_batch_path.return_value = selected_file_path
        expected_suggested_file_path = (
            isolate_qstandard_paths / batch_mock.cls.default_filename.return_value
        )

        # Act
        created_batch = batch_workspace.create_batch()

        # Assert
        assert created_batch is batch_mock.instance
        batch_mock.cls.assert_called_once_with(expected_selected_file_path)
        batch_mock.instance.save.assert_called_once_with()
        workspace_dialogs.choose_new_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_with_recent_batch_suggests_latest_batch_directory(
        self,
        batch_mock: BatchMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        recent_batches: list[Path],
    ) -> None:
        """The latest history path determines the initial directory for creation."""
        # Arrange
        latest_batch = recent_batches[0]
        batch_workspace_history_mocks.instance.latest_opened = latest_batch
        selected_file_path = latest_batch.parent / "new_batch.json"
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_new_batch_path.return_value = selected_file_path
        expected_suggested_file_path = (
            latest_batch.parent / batch_mock.cls.default_filename.return_value
        )

        # Act
        created_batch = batch_workspace.create_batch()

        # Assert
        assert created_batch is batch_mock.instance
        batch_mock.cls.assert_called_once_with(selected_file_path)
        batch_mock.instance.save.assert_called_once_with()
        workspace_dialogs.choose_new_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_without_recent_batch_suggests_standard_documents_directory(
        self,
        isolate_qstandard_paths: Path,
        batch_mock: BatchMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """An empty history makes the system documents directory the creation default."""
        # Arrange
        batch_workspace_history_mocks.instance.latest_opened = None
        selected_file_path = isolate_qstandard_paths / "new_batch.json"
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_new_batch_path.return_value = selected_file_path
        expected_suggested_path = (
            isolate_qstandard_paths / batch_mock.cls.default_filename.return_value
        )

        # Act
        created_batch = batch_workspace.create_batch()

        # Assert
        assert created_batch is batch_mock.instance
        batch_mock.cls.assert_called_once_with(selected_file_path)
        batch_mock.instance.save.assert_called_once_with()
        workspace_dialogs.choose_new_batch_path.assert_called_once_with(
            expected_suggested_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_canceled_dialog_returns_none_without_creating_batch(
        self,
        batch_mock: BatchMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A canceled creation selection returns None without constructing a Batch."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_new_batch_path.return_value = None

        # Act
        created_batch = batch_workspace.create_batch()

        # Assert
        assert created_batch is None
        batch_mock.cls.assert_not_called()
        batch_mock.instance.save.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_initial_save_error_returns_none_and_delegates_error_display(
        self,
        batch_mock: BatchMocks,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        tmp_path: Path,
    ) -> None:
        """A failed initial save reports the path and error through the dialog collaborator."""
        # Arrange
        selected_file_path = (tmp_path / "new_batch.json").resolve()
        error = "random error"
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_new_batch_path.return_value = selected_file_path
        batch_mock.instance.save.return_value = (False, error)

        # Act
        created_batch = batch_workspace.create_batch()

        # Assert
        assert created_batch is None

        batch_mock.cls.assert_called_once_with(selected_file_path)
        batch_mock.instance.save.assert_called_once_with()

        workspace_dialogs.show_save_error.assert_called_once_with(
            selected_file_path,
            error,
        )


###############################################################################
class TestBatchWorkspaceOpenLastBatch:
    """Cover opening the path exposed as latest by the history collaborator."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_last_batch_is_loaded_and_activated(
        self,
        batch_load_mock: Mock,
        batch: Batch,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """The latest history path is loaded and becomes the active batch."""
        # Arrange
        batch_load_mock.return_value = (batch, "")
        batch_workspace_history_mocks.instance.latest_opened = batch.file_path

        # Act
        is_batch_open = batch_workspace.open_last_batch()

        # Assert
        assert is_batch_open is True
        assert batch_workspace.current_batch is batch
        batch_load_mock.assert_called_once_with(batch.file_path)
        batch_workspace_history_mocks.instance.add_recently_opened.assert_called_once_with(
            batch.file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_without_recent_batch_returns_false_without_loading(
        self,
        batch_load_mock: Mock,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """An empty history cannot provide a last batch to open."""
        # Arrange
        batch_workspace_history_mocks.instance.latest_opened = None

        # Act
        is_batch_open = batch_workspace.open_last_batch()

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is None
        batch_load_mock.assert_not_called()
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_load_error_returns_false(
        self,
        batch_load_mock: Mock,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        recent_batches: list[Path],
    ) -> None:
        """A loader failure for the latest path leaves the workspace inactive."""
        # Arrange
        latest_batch = recent_batches[0]
        batch_workspace_history_mocks.instance.latest_opened = latest_batch
        batch_load_mock.return_value = (None, "invalid JSON")

        # Act
        is_batch_open = batch_workspace.open_last_batch()

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is None
        batch_load_mock.assert_called_once_with(latest_batch)
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()


###############################################################################
class TestBatchWorkspaceOpenRecentBatch:
    """Cover membership checking and opening through the history collaborator."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_history_path_loads_and_activates(
        self,
        batch_load_mock: Mock,
        batch: Batch,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A path exposed by recent history is loaded and activated."""
        # Arrange
        batch_load_mock.return_value = (batch, "")
        batch_workspace_history_mocks.instance.recently_opened = (batch.file_path,)

        # Act
        is_batch_open = batch_workspace.open_recent_batch(batch.file_path)

        # Assert
        assert is_batch_open is True
        assert batch_workspace.current_batch is batch
        batch_load_mock.assert_called_once_with(batch.file_path)
        batch_workspace_history_mocks.instance.add_recently_opened.assert_called_once_with(
            batch.file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_path_outside_history_returns_false_without_loading(
        self,
        batch_load_mock: Mock,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        tmp_path: Path,
    ) -> None:
        """A path absent from history is rejected before filesystem loading."""
        # Arrange
        requested_path = (tmp_path / "unknown.json").resolve()
        batch_workspace_history_mocks.instance.recently_opened = ()

        # Act
        is_batch_open = batch_workspace.open_recent_batch(requested_path)

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is None
        batch_load_mock.assert_not_called()
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_load_error_returns_false(
        self,
        batch_load_mock: Mock,
        batch: Batch,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A known recent path that cannot be loaded leaves the workspace inactive."""
        # Arrange
        batch_workspace_history_mocks.instance.recently_opened = (batch.file_path,)
        batch_load_mock.return_value = (None, "random error")

        # Act
        is_batch_open = batch_workspace.open_recent_batch(batch.file_path)

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is None
        batch_load_mock.assert_called_once_with(batch.file_path)
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()


###############################################################################
class TestBatchWorkspaceOpenBatch:
    """Cover dialog-result handling, loading, activation, and open-error delegation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_selected_file_loads_and_activates(
        self,
        isolate_qstandard_paths: Path,
        batch_load_mock: Mock,
        batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A selected readable file is loaded and becomes the active batch."""
        # Arrange
        batch_load_mock.return_value = (batch, "")
        selected_file_path = batch.file_path
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_open_batch_path.return_value = selected_file_path
        expected_suggested_file_path = isolate_qstandard_paths

        # Act
        is_batch_open = batch_workspace.open_batch()

        # Assert
        assert is_batch_open is True
        assert batch_workspace.current_batch is batch
        batch_load_mock.assert_called_once_with(selected_file_path)
        workspace_dialogs.choose_open_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )
        batch_workspace_history_mocks.instance.add_recently_opened.assert_called_once_with(
            selected_file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_canceled_dialog_returns_false_without_loading(
        self,
        isolate_qstandard_paths: Path,
        batch_load_mock: Mock,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A canceled open selection returns False without loading a batch."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_open_batch_path.return_value = None
        expected_suggested_file_path = isolate_qstandard_paths

        # Act
        is_batch_open = batch_workspace.open_batch()

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is None
        batch_load_mock.assert_not_called()
        workspace_dialogs.choose_open_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_current_file_returns_true_without_reloading(
        self,
        isolate_qstandard_paths: Path,
        batch_load_mock: Mock,
        active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """Selecting the already active path succeeds without invoking the loader."""
        # Arrange
        active_file_path = active_batch.file_path
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_open_batch_path.return_value = active_file_path
        expected_suggested_file_path = isolate_qstandard_paths

        # Act
        is_batch_open = batch_workspace.open_batch()

        # Assert
        assert is_batch_open is True
        assert batch_workspace.current_batch is active_batch
        batch_load_mock.assert_not_called()
        workspace_dialogs.choose_open_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_load_error_returns_false_and_delegates_open_error(
        self,
        isolate_qstandard_paths: Path,
        batch_load_mock: Mock,
        batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """A selected-file load error is delegated to the dialog collaborator."""
        # Arrange
        error = "random error"
        batch_load_mock.return_value = (None, error)
        selected_file_path = batch.file_path
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_open_batch_path.return_value = selected_file_path
        expected_suggested_file_path = isolate_qstandard_paths

        # Act
        is_batch_open = batch_workspace.open_batch()

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is None
        workspace_dialogs.choose_open_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )
        workspace_dialogs.show_open_error.assert_called_once_with(
            selected_file_path,
            error,
        )
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_activation_cancel_returns_false_without_open_error(
        self,
        isolate_qstandard_paths: Path,
        batch_load_mock: Mock,
        replacement_batch: Batch,
        modified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """Canceling replacement is not treated as a file-loading error."""
        # Arrange
        batch_load_mock.return_value = (replacement_batch, "")
        selected_file_path = replacement_batch.file_path
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_open_batch_path.return_value = selected_file_path
        workspace_dialogs.confirm_unsaved_changes.return_value = SaveDecision.CANCEL
        expected_suggested_file_path = isolate_qstandard_paths

        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace

        # Act
        is_batch_open = batch_workspace.open_batch()

        # Assert
        assert is_batch_open is False
        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace
        assert replacement_batch.parent() is None
        batch_load_mock.assert_called_once_with(selected_file_path)
        workspace_dialogs.choose_open_batch_path.assert_called_once_with(
            expected_suggested_file_path,
        )
        workspace_dialogs.confirm_unsaved_changes.assert_called_once_with()
        workspace_dialogs.show_open_error.assert_not_called()


###############################################################################
class TestBatchWorkspaceCurrentBatch:
    """Test the current batch state exposed by the workspace."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_has_no_current_batch_when_workspace_is_empty(
        self,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """An empty workspace reports no current batch."""
        # Act / Assert
        assert batch_workspace.current_batch is None
        assert batch_workspace.has_current_batch() is False

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_has_current_batch_when_batch_is_active(
        self,
        active_batch: Batch,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """An active batch is returned and reported as the current batch."""
        # Act / Assert
        assert batch_workspace.current_batch is active_batch
        assert batch_workspace.has_current_batch() is True

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    def test_current_batch_property_cannot_be_assigned(
        self,
        batch_workspace: BatchWorkspace,
    ) -> None:
        """The current batch property cannot be replaced directly by callers."""
        # Act / Assert
        with pytest.raises(AttributeError):
            batch_workspace.current_batch = None  # pyright: ignore[reportAttributeAccessIssue]


###############################################################################
class TestBatchWorkspaceActivation:
    """Cover active-batch installation, replacement, cancellation, and signals."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_first_batch_becomes_active_emits_and_updates_recent_history(
        self,
        batch: Batch,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Activating the first batch parents it, emits, and delegates the MRU update."""
        # Arrange
        assert batch_workspace.current_batch is None

        def check_batch_opened_signal(new_batch: Batch) -> bool:
            return new_batch == batch

        # Act
        with qtbot.waitSignal(
            batch_workspace.batch_opened,
            check_params_cb=check_batch_opened_signal,
        ):
            is_batch_activate = batch_workspace.activate_batch(batch)

        # Assert
        assert is_batch_activate is True
        assert batch_workspace.current_batch is batch
        assert batch.parent() is batch_workspace
        batch_workspace_history_mocks.instance.add_recently_opened.assert_called_once_with(
            batch.file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_same_batch_returns_false_without_state_change(
        self,
        active_batch: Batch,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Reactivating the same Batch is rejected without another history update."""
        # Arrange
        assert batch_workspace.current_batch is active_batch
        assert active_batch.parent() is batch_workspace

        # Act
        with qtbot.assertNotEmitted(batch_workspace.batch_opened):
            is_batch_activate = batch_workspace.activate_batch(active_batch)

        # Assert
        assert is_batch_activate is False
        assert batch_workspace.current_batch is active_batch
        assert active_batch.parent() is batch_workspace
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_replacement_closes_old_and_activates_new(
        self,
        batch: Batch,
        replacement_batch: Batch,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Replacing a clean active batch closes it before installing the new one."""
        # Arrange
        assert batch_workspace.activate_batch(batch) is True
        assert batch_workspace.current_batch is batch
        assert batch.parent() is batch_workspace
        assert batch.is_modified is False
        batch_workspace_history_mocks.instance.add_recently_opened.reset_mock()

        def check_batch_closed_signal(old_batch: Batch) -> bool:
            return old_batch == batch

        def check_batch_opened_signal(new_batch: Batch) -> bool:
            return new_batch == replacement_batch

        # Act
        with (
            qtbot.waitSignals(
                [
                    batch_workspace.batch_closed,
                    batch_workspace.batch_opened,
                ],
                check_params_cbs=[
                    check_batch_closed_signal,
                    check_batch_opened_signal,
                ],
                order="strict",
            ),
        ):
            is_batch_activate = batch_workspace.activate_batch(replacement_batch)

        # Assert
        assert is_batch_activate is True
        assert batch.parent() is None
        assert batch_workspace.current_batch is replacement_batch
        assert replacement_batch.parent() is batch_workspace
        batch_workspace_history_mocks.instance.add_recently_opened.assert_called_once_with(
            replacement_batch.file_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_close_cancellation_preserves_existing_batch(
        self,
        replacement_batch: Batch,
        modified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace_history_mocks: BatchWorkspaceHistoryMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """A canceled close prevents replacement and preserves the existing active batch."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.confirm_unsaved_changes.return_value = SaveDecision.CANCEL
        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_closed),
            qtbot.assertNotEmitted(batch_workspace.batch_opened),
        ):
            is_batch_activate = batch_workspace.activate_batch(replacement_batch)

        # Assert
        assert is_batch_activate is False
        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace
        assert replacement_batch.parent() is None
        workspace_dialogs.confirm_unsaved_changes.assert_called_once_with()
        batch_workspace_history_mocks.instance.add_recently_opened.assert_not_called()


###############################################################################
class TestBatchWorkspaceSaveCurrentBatch:
    """Cover saving the active batch and delegating save errors."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_successful_save_returns_true_and_emits_signal(
        self,
        batch_save_mock: Mock,
        active_batch: Batch,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """A successful active-batch save returns True and emits batch_saved."""
        # Arrange
        assert batch_workspace.current_batch is active_batch
        assert active_batch.parent() is batch_workspace

        # Act
        with qtbot.waitSignal(
            batch_workspace.batch_saved,
            check_params_cb=check_signal_without_args,
        ):
            is_batch_saved = batch_workspace.save_current_batch()

        # Assert
        assert is_batch_saved is True
        batch_save_mock.assert_called_once_with(active_batch)

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_without_current_batch_returns_false(
        self,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Saving without an active batch returns False."""
        # Arrange
        assert batch_workspace.current_batch is None

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
        ):
            is_batch_saved = batch_workspace.save_current_batch()

        # Assert
        assert is_batch_saved is False
        assert batch_workspace.current_batch is None

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_save_error_returns_false_and_delegates_error_display(
        self,
        batch_save_mock: Mock,
        active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """A failed active-batch save delegates the exact path and error to dialogs."""
        # Arrange
        error = "randomn error"
        batch_save_mock.return_value = (False, error)
        workspace_dialogs = batch_workspace_dialogs_mocks.instance

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
        ):
            is_batch_saved = batch_workspace.save_current_batch()

        # Assert
        assert is_batch_saved is False
        batch_save_mock.assert_called_once_with(active_batch)
        workspace_dialogs.show_save_error.assert_called_once_with(
            active_batch.file_path,
            error,
        )


###############################################################################
class TestBatchWorkspaceSaveCurrentBatchAs:
    """Cover Save As orchestration without testing dialog-internal validation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_selected_destination_is_saved_exactly_and_emits_signal(
        self,
        isolate_qstandard_paths: Path,
        batch_save_mock: Mock,
        active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
        tmp_path: Path,
    ) -> None:
        """BatchWorkspace trusts the destination returned by its dialog collaborator."""
        # Arrange
        selected_file_path = (tmp_path / "copy.json").resolve()
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_save_batch_path.return_value = selected_file_path
        expected_suggested_path = isolate_qstandard_paths / Batch.default_filename()

        # Act
        with qtbot.waitSignal(
            batch_workspace.batch_saved,
            check_params_cb=check_signal_without_args,
        ):
            is_batch_saved = batch_workspace.save_current_batch_as()

        # Assert
        assert is_batch_saved is True
        batch_save_mock.assert_called_once_with(active_batch, selected_file_path)
        workspace_dialogs.choose_save_batch_path.assert_called_once_with(
            expected_suggested_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_without_current_batch_returns_false_without_asking_for_path(
        self,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Saving as without an active batch returns before using the dialog collaborator."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        assert batch_workspace.current_batch is None

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
        ):
            is_batch_saved = batch_workspace.save_current_batch_as()

        # Assert
        assert is_batch_saved is False
        workspace_dialogs.choose_save_batch_path.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_canceled_dialog_returns_false_without_saving(
        self,
        isolate_qstandard_paths: Path,
        batch_save_mock: Mock,
        active_batch: Batch,  # noqa: ARG002 needed to have an activated batch in workspace
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """A canceled Save As selection leaves the active batch unsaved."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_save_batch_path.return_value = None
        expected_suggested_path = isolate_qstandard_paths / Batch.default_filename()

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
        ):
            is_batch_saved = batch_workspace.save_current_batch_as()

        # Assert
        assert is_batch_saved is False
        batch_save_mock.assert_not_called()
        workspace_dialogs.choose_save_batch_path.assert_called_once_with(
            expected_suggested_path,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_save_error_returns_false_and_delegates_error_display(
        self,
        batch_save_mock: Mock,
        active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """A failed Save As delegates its selected destination and error to dialogs."""
        # Arrange
        selected_file_path = (tmp_path / "copy.json").resolve()
        error = "random error"
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.choose_save_batch_path.return_value = selected_file_path
        batch_save_mock.return_value = (False, error)

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
        ):
            is_batch_saved = batch_workspace.save_current_batch_as()

        # Assert
        assert is_batch_saved is False
        batch_save_mock.assert_called_once_with(active_batch, selected_file_path)
        workspace_dialogs.show_save_error.assert_called_once_with(
            selected_file_path,
            error,
        )


###############################################################################
class TestBatchWorkspaceCloseCurrentBatch:
    """Cover closing clean and modified batches across save, discard, and cancel."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_without_current_batch_returns_true(
        self,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Closing an already empty workspace succeeds without prompting."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        assert batch_workspace.current_batch is None

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_closed),
        ):
            is_batch_closed = batch_workspace.close_current_batch()

        # Assert
        assert is_batch_closed is True
        assert batch_workspace.current_batch is None
        workspace_dialogs.confirm_unsaved_changes.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_unmodified_batch_closes_without_prompt_and_emits_signal(
        self,
        mocker: MockerFixture,
        unmodified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """An unmodified batch closes without consulting the dialog collaborator."""
        # Arrange
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        disconnect_spy = mocker.spy(unmodified_active_batch, "disconnect")
        assert batch_workspace.current_batch is unmodified_active_batch
        assert unmodified_active_batch.parent() is batch_workspace

        def check_batch_closed_signal(old_batch: Batch) -> bool:
            return old_batch == unmodified_active_batch

        # Act
        with qtbot.waitSignal(
            batch_workspace.batch_closed,
            check_params_cb=check_batch_closed_signal,
        ):
            is_batch_closed = batch_workspace.close_current_batch()

        # Assert
        assert is_batch_closed is True
        assert batch_workspace.current_batch is None
        assert unmodified_active_batch.parent() is None
        disconnect_spy.assert_called_once_with(batch_workspace)
        workspace_dialogs.confirm_unsaved_changes.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_modified_save_choice_closes_after_successful_save(
        self,
        mocker: MockerFixture,
        batch_save_mock: Mock,
        modified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Choosing Save closes a modified batch when its save succeeds."""
        # Arrange
        disconnect_spy = mocker.spy(modified_active_batch, "disconnect")
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.confirm_unsaved_changes.return_value = SaveDecision.SAVE
        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace

        def check_batch_closed_signal(old_batch: Batch) -> bool:
            return old_batch == modified_active_batch

        # Act
        with (
            qtbot.waitSignals(
                [
                    batch_workspace.batch_saved,
                    batch_workspace.batch_closed,
                ],
                check_params_cbs=[
                    check_signal_without_args,
                    check_batch_closed_signal,
                ],
                order="strict",
            ),
        ):
            is_batch_closed = batch_workspace.close_current_batch()

        # Assert
        assert is_batch_closed is True
        assert batch_workspace.current_batch is None
        assert modified_active_batch.parent() is None
        batch_save_mock.assert_called_once_with(modified_active_batch)
        disconnect_spy.assert_called_once_with(batch_workspace)
        workspace_dialogs.confirm_unsaved_changes.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_modified_save_choice_preserves_batch_when_save_errors(
        self,
        mocker: MockerFixture,
        batch_save_mock: Mock,
        modified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """A failed requested save cancels closing and preserves the active batch."""
        # Arrange
        error = "random error"
        batch_save_mock.return_value = (False, error)
        disconnect_spy = mocker.spy(modified_active_batch, "disconnect")
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.confirm_unsaved_changes.return_value = SaveDecision.SAVE

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
            qtbot.assertNotEmitted(batch_workspace.batch_closed),
        ):
            is_batch_closed = batch_workspace.close_current_batch()

        # Assert
        assert is_batch_closed is False
        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace
        batch_save_mock.assert_called_once_with(modified_active_batch)
        disconnect_spy.assert_not_called()
        workspace_dialogs.confirm_unsaved_changes.assert_called_once_with()
        workspace_dialogs.show_save_error.assert_called_once_with(
            modified_active_batch.file_path,
            error,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_modified_discard_choice_closes_without_saving(
        self,
        mocker: MockerFixture,
        batch_save_mock: Mock,
        modified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Choosing Discard closes a modified batch without saving it."""
        # Arrange
        disconnect_spy = mocker.spy(modified_active_batch, "disconnect")
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.confirm_unsaved_changes.return_value = SaveDecision.DISCARD

        def check_batch_closed_signal(old_batch: Batch) -> bool:
            return old_batch == modified_active_batch

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
            qtbot.waitSignal(
                batch_workspace.batch_closed,
                check_params_cb=check_batch_closed_signal,
            ),
        ):
            is_batch_closed = batch_workspace.close_current_batch()

        # Assert
        assert is_batch_closed is True
        assert batch_workspace.current_batch is None
        assert modified_active_batch.parent() is None
        disconnect_spy.assert_called_once_with(batch_workspace)
        batch_save_mock.assert_not_called()
        workspace_dialogs.confirm_unsaved_changes.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_modified_cancel_choice_preserves_active_batch(
        self,
        mocker: MockerFixture,
        batch_save_mock: Mock,
        modified_active_batch: Batch,
        batch_workspace_dialogs_mocks: BatchWorkspaceDialogsMocks,
        batch_workspace: BatchWorkspace,
        qtbot: QtBot,
    ) -> None:
        """Choosing Cancel leaves a modified batch active and attached."""
        # Arrange
        disconnect_spy = mocker.spy(modified_active_batch, "disconnect")
        workspace_dialogs = batch_workspace_dialogs_mocks.instance
        workspace_dialogs.confirm_unsaved_changes.return_value = SaveDecision.CANCEL

        # Act
        with (
            qtbot.assertNotEmitted(batch_workspace.batch_saved),
            qtbot.assertNotEmitted(batch_workspace.batch_closed),
        ):
            is_batch_closed = batch_workspace.close_current_batch()

        # Assert
        assert is_batch_closed is False
        assert batch_workspace.current_batch is modified_active_batch
        assert modified_active_batch.parent() is batch_workspace
        disconnect_spy.assert_not_called()
        batch_save_mock.assert_not_called()
        workspace_dialogs.confirm_unsaved_changes.assert_called_once_with()
