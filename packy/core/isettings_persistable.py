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
    from packy.models.packy_settings import PackySettings


###############################################################################
class ISettingsPersistable(Protocol):
    """_summary_

    Args:
        Protocol (_type_): _description_
    """

    @abstractmethod
    def read_settings(self, settings: PackySettings) -> None:
        """_summary_

        Args:
            settings (PackySettings): _description_
        """
        raise NotImplementedError

    @abstractmethod
    def write_settings(self, settings: PackySettings) -> None:
        """_summary_

        Args:
            settings (PackySettings): _description_
        """
        raise NotImplementedError
