"""_summary_

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
    """_summary_

    Args:
        Protocol (_type_): _description_
    """

    @abstractmethod
    def read_settings(self, settings: Settings) -> None:
        """_summary_

        Args:
            settings (PackySettings): _description_
        """
        raise NotImplementedError

    @abstractmethod
    def write_settings(self, settings: Settings) -> None:
        """_summary_

        Args:
            settings (PackySettings): _description_
        """
        raise NotImplementedError
