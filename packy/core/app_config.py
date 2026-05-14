"""Application-wide configuration definitions.

This module provides runtime configuration values used throughout the
application.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Third-party
from PySide6.QtCore import QStandardPaths

# Standard library
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import final


###############################################################################
@final
@dataclass(frozen=True, slots=True)
class AppConfig:
    """Immutable application configuration container.

    Stores derived runtime configuration values.

    Attributes:
        VERSION (str): Application current version.
        LOG_FILE_PATH (Path): Absolute path to the application log file.
    """

    VERSION: str = "0.9.0.0"
    LOG_FILE_PATH: Path = field(init=False)

    def __post_init__(self) -> None:
        """Initializes derived configuration paths after dataclass creation."""
        in_dev_mode = not getattr(sys, "frozen", False)
        if in_dev_mode:
            folder_path = Path("./logs")
        else:
            app_data_location = QStandardPaths.StandardLocation.AppDataLocation
            folder_path = Path(QStandardPaths.writableLocation(app_data_location))
        object.__setattr__(
            self,
            "LOG_FILE_PATH",
            folder_path / "log.txt",
        )
