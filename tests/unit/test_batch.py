"""Unit tests for :class:`Batch`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
from packy.core.archiver import Archiver
from packy.core.batch import Batch

# Third-party
import pytest
from PySide6.QtCore import QDateTime, QFileInfo, QObject

# Standard library
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from collections.abc import Callable


###############################################################################
### Helpers
###############################################################################
# -----------------------------------------------------------------------------
def check_modified_signal(is_modified: bool) -> bool:  # noqa: FBT001
    """Return whether a modified_changed signal reports a modified batch."""
    return is_modified is True


# -----------------------------------------------------------------------------
def check_unmodified_signal(is_modified: bool) -> bool:  # noqa: FBT001
    """Return whether a modified_changed signal reports an unmodified batch."""
    return is_modified is False


# -----------------------------------------------------------------------------
def check_signal_without_args() -> bool:
    """Return a signal that carries no arguments."""
    return True


# -----------------------------------------------------------------------------
def check_job_signal(expected_job: str) -> Callable[[str], bool]:
    """Return a signal predicate matching one expected job."""

    def check_job(job: str) -> bool:
        return job == expected_job

    return check_job


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class SavedState:
    """Represent the observable batch state when saved is emitted."""

    file_path: Path
    is_modified: bool
    last_saved: QDateTime


# -----------------------------------------------------------------------------
def capture_saved_states(batch: Batch) -> list[SavedState]:
    """Capture the public batch state whenever saved is emitted."""
    saved_states: list[SavedState] = []

    def capture() -> None:
        saved_states.append(
            SavedState(
                file_path=batch.file_path,
                is_modified=batch.is_modified,
                last_saved=batch.last_saved,
            ),
        )

    batch.saved.connect(capture)
    return saved_states


###############################################################################
### Tests
###############################################################################
type ArchiverSettingValue = Archiver.Format | Archiver.CompressionLevel | Archiver.CompressionMethod


###############################################################################
class TestArchiverSettings:
    """Cover the public defaults and text representations of archiver settings."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_defaults_match_archiver_defaults(self) -> None:
        """Default construction exposes the documented default archiver values."""
        # Act
        settings = Batch.ArchiverSettings()

        # Assert
        assert settings.format == Archiver.Format.ZIP
        assert settings.compression_level == Archiver.CompressionLevel.NORMAL
        assert settings.compression_method == Archiver.CompressionMethod.STORE

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_text_representations_include_current_values(self) -> None:
        """String, repr, and formatted output expose the current settings values."""
        # Arrange
        settings = Batch.ArchiverSettings()
        expected_repr = (
            "ArchiverSettings(\n"
            f"  format={settings.format!r},\n"
            f"  compression_level={settings.compression_level!r},\n"
            f"  compression_method={settings.compression_method!r}\n"
            ")"
        )
        expected_str = (
            "ArchiverSettings("
            f"{settings.format}, {settings.compression_level}, {settings.compression_method})"
        )

        # Act
        rendered_repr = repr(settings)
        rendered_str = str(settings)
        rendered_format = format(settings, ">80")

        # Assert
        assert rendered_repr == expected_repr
        assert rendered_str == expected_str
        assert rendered_format == format(expected_str, ">80")


###############################################################################
class TestBatch:
    """Cover the static methods."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_default_filename_returns_untitled_batch_json(self) -> None:
        """The default batch filename is the documented untitled JSON filename."""
        # Act
        filename = Batch.default_filename()

        # Assert
        assert filename == "untitled-batch.json"


###############################################################################
class TestBatchConstruction:
    """Cover Batch construction, initial public state, and path validation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_absolute_file_path_initializes_clean_batch(self, tmp_path: Path) -> None:
        """An absolute path creates a clean batch with default settings and Qt metadata."""
        # Arrange
        file_path = tmp_path / "batch.json"
        parent = QObject()

        # Act
        batch = Batch(file_path, parent)

        # Assert
        assert batch.parent() is parent
        assert batch.objectName() == "Batch"
        assert batch.file_path == file_path
        assert batch.display_name == "batch.json"
        assert batch.last_saved.isValid() is False
        assert batch.is_modified is False
        assert batch.archiver_format == Archiver.Format.ZIP
        assert batch.archiver_compression_level == Archiver.CompressionLevel.NORMAL
        assert batch.archiver_compression_method == Archiver.CompressionMethod.STORE
        assert batch.jobs == ()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_equivalence_partitioning
    def test_relative_file_path_raises_assertion_error(self) -> None:
        """A relative construction path is rejected before a Batch is created."""
        # Arrange
        file_path = Path("batch.json")

        # Act / Assert
        with pytest.raises(AssertionError):
            Batch(file_path)


