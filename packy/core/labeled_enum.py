"""Enum utilities providing labeled enumeration values.

This module defines a base enumeration class associating integer values
with human-readable labels. It is intended for use in UI-oriented enums
where both a stable identifier and a display label are required.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Standard library
from enum import Enum
from typing import Any, Self, override


###############################################################################
class LabeledEnum(Enum):
    """Base enumeration class associating identifiers with display labels.

    Each enumeration member stores both an integer identifier and a
    human-readable label accessible through dedicated properties.
    """

    # -------------------------------------------------------------------------
    @override
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        """Generates sequential integer identifiers for enum members.

        Args:
            name (str): The enumeration member name.
            start (int): The initial value passed to auto().
            count (int): The number of existing enum members.
            last_values (list[Any]): The previously generated values.

        Returns:
            Any: The generated enumeration value.
        """
        return count

    # -------------------------------------------------------------------------
    def __new__(cls, id_: int, label: str) -> Self:
        """Creates a labeled enumeration member.

        Args:
            id_ (int): The integer identifier associated with the member.
            label (str): The human-readable label of the member.

        Returns:
            Self: The initialized enumeration member instance.
        """
        obj = object.__new__(cls)
        obj._value_ = id_
        obj._label = label  # pyright: ignore[reportAttributeAccessIssue] This syntax is allowed: <https://docs.python.org/3/howto/enum.html#when-to-use-new-vs-init>  # noqa: SLF001
        return obj

    # -------------------------------------------------------------------------
    @property
    def id(self) -> int:
        """The integer identifier of the enumeration member.

        Returns:
            int: The enumeration identifier.
        """
        return self._value_

    # -------------------------------------------------------------------------
    @property
    def label(self) -> str:
        """The display label of the enumeration member.

        Returns:
            str: The human-readable label.
        """
        return self._label  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
