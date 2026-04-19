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
from packy.utils.external_data_access import ExternalData, external_data_path
from packy.views.main_window import MainWindow

# Third-party
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon

# Standard library
import sys


###############################################################################
class Packy:
    """Encapsulate the lifecycle of the Packy application.

    This class orchestrates the different stages of the application
    lifecycle: configuration, initialization, execution, and disposal.
    """

    # -------------------------------------------------------------------------
    @staticmethod
    def launch(app: Packy) -> None:
        """Execute the full lifecycle of the application.

        Args:
            app (Packy): The application instance to launch.
        """
        QtCore.qDebug("Starting PackY...")
        app.configure()
        app.init()
        QtCore.qDebug("PackY started successfully!")
        app.run()
        QtCore.qDebug("Stopping PackY...")
        app.dispose()
        QtCore.qDebug("PackY stopped successfully!")

    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """Initialize the Packy application instance."""

    # -------------------------------------------------------------------------
    def configure(self) -> None:
        """Configure the application environment and settings."""
        QtCore.qDebug("*** (1/2) Configurating app ***")
        QtCore.qDebug("App configurated")

    # -------------------------------------------------------------------------
    def init(self) -> None:
        """Initialize application components and logging system."""
        QtCore.qDebug("*** (2/2) Initializing app ***")
        QtCore.qInstallMessageHandler(messageHandler)
        QtCore.qDebug("App initialized.")

    # -------------------------------------------------------------------------
    def run(self) -> None:
        """Start the Qt application event loop and main window.

        This method creates the QApplication instance, sets the
        application icon, initializes the main window, and starts
        the event loop.
        """
        QtCore.qDebug("*** Run app ***")
        app = QtWidgets.QApplication(sys.argv)
        icon_path = external_data_path(ExternalData.LOGO)
        app.setWindowIcon(QIcon(icon_path))
        main_window = MainWindow()

        sys.exit(app.exec())

    # -------------------------------------------------------------------------
    def dispose(self) -> None:
        """Release application resources before shutdown."""
        QtCore.qDebug("*** Dispose app ***")
        QtCore.qDebug("*** App disposed. ***")