###############################################################################
class TestBatchRepresentation:
    """Cover the formatting and text representations."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_batch_text_representations_include_current_public_state(
        self,
        tmp_path: Path,
    ) -> None:
        """Batch string, repr, and formatted output reflect its current observable state."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        settings = Batch.ArchiverSettings()
        expected_repr = (
            "Batch(\n"
            f"  archiver_settings='{settings!r}', \n"
            f"  file_path={batch.file_path!r}, \n"
            f"  last_saved={batch.last_saved!r}, \n"
            f"  is_modified={batch.is_modified!r}, \n"
            f"  jobs={list(batch.jobs)!r}\n"
            ")"
        )
        expected_str = (
            "Batch("
            f"{settings}, "
            f"{batch.file_path}, "
            f"{batch.last_saved}, "
            f"{batch.is_modified}, "
            f"{list(batch.jobs)})"
        )

        # Act
        rendered_repr = repr(batch)
        rendered_str = str(batch)
        rendered_format = format(batch, ">80")

        # Assert
        assert rendered_repr == expected_repr
        assert rendered_str == expected_str
        assert rendered_format == format(expected_str, ">80")


###############################################################################
class TestBatchArchiverSettingsChanges:
    """Cover archiver-setting assignment and the corresponding Qt change signals."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_state_transition
    @pytest.mark.parametrize(
        ("property_name", "signal_name", "new_value"),
        [
            pytest.param(
                "archiver_format",
                "format_changed",
                Archiver.Format.TAR,
                id="format",
            ),
            pytest.param(
                "archiver_compression_level",
                "compression_level_changed",
                Archiver.CompressionLevel.MAXIMUM,
                id="compression_level",
            ),
            pytest.param(
                "archiver_compression_method",
                "compression_method_changed",
                Archiver.CompressionMethod.DEFLATE,
                id="compression_method",
            ),
        ],
    )
    def test_different_value_updates_property_and_marks_modified(
        self,
        tmp_path: Path,
        qtbot: QtBot,
        property_name: str,
        signal_name: str,
        new_value: ArchiverSettingValue,
    ) -> None:
        """Assigning a different archiver value updates it and emits the old and new values."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        old_value = cast("ArchiverSettingValue", getattr(batch, property_name))
        signal = getattr(batch, signal_name)

        def check_setting_signal(
            actual_old_value: ArchiverSettingValue,
            actual_new_value: ArchiverSettingValue,
        ) -> bool:
            return actual_old_value is old_value and actual_new_value is new_value

        # Act
        with (
            qtbot.waitSignal(
                signal,
                check_params_cb=check_setting_signal,
            ),
            qtbot.waitSignal(
                batch.modified_changed,
                check_params_cb=check_modified_signal,
            ),
        ):
            setattr(batch, property_name, new_value)

        # Assert
        assert getattr(batch, property_name) == new_value
        assert batch.is_modified is True

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.parametrize(
        ("property_name", "signal_name"),
        [
            pytest.param(
                "archiver_format",
                "format_changed",
                id="format",
            ),
            pytest.param(
                "archiver_compression_level",
                "compression_level_changed",
                id="compression_level",
            ),
            pytest.param(
                "archiver_compression_method",
                "compression_method_changed",
                id="compression_method",
            ),
        ],
    )
    def test_same_value_does_not_emit_signal(
        self,
        tmp_path: Path,
        qtbot: QtBot,
        property_name: str,
        signal_name: str,
    ) -> None:
        """Reassigning an archiver value leaves state unchanged without a change signal."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        current_value = cast("ArchiverSettingValue", getattr(batch, property_name))
        signal = getattr(batch, signal_name)

        # Act
        with (
            qtbot.assertNotEmitted(signal),
            qtbot.assertNotEmitted(batch.modified_changed),
        ):
            setattr(batch, property_name, current_value)

        # Assert
        assert getattr(batch, property_name) == current_value
        assert batch.is_modified is False


###############################################################################
class TestBatchSave:
    """Cover successful and failed batch persistence and its observable state transitions."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_same_path_does_not_emit_file_path_changed(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Saving a batch to the current path writes the file without emitting a path-change signal."""
        # Arrange
        file_path = tmp_path / "batch.json"
        batch = Batch(file_path)
        saved_states = capture_saved_states(batch)

        # Act
        with (
            qtbot.assertNotEmitted(batch.file_path_changed),
            qtbot.assertNotEmitted(batch.modified_changed),
            qtbot.waitSignal(batch.saved),
        ):
            result = batch.save()

        # Assert
        expected_last_saved = QFileInfo(file_path).lastModified()
        assert result == (True, "")
        assert file_path.read_text(encoding="utf-8") == "placeholder for futur code"
        assert batch.file_path == file_path
        assert batch.is_modified is False
        assert batch.last_saved == expected_last_saved
        assert saved_states == [
            SavedState(
                file_path=file_path,
                is_modified=False,
                last_saved=expected_last_saved,
            ),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    def test_new_path_resets_state_and_emits_change_signals(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Save-as updates the path, resets modified state, and emits success signals."""
        # Arrange
        old_file_path = tmp_path / "old.json"
        new_file_path = tmp_path / "new.json"
        batch = Batch(old_file_path)
        saved_states = capture_saved_states(batch)

        def check_file_path_changed_signal(
            actual_old_path: Path,
            actual_new_path: Path,
        ) -> bool:
            return actual_old_path == old_file_path and actual_new_path == new_file_path

        # Act
        with (
            qtbot.assertNotEmitted(batch.modified_changed),
            qtbot.waitSignals(
                [
                    batch.file_path_changed,
                    batch.saved,
                ],
                check_params_cbs=[
                    check_file_path_changed_signal,
                    check_signal_without_args,
                ],
                order="strict",
            ),
        ):
            result = batch.save(new_file_path)

        # Assert
        expected_last_saved = QFileInfo(new_file_path).lastModified()
        assert result == (True, "")
        assert new_file_path.read_text(encoding="utf-8") == "placeholder for futur code"
        assert old_file_path.exists() is False
        assert batch.file_path == new_file_path
        assert batch.is_modified is False
        assert batch.last_saved == expected_last_saved
        assert saved_states == [
            SavedState(
                file_path=new_file_path,
                is_modified=False,
                last_saved=expected_last_saved,
            ),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    def test_new_path_modified_batch_emits_change_signals_before_saved(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Save-as updates path and modified state before emitting saved."""
        # Arrange
        old_file_path = tmp_path / "old.json"
        new_file_path = tmp_path / "new.json"
        batch = Batch(old_file_path)
        batch._is_modified = True # pyright: ignore[reportPrivateUsage]
        saved_states = capture_saved_states(batch)

        def check_file_path_changed_signal(
            actual_old_path: Path,
            actual_new_path: Path,
        ) -> bool:
            return actual_old_path == old_file_path and actual_new_path == new_file_path

        # Act
        with qtbot.waitSignals(
            [
                batch.file_path_changed,
                batch.modified_changed,
                batch.saved,
            ],
            check_params_cbs=[
                check_file_path_changed_signal,
                check_unmodified_signal,
                check_signal_without_args,
            ],
            order="strict",
        ):
            result = batch.save(new_file_path)

        # Assert
        expected_last_saved = QFileInfo(new_file_path).lastModified()
        assert result == (True, "")
        assert new_file_path.read_text(encoding="utf-8") == "placeholder for futur code"
        assert old_file_path.exists() is False
        assert batch.file_path == new_file_path
        assert batch.is_modified is False
        assert batch.last_saved == expected_last_saved
        assert saved_states == [
            SavedState(
                file_path=new_file_path,
                is_modified=False,
                last_saved=expected_last_saved,
            ),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_state_transition
    def test_modified_batch_resets_modified_state(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """A successful save resets a modified batch to the unmodified state."""
        # Arrange
        file_path = tmp_path / "batch.json"
        batch = Batch(file_path)
        batch._is_modified = True # pyright: ignore[reportPrivateUsage]
        saved_states = capture_saved_states(batch)

        # Act
        with (
            qtbot.assertNotEmitted(batch.file_path_changed),
            qtbot.waitSignals(
                [
                    batch.modified_changed,
                    batch.saved,
                ],
                check_params_cbs=[
                    check_unmodified_signal,
                    check_signal_without_args,
                ],
                order="strict",
            ),
        ):
            result = batch.save()

        # Assert
        assert result == (True, "")
        assert batch.is_modified is False
        assert saved_states == [
            SavedState(
                file_path=file_path,
                is_modified=False,
                last_saved=QFileInfo(file_path).lastModified(),
            ),
        ]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_equivalence_partitioning
    def test_relative_destination_raises_assertion_error(self, tmp_path: Path) -> None:
        """Save-as rejects a relative destination before attempting persistence."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        destination = Path("relative.json")

        # Act / Assert
        with pytest.raises(AssertionError):
            batch.save(destination)

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_branch
    def test_write_error_returns_false_and_preserves_state(
        self,
        tmp_path: Path,
        qtbot: QtBot,
        mocker: MockerFixture,
    ) -> None:
        """A write failure returns an error without resetting state or emitting success signals."""
        # Arrange
        file_path = tmp_path / "batch.json"
        batch = Batch(file_path)
        batch._is_modified = True # pyright: ignore[reportPrivateUsage]
        previous_last_saved = batch.last_saved
        mocker.patch.object(
            Path,
            "open",
            autospec=True,
            side_effect=OSError(13, "write denied"),
        )

        # Act
        with (
            qtbot.assertNotEmitted(batch.file_path_changed),
            qtbot.assertNotEmitted(batch.saved),
            qtbot.assertNotEmitted(batch.modified_changed),
        ):
            success, error_msg = batch.save()

        # Assert
        assert success is False
        assert error_msg
        assert str(file_path) in error_msg
        assert "write denied" in error_msg
        assert batch.file_path == file_path
        assert batch.is_modified is True
        assert batch.last_saved == previous_last_saved


###############################################################################
class TestBatchLoad:
    """Cover successful loading and established file-read failure outcomes."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_readable_file_returns_clean_batch_without_applying_content(
        self,
        tmp_path: Path,
    ) -> None:
        """A readable file returns a clean Batch without applying its contents."""
        # Arrange
        file_path = tmp_path / "batch.json"
        file_path.write_text("arbitrary existing content", encoding="utf-8")

        # Act
        loaded_batch, error_msg = Batch.load(file_path)

        # Assert
        assert error_msg == ""
        assert isinstance(loaded_batch, Batch)
        assert loaded_batch.file_path == file_path
        assert loaded_batch.display_name == "batch.json"
        assert loaded_batch.is_modified is False
        assert loaded_batch.archiver_format == Archiver.Format.ZIP
        assert loaded_batch.archiver_compression_level == Archiver.CompressionLevel.NORMAL
        assert loaded_batch.archiver_compression_method == Archiver.CompressionMethod.STORE
        assert loaded_batch.jobs == ()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_missing_file_returns_none_with_message(self, tmp_path: Path) -> None:
        """A missing batch file returns None and an error message containing the requested path."""
        # Arrange
        file_path = tmp_path / "missing.json"

        # Act
        loaded_batch, error_msg = Batch.load(file_path)

        # Assert
        assert loaded_batch is None
        assert error_msg
        assert str(file_path) in error_msg

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_branch
    def test_read_error_returns_none_with_message(
        self,
        tmp_path: Path,
        mocker: MockerFixture,
    ) -> None:
        """An OS read error returns None and reports the path and operating-system error text."""
        # Arrange
        file_path = tmp_path / "batch.json"
        file_path.write_text("arbitrary existing content", encoding="utf-8")
        mocker.patch.object(
            Path,
            "open",
            autospec=True,
            side_effect=OSError(13, "read denied"),
        )

        # Act
        loaded_batch, error_msg = Batch.load(file_path)

        # Assert
        assert loaded_batch is None
        assert error_msg
        assert str(file_path) in error_msg
        assert "read denied" in error_msg


###############################################################################
class TestBatchJobs:
    """Cover ordered job changes, modified-state transitions, and index validation."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_jobs_property_returns_immutable_value(
        self,
        tmp_path: Path,
    ) -> None:
        """The jobs property returns a snapshot unaffected by later job changes."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        batch._jobs = ["first"] # pyright: ignore[reportPrivateUsage]
        original_jobs = batch.jobs

        # Act
        batch._jobs.append("second") # pyright: ignore[reportPrivateUsage]

        # Assert
        assert original_jobs == ("first",)
        assert batch.jobs == ("first", "second")

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    def test_jobs_property_cannot_be_assigned(
        self,
        tmp_path: Path,
    ) -> None:
        """The jobs property cannot be replaced directly by callers."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")

        # Act / Assert
        with pytest.raises(AttributeError):
            batch.jobs = ("replacement",)  # pyright: ignore[reportAttributeAccessIssue]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    def test_first_add_marks_modified_before_emitting_job_added(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Adding the first job marks the batch modified before notifying that the job was added."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")

        added_state: list[bool] = []

        def capture_added_state() -> None:
            added_state.append(batch.is_modified)

        batch.job_added.connect(capture_added_state)

        # Act
        with qtbot.waitSignals(
            [
                batch.modified_changed,
                batch.job_added,
            ],
            check_params_cbs=[
                check_modified_signal,
                check_job_signal("first"),
            ],
            order="strict",
        ):
            batch.add_job("first")

        # Assert
        assert batch.jobs == ("first",)
        assert batch.is_modified is True
        assert added_state == [True]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_add_while_modified_preserves_order_without_second_modified_signal(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Adding while modified preserves order without re-emitting modified_changed."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        batch._jobs = ["first"] # pyright: ignore[reportPrivateUsage]
        batch._is_modified = True # pyright: ignore[reportPrivateUsage]

        # Act
        with (
            qtbot.assertNotEmitted(batch.modified_changed),
            qtbot.waitSignal(batch.job_added, check_params_cb=check_job_signal("second")),
        ):
            batch.add_job("second")

        # Assert
        assert batch.jobs == ("first", "second")
        assert batch.is_modified is True

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_remove_after_save_removes_selected_job_and_marks_batch_modified(
        self,
        tmp_path: Path,
        qtbot: QtBot,
    ) -> None:
        """Removing from a saved batch emits the job and marks the batch modified."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        batch._jobs = ["first", "second"] # pyright: ignore[reportPrivateUsage]
        assert batch.is_modified is False

        removed_state: list[bool] = []

        def capture_removed_state() -> None:
            removed_state.append(batch.is_modified)

        batch.job_removed.connect(capture_removed_state)

        # Act
        with qtbot.waitSignals(
            [
                batch.modified_changed,
                batch.job_removed,
            ],
            check_params_cbs=[
                check_modified_signal,
                check_job_signal("first"),
            ],
            order="strict",
        ):
            batch.remove_job(0)

        # Assert
        assert batch.jobs == ("second",)
        assert batch.is_modified is True
        assert removed_state == [True]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_boundary_value_analysis
    @pytest.mark.parametrize(
        "index",
        [
            pytest.param(-1, id="below_zero"),
            pytest.param(1, id="equal_length"),
        ],
    )
    def test_invalid_index_raises_assertion_error(self, tmp_path: Path, index: int) -> None:
        """An index immediately outside the valid range is rejected without changing the jobs."""
        # Arrange
        batch = Batch(tmp_path / "batch.json")
        batch._jobs = ["only"] # pyright: ignore[reportPrivateUsage]
        original_jobs = batch.jobs

        # Act / Assert
        with pytest.raises(AssertionError):
            batch.remove_job(index)
        assert batch.jobs == original_jobs
