"""Provide the main application lifecycle management for Packy.

This module defines the Packy application class responsible for handling
the full lifecycle of the application, including configuration,
initialization, execution, and cleanup.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.models.log import messageHandler
from packy.views.main_window import MainWindow

# Third-party
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QCoreApplication

# Standard library
import sys
from typing import final


###############################################################################
@final
class Packy:
    """Encapsulate the lifecycle of the Packy application.

    This class orchestrates the different stages of the application
    lifecycle: configuration, initialization, execution, and disposal.
    """

    # -------------------------------------------------------------------------
    @staticmethod
    def launch(app: Packy) -> int:
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
        QtCore.qInstallMessageHandler(messageHandler)
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
