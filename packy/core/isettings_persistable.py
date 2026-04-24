"""Define an interface for objects that can persist their state to settings.

This module provides an interface that enforces implementation of
methods for reading from and writing to a settings storage.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Standard library
from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    # Local application
    from packy.core.settings import Settings

###############################################################################
class ISettingsPersistable(Protocol):
    """Define a contract for objects supporting settings persistence.

    Classes implementing this protocol must provide methods to read
    their state from a settings object and write their state back to it.
    """

    @abstractmethod
    def read_settings(self, settings: Settings) -> None:
        """Load the object state from the provided settings.

        Args:
            settings (Settings): The settings source to read from.
        """
        raise NotImplementedError

    @abstractmethod
    def write_settings(self, settings: Settings) -> None:
        """Persist the object state into the provided settings.

        Args:
            settings (Settings): The settings destination to write to.
        """
        raise NotImplementedError
