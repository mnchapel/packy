"""Unit tests for :class:`BatchWorkspaceDialogs`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
import packy.core.batch_workspace_dialogs as bw_dialogs_module
from packy.constants.file_filters import FileFilter
from packy.core.batch_workspace import SaveDecision
from packy.core.batch_workspace_dialogs import BatchWorkspaceDialogs

# Third-party
import pytest
from PySide6.QtWidgets import QMessageBox, QWidget

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from pathlib import Path
    from unittest.mock import MagicMock


###############################################################################
### Test Contexts
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class QtDialogsContext:
    """Expose batch dialogs with their real Qt parent and translated filters."""

    parent: QWidget
    workspace_dialogs: BatchWorkspaceDialogs
    batch_file_filter: str
    files_filter: str


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
    """Expose blocking message-box operations patched for BatchWorkspace tests."""

    critical: MagicMock
    warning: MagicMock
    exec: MagicMock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def qt_file_dialog_mocks(mocker: MockerFixture) -> QtFileDialogMocks:
    """Patch blocking native file dialogs with canceled responses by default."""
    # Setup
    get_save_file_name_mock: MagicMock = mocker.patch.object(
        bw_dialogs_module.QFileDialog,
        "getSaveFileName",
        autospec=True,
        return_value=("", ""),
    )
    get_open_file_name_mock: MagicMock = mocker.patch.object(
        bw_dialogs_module.QFileDialog,
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
    critical_mock: MagicMock = mocker.patch.object(
        bw_dialogs_module.QMessageBox,
        "critical",
        autospec=True,
    )
    warning_mock: MagicMock = mocker.patch.object(
        bw_dialogs_module.QMessageBox,
        "warning",
        autospec=True,
        return_value=QMessageBox.StandardButton.Cancel,
    )
    exec_mock: MagicMock = mocker.patch.object(
        bw_dialogs_module.QMessageBox,
        "exec",
        autospec=True,
        return_value=QMessageBox.StandardButton.Yes,
    )

    return QtMessageBoxMocks(
        critical=critical_mock,
        warning=warning_mock,
        exec=exec_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def qt_dialogs_context(mocker: MockerFixture, qtbot: QtBot) -> QtDialogsContext:
    """Provide batch dialogs with deterministic translation and a real Qt parent."""

    # Setup
    def translate(context: str, source_text: str) -> str:
        return f"{context}:{source_text}"

    mocker.patch.object(
        bw_dialogs_module.QCoreApplication,
        "translate",
        side_effect=translate,
    )

    parent = QWidget()
    qtbot.addWidget(parent)

    batch_file_filter = f"BatchWorkspaceDialogs:{FileFilter.BATCH_FILE}"
    files_filter = f"BatchWorkspaceDialogs:{FileFilter.ALL_FILES};;{batch_file_filter}"

    return QtDialogsContext(
        parent=parent,
        workspace_dialogs=BatchWorkspaceDialogs(parent),
        batch_file_filter=batch_file_filter,
        files_filter=files_filter,
    )


###############################################################################
### Tests
###############################################################################
class TestWorkspaceDialogsChooseNewBatchPath:
    """Cover new-batch path selection and cancellation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_selected_path_returns_resolved_path(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        tmp_path: Path,
    ) -> None:
        """A selected new-batch destination is returned as a resolved path."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        expected_selected_file_path = (tmp_path / "new_batch.json").resolve()
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        save_dialog_mock = qt_file_dialog_mocks.get_save_file_name
        save_dialog_mock.return_value = (
            str(expected_selected_file_path),
            qt_dialogs_context.batch_file_filter,
        )

        # Act
        selected_file_path = workspace_dialogs.choose_new_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path == expected_selected_file_path
        args = save_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_canceled_dialog_returns_none(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        tmp_path: Path,
    ) -> None:
        """Canceling new-batch selection returns no destination."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        save_dialog_mock = qt_file_dialog_mocks.get_save_file_name
        save_dialog_mock.return_value = (
            "",
            "",
        )

        # Act
        selected_file_path = workspace_dialogs.choose_new_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path is None
        args = save_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter


