"""Provide the main application lifecycle management for Packy.

This module defines the Packy application class responsible for handling
the full lifecycle of the application, including configuration,
initialization, execution, and cleanup.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.debug_logger import DebugLogger
from packy.views.main_window import MainWindow

# Third-party
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication, QStandardPaths

# Standard library
import sys
from pathlib import Path
from typing import final


###############################################################################
class PackyLifeCycleError(Exception):
    """An error occurring during the Packy application lifecycle.

    This exception represents failures encountered during one of the
    lifecycle phases such as configuration, initialization, execution,
    or disposal.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with an error message.

        Args:
            message (str): A descriptive message explaining the failure.
        """
        super().__init__(message)


###############################################################################
@final
class PackyApp:
    """Encapsulate the lifecycle of the Packy application.

    This class orchestrates the different stages of the application
    lifecycle: configuration, initialization, execution, and disposal.
    """

    # -------------------------------------------------------------------------
    @staticmethod
    def launch(app: PackyApp) -> int:
        """Execute the full lifecycle of the application.

        Args:
            app (Packy): The application instance to launch.

        Returns:
            int: The exit code of the application.
        """
        exit_code = 1
        try:
            app.configure()
            app.init()
            exit_code = app.run()
        finally:
            app.dispose()

        return exit_code

    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """Initialize the Packy application instance."""
        QCoreApplication.setOrganizationName("PackY")
        QCoreApplication.setOrganizationDomain("packy.com")
        QCoreApplication.setApplicationName("PackY")

    # -------------------------------------------------------------------------
    def configure(self) -> None:
        """Configure the application environment and settings."""

    # -------------------------------------------------------------------------
    def init(self) -> None:
        """Initialize application components and logging system."""
        in_dev_mode = not getattr(sys, "frozen", False)
        if in_dev_mode:
            folder_path = Path("./logs")
        else:
            app_data_location = QStandardPaths.StandardLocation.AppDataLocation
            folder_path = Path(QStandardPaths.writableLocation(app_data_location))
        log_file_path = folder_path / "log.txt"
        has_started = DebugLogger.start(log_file_path)
        if not has_started:
            raise PackyLifeCycleError("Debug logger has already been started.")  # noqa: TRY003
        QtCore.qDebug("App initialized.")

    # -------------------------------------------------------------------------
    def run(self) -> int:
        """Start the Qt application event loop and main window.

        This method creates the QApplication instance, sets the
        application icon, initializes the main window, and starts
        the event loop.

        Returns:
            int: The exit code of the application.
        """
        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()
        return app.exec()

    # -------------------------------------------------------------------------
    def dispose(self) -> None:
        """Release application resources before shutdown."""
        QtCore.qDebug("App disposed.")
        has_stopped = DebugLogger.stop()
        if not has_stopped:
            raise PackyLifeCycleError("Debug logger is not started.")  # noqa: TRY003
