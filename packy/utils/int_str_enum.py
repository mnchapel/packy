"""Define an :class:`Enum` base class with integer values and string labels.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Standard library
from enum import Enum
from typing import Any, Self, override


###############################################################################
class IntStrEnum(Enum):
    """Represent enum members with integer values and string labels.

    Define each member with an ``(int_value, str_value)`` tuple. Members created
    with :func:`enum.auto` use the number of previously defined members as their
    integer value and their lowercase name as their string value.

    Example enumeration:

    >>> from packy.utils.int_str_enum import IntStrEnum
    >>> from enum import auto
    >>> class ButtonLabel(IntStrEnum):
    ...     RUN = (0, "Run")
    ...     RUN_ALL = (1, "Run all")
    ...     PAUSE = (2, "Pause")
    ...     STOP = (3, "Stop")
    ...     RESTART = auto()
    >>> ButtonLabel.RUN_ALL.int_value
    1
    >>> ButtonLabel.RUN_ALL.str_value
    'Run all'
    >>> ButtonLabel.RESTART.int_value
    4
    >>> ButtonLabel.RESTART.str_value
    'restart'
    >>> str(ButtonLabel.RUN_ALL)
    'ButtonLabel.RUN_ALL(1, Run all)'
    >>> ButtonLabel.RUN_ALL  # call repr(ButtonLabel.RUN_ALL)
    ButtonLabel.RUN_ALL(name='RUN_ALL', value/int_value=1, str_value='Run all')
    >>> format(ButtonLabel.RUN_ALL)  # indirectly call str()
    "ButtonLabel.RUN_ALL(1, 'Run all')"
    >>> ButtonLabel.RESTART  # call repr(ButtonLabel.RESTART)
    ButtonLabel.RESTART(name='RESTART', value/int_value=4, str_value='restart')
    >>> str(ButtonLabel.RESTART)
    "ButtonLabel.RESTART(4, 'restart')"
    >>> format(ButtonLabel.RESTART)  # indirectly call str()
    "ButtonLabel.RESTART(4, 'restart')"
    """

    # -------------------------------------------------------------------------
    @override
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> Any:
        """Generate the value for an automatically assigned enum member.

        Args:
            name (str): Name of the member being generated.
            start (int): Initial value supplied for automatic numbering. This value is
              ignored.
            count (int): Number of members defined before the new member.
            last_values (list[Any]): Previously assigned member values. These values
              are ignored.

        Returns:
            tuple[int, str]: The member count and lowercase member name.
        """
        return (count, name.lower())

    # -------------------------------------------------------------------------
    def __new__(cls, int_value: int, str_value: str) -> Self:
        """Create an enum member from an integer value and string label.

        Args:
            int_value (int): Integer stored as the enum member's value.
            str_value (str): String label associated with the member.

        Returns:
            Self: The newly created enum member.
        """
        member = object.__new__(cls)
        member._value_ = int(int_value) # Convert is need when a IntEnum is passed
        member._str_value = str_value  # pyright: ignore[reportAttributeAccessIssue] This syntax is allowed: <https://docs.python.org/3/howto/enum.html#when-to-use-new-vs-init>  # noqa: SLF001
        return member

    # -------------------------------------------------------------------------
    @override
    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return (
            f"{cls_name}.{self.name}("
            f"name={self.name!r}, "
            f"value/int_value={int(self.value)!r}, "
            f"str_value={self.str_value!r})"
        )

    # -------------------------------------------------------------------------
    @override
    def __str__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}.{self.name}({int(self.value)}, {self.str_value})"

    # -------------------------------------------------------------------------
    @override
    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    # -------------------------------------------------------------------------
    @property
    def int_value(self) -> int:
        """The member's integer value."""
        return self._value_

    # -------------------------------------------------------------------------
    @property
    def str_value(self) -> str:
        """The member's string label."""
        return self._str_value  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportAttributeAccessIssue]