###############################################################################
class TestWorkspaceDialogsChooseOpenBatchPath:
    """Cover existing-batch path selection and cancellation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_selected_path_returns_resolved_path(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        tmp_path: Path,
    ) -> None:
        """A selected existing batch is returned as a resolved path."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        expected_selected_file_path = (tmp_path / "new_batch.json").resolve()
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        open_dialog_mock = qt_file_dialog_mocks.get_open_file_name
        open_dialog_mock.return_value = (
            str(expected_selected_file_path),
            qt_dialogs_context.batch_file_filter,
        )

        # Act
        selected_file_path = workspace_dialogs.choose_open_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path == expected_selected_file_path
        args = open_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_canceled_dialog_returns_none(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        tmp_path: Path,
    ) -> None:
        """Canceling existing-batch selection returns no path."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        open_dialog_mock = qt_file_dialog_mocks.get_open_file_name
        open_dialog_mock.return_value = (
            "",
            "",
        )

        # Act
        selected_file_path = workspace_dialogs.choose_open_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path is None
        args = open_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter


###############################################################################
class TestWorkspaceDialogsChooseSaveBatchPath:
    """Cover save destinations, extension confirmation, retry, and cancellation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_json_path_returns_resolved_path_without_confirmation(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        qt_message_box_mocks: QtMessageBoxMocks,
        tmp_path: Path,
    ) -> None:
        """A JSON destination is accepted without extension confirmation."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        expected_selected_file_path = (tmp_path / "new_batch.json").resolve()
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        save_dialog_mock = qt_file_dialog_mocks.get_save_file_name
        save_dialog_mock.return_value = (
            str(expected_selected_file_path),
            qt_dialogs_context.batch_file_filter,
        )
        message_exec_mock = qt_message_box_mocks.exec

        # Act
        selected_file_path = workspace_dialogs.choose_save_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path == expected_selected_file_path
        args = save_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter
        message_exec_mock.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_extension_mismatch_confirmed_returns_resolved_path(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        qt_message_box_mocks: QtMessageBoxMocks,
        tmp_path: Path,
    ) -> None:
        """Confirming an extension mismatch accepts the selected destination."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        expected_selected_file_path = (tmp_path / "new_batch.txt").resolve()
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        save_dialog_mock = qt_file_dialog_mocks.get_save_file_name
        save_dialog_mock.return_value = (
            str(expected_selected_file_path),
            qt_dialogs_context.batch_file_filter,
        )
        message_box_exec_mock = qt_message_box_mocks.exec
        message_box_exec_mock.return_value = QMessageBox.StandardButton.Yes

        # Act
        selected_file_path = workspace_dialogs.choose_save_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path == expected_selected_file_path
        args = save_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter
        message_box_exec_mock.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_extension_mismatch_declined_reopens_dialog(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        qt_message_box_mocks: QtMessageBoxMocks,
        tmp_path: Path,
    ) -> None:
        """Declining a mismatched extension reopens selection and returns the next path."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        declined_file_path = tmp_path / "declined.txt"
        accepted_file_path = tmp_path / "new_batch.json"
        expected_selected_file_path = (tmp_path / "new_batch.json").resolve()
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        save_dialog_mock = qt_file_dialog_mocks.get_save_file_name
        save_dialog_mock.side_effect = [
            (
                str(declined_file_path),
                qt_dialogs_context.batch_file_filter,
            ),
            (
                str(accepted_file_path),
                qt_dialogs_context.batch_file_filter,
            ),
        ]
        message_box_exec_mock = qt_message_box_mocks.exec
        message_box_exec_mock.return_value = QMessageBox.StandardButton.No

        # Act
        selected_file_path = workspace_dialogs.choose_save_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path == expected_selected_file_path
        assert save_dialog_mock.call_count == 2
        assert save_dialog_mock.call_args_list[0] == save_dialog_mock.call_args_list[1]
        args = save_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter
        message_box_exec_mock.assert_called_once_with()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_canceled_dialog_returns_none_without_confirmation(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_file_dialog_mocks: QtFileDialogMocks,
        qt_message_box_mocks: QtMessageBoxMocks,
        tmp_path: Path,
    ) -> None:
        """Canceling save-as returns no path and opens no extension warning."""
        # Arrange
        suggested_file_path = tmp_path / "default.json"
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        save_dialog_mock = qt_file_dialog_mocks.get_save_file_name
        save_dialog_mock.return_value = (
            "",
            "",
        )
        message_box_exec_mock = qt_message_box_mocks.exec
        message_box_exec_mock.return_value = QMessageBox.StandardButton.Yes

        # Act
        selected_file_path = workspace_dialogs.choose_save_batch_path(suggested_file_path)

        # Assert
        assert selected_file_path is None
        args = save_dialog_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert args[2] == str(suggested_file_path)
        assert args[3] == qt_dialogs_context.files_filter
        assert args[4] == qt_dialogs_context.batch_file_filter
        message_box_exec_mock.assert_not_called()


###############################################################################
class TestWorkspaceDialogsMessageBox:
    """Cover info, warning and error dialogs."""

    # -------------------------------------------------------------------------
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    @pytest.mark.parametrize(
        ("response", "expected_decision"),
        [
            pytest.param(
                QMessageBox.StandardButton.Save,
                SaveDecision.SAVE,
                id="save",
                marks=pytest.mark.scenario_happy_path,
            ),
            pytest.param(
                QMessageBox.StandardButton.Discard,
                SaveDecision.DISCARD,
                id="discard",
                marks=pytest.mark.scenario_alternate_path,
            ),
            pytest.param(
                QMessageBox.StandardButton.Cancel,
                SaveDecision.CANCEL,
                id="cancel",
                marks=pytest.mark.scenario_alternate_path,
            ),
            pytest.param(
                QMessageBox.StandardButton.No,
                SaveDecision.CANCEL,
                id="unexpected-response",
                marks=[
                    pytest.mark.scenario_failure_error_path,
                    pytest.mark.technique_error_guessing,
                ],
            ),
        ],
    )
    def test_confirm_unsaved_changes_maps_response(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_message_box_mocks: QtMessageBoxMocks,
        response: QMessageBox.StandardButton,
        expected_decision: SaveDecision,
    ) -> None:
        """Each message-box response maps to its caller-visible save decision."""
        # Arrange
        workspace_dialogs = qt_dialogs_context.workspace_dialogs

        message_box_warning_mock = qt_message_box_mocks.warning
        message_box_warning_mock.return_value = response

        # Act
        user_response = workspace_dialogs.confirm_unsaved_changes()

        # Assert
        assert user_response is expected_decision
        message_box_warning_mock.assert_called_once()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_show_save_error_displays_file_path_and_error(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_message_box_mocks: QtMessageBoxMocks,
        tmp_path: Path,
    ) -> None:
        """A save failure displays its file path and error in a critical message."""
        # Arrange
        file_path = tmp_path / "unsaved.json"
        error = "Random error"
        workspace_dialogs = qt_dialogs_context.workspace_dialogs
        message_box_critical_mock = qt_message_box_mocks.critical

        # Act
        workspace_dialogs.show_save_error(file_path, error)

        # Assert
        args = message_box_critical_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert str(file_path) in args[2]
        assert error in args[2]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_show_open_error_displays_file_path_and_error(
        self,
        qt_dialogs_context: QtDialogsContext,
        qt_message_box_mocks: QtMessageBoxMocks,
        tmp_path: Path,
    ) -> None:
        """An open failure displays its file path and error in a critical message."""
        # Arrange
        file_path = tmp_path / "unreadable.json"
        error = "Random error"
        workspace_dialogs = qt_dialogs_context.workspace_dialogs
        message_box_critical_mock = qt_message_box_mocks.critical

        # Act
        workspace_dialogs.show_open_error(file_path, error)

        # Assert
        args = message_box_critical_mock.call_args.args
        assert args[0] == qt_dialogs_context.parent
        assert str(file_path) in args[2]
        assert error in args[2]
