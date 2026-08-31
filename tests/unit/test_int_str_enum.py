"""Unit tests for :class:`IntStrEnum`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Future library
from __future__ import annotations

# Local application
from packy.utils.int_str_enum import IntStrEnum

# Third-party
import pytest

# Standard library
import sys
from enum import IntEnum, auto


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
class ButtonLabel(IntStrEnum):
    """Provide representative explicit and automatic enum members for tests."""

    RUN = (0, "Run")
    RUN_ALL = (1, "Run all")
    PAUSE = (2, "Pause")
    STOP = (3, "Stop")
    RESTART = auto()
    EXIT = auto()


# -----------------------------------------------------------------------------
class NonSequentialLabel(IntStrEnum):
    """Provide non-sequential explicit values to distinguish auto() count behavior."""

    FIRST = (10, "First")
    SECOND = (42, "Second")
    AUTOMATIC = auto()
    NEXT_AUTOMATIC = auto()


# -----------------------------------------------------------------------------
class PlainInt(IntEnum):
    """Provide an IntEnum to verify that IntStrEnum stores plain integers."""

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3


# -----------------------------------------------------------------------------
class PlainIntLabel(IntStrEnum):
    """Provide an IntStrEnum initialized from an IntEnum."""

    ZERO = (PlainInt.ZERO, "Zero")
    ONE = (PlainInt.ONE, "One")
    TWO = (PlainInt.TWO, "Two")
    THREE = (PlainInt.THREE, "Three")


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestIntStrEnumMembers:
    """Tests for values and labels exposed by manually and automatically defined members."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_manual_member_exposes_integer_and_string_values(self) -> None:
        """A manually defined member exposes its enum value, integer value, and string label."""
        # Arrange
        run_member = ButtonLabel.RUN
        stop_member = ButtonLabel.STOP

        # Act
        run_values = (
            run_member.value,
            run_member.int_value,
            run_member.str_value,
        )
        stop_values = (
            stop_member.value,
            stop_member.int_value,
            stop_member.str_value,
        )

        # Assert
        assert type(run_member.value) is int
        assert run_values == (0, 0, "Run")
        assert type(stop_member.value) is int
        assert stop_values == (3, 3, "Stop")

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    def test_auto_members_use_definition_count_and_lowercase_names(self) -> None:
        """Automatic members use definition count for integers and lowercase names for labels."""
        # Arrange
        automatic_member = NonSequentialLabel.AUTOMATIC
        next_automatic_member = NonSequentialLabel.NEXT_AUTOMATIC

        # Act
        automatic_values = (
            automatic_member.value,
            automatic_member.int_value,
            automatic_member.str_value,
        )
        next_automatic_values = (
            next_automatic_member.value,
            next_automatic_member.int_value,
            next_automatic_member.str_value,
        )

        # Assert
        assert automatic_values == (2, 2, "automatic")
        assert next_automatic_values == (3, 3, "next_automatic")

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    def test_intenum_member_return_a_plain_int_value(self) -> None:
        """A member initialized with a IntEnum returns a plain int value."""
        # Arrange
        member = PlainIntLabel.ONE

        # Act / Assert
        assert type(member.value) is int
        assert type(member.int_value) is int
        assert member.value == 1
        assert member.int_value == 1


###############################################################################
class TestIntStrEnumRepresentations:
    """Tests for the public repr, str, and format representations."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_repr_returns_diagnostic_representation(self) -> None:
        """Repr exposes the member name, integer value, and quoted string label."""
        # Act
        result = repr(ButtonLabel.RUN_ALL)

        # Assert
        assert (
            result == "ButtonLabel.RUN_ALL(name='RUN_ALL', value/int_value=1, str_value='Run all')"
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_str_returns_human_readable_representation(self) -> None:
        """Str exposes the member name, integer value, and unquoted string label."""
        # Act
        result = str(ButtonLabel.RUN_ALL)

        # Assert
        assert result == "ButtonLabel.RUN_ALL(1, Run all)"

    # -------------------------------------------------------------------------
    @pytest.mark.parametrize(
        ("format_spec", "expected"),
        [
            pytest.param(
                "",
                "ButtonLabel.RUN_ALL(1, Run all)",
                id="default",
                marks=[
                    pytest.mark.scenario_happy_path,
                    pytest.mark.technique_equivalence_partitioning,
                ],
            ),
            pytest.param(
                ">40",
                "         ButtonLabel.RUN_ALL(1, Run all)",
                id="right-aligned",
                marks=[
                    pytest.mark.scenario_alternate_path,
                    pytest.mark.technique_equivalence_partitioning,
                ],
            ),
            pytest.param(
                "<40",
                "ButtonLabel.RUN_ALL(1, Run all)         ",
                id="left-aligned",
                marks=[
                    pytest.mark.scenario_alternate_path,
                    pytest.mark.technique_equivalence_partitioning,
                ],
            ),
            pytest.param(
                "^40",
                "    ButtonLabel.RUN_ALL(1, Run all)     ",
                id="centered",
                marks=[
                    pytest.mark.scenario_alternate_path,
                    pytest.mark.technique_equivalence_partitioning,
                ],
            ),
        ],
    )
    def test_format_applies_string_format_spec(
        self,
        format_spec: str,
        expected: str,
    ) -> None:
        """Formatting applies the supplied string format specification to the representation."""
        # Arrange
        member = ButtonLabel.RUN_ALL

        # Act
        result = format(member, format_spec)

        # Assert
        assert result == expected


###############################################################################
class TestIntStrEnumLookup:
    """Tests for public Enum lookup behavior established by IntStrEnum integer values."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_integer_value_lookup_returns_matching_member(self) -> None:
        """Looking up an integer value returns the member that exposes that enum value."""
        # Act
        member = ButtonLabel(3)

        # Assert
        assert member is ButtonLabel.STOP

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_iteration_returns_members_in_definition_order(self) -> None:
        """Iteration returns explicit and automatic members in their definition order."""
        # Act
        members = list(ButtonLabel)

        # Assert
        assert members == [
            ButtonLabel.RUN,
            ButtonLabel.RUN_ALL,
            ButtonLabel.PAUSE,
            ButtonLabel.STOP,
            ButtonLabel.RESTART,
            ButtonLabel.EXIT,
        ]


###############################################################################
class TestIntStrEnumInvalidDefinitions:
    """Tests for enum definitions whose tuple arity violates the required member shape."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_boundary_value_analysis
    def test_single_tuple_value_raises_type_error(self) -> None:
        """A member definition with one tuple element is rejected with TypeError."""
        # Act / Assert
        with pytest.raises(TypeError):

            class BadEnum(IntStrEnum):  # pyright: ignore[reportUnusedClass]
                A = (1,)  # pyright: ignore[reportCallIssue]

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_invalid_input
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_boundary_value_analysis
    def test_three_tuple_values_raise_type_error(self) -> None:
        """A member definition with three tuple elements is rejected with TypeError."""
        # Act / Assert
        with pytest.raises(TypeError):

            class BadEnum(IntStrEnum):  # pyright: ignore[reportUnusedClass]
                A = (1, "one", "extra")  # pyright: ignore[reportCallIssue]


###############################################################################
if __name__ == "__main__":
    sys.exit(pytest.main())
