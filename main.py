"""Provide the application entry point for Packy.

This module defines the main function responsible for launching the
application and handling top-level exceptions.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.packy import Packy


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
    try:
        Packy.launch(Packy())
    except Exception as e:  # noqa: BLE001
        print(f"Exception: {e}")  # noqa: T201


if __name__ == "__main__":
    main()
