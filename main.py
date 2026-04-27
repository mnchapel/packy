"""Provide the application entry point for Packy.

This module defines the main function responsible for launching the
application and handling top-level exceptions.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.packy_app import PackyApp

# Standard library
import sys


# -----------------------------------------------------------------------------
def main() -> None:
    """Run the Packy application entry point.

    This function instantiates the Packy application and executes its
    lifecycle. Any unhandled exception is caught and printed to standard
    output.

    Raises:
        Exception: Propagates any exception raised during application
            execution after being caught and logged.
    """
    exit_code = 0
    try:
        exit_code = PackyApp.launch(PackyApp())
    except Exception as e:  # noqa: BLE001
        print(f"Exception: {e}")  # noqa: T201
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
