"""Provide the PackY Qt application and its execution lifecycle.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.app_config import AppConfig
from packy.core.localization import Localization
from packy.core.user_settings import UserSettings
from packy.ui.main_window import MainWindow

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

# Standard library
from typing import final


###############################################################################
@final
class App(QApplication):
    """Coordinate application the lifecycle.

    This class orchestrates the different stages of the application lifecycle:
    configuration, initialization, execution, and disposal.
    """

    # -------------------------------------------------------------------------
    @staticmethod
    def launch(app: App) -> int:
        """Configure, initialize, run, and dispose of an application instance.

        The application is disposed even if configuration, initialization, or
        execution raises an exception.

        Args:
            app (App): Application instance to launch.

        Returns:
            int: Exit code returned by :meth:`run`.
        """
        exit_code = 1
        try:
            config: AppConfig = AppConfig()
            app.initialize(config)
            exit_code = app.run()
        finally:
            app.dispose()

        return exit_code

    # -------------------------------------------------------------------------
    def __init__(self, args: list[str]) -> None:
        """Initialize the PackY application.

        The application creates its localization and persistent-settings services and
        registers the application metadata used by Qt.

        Args:
            args (list[str]): Command-line arguments passed to Qt.
        """
        super().__init__(args)
        self.setObjectName(self.__class__.__name__)

        self._localization: Localization | None = None
        self._config: AppConfig | None = None
        self._settings: UserSettings | None = None
        self._main_window: MainWindow | None = None
        self._initialized = False

        self.aboutToQuit.connect(self._on_about_to_quit)

    # -------------------------------------------------------------------------
    def initialize(self, config: AppConfig) -> None:
        """Initialize application components.

        Args:
            config (AppConfig): Configuration.
        """
        if self._initialized:
            raise RuntimeError("Application already initialized")

        # Initialize metadata
        self.setOrganizationName("PackY")
        self.setOrganizationDomain("packy.com")
        self.setApplicationName("PackY")
        self.setApplicationDisplayName("PackY")
        self.setApplicationVersion(config.VERSION)

        # Initialize localization
        self._localization = Localization()
        self._localization.install_translators(config.DEFAULT_LANGUAGE_CODE)

        # Initialize configurations
        self._config = config
        self._settings = UserSettings(self)
        QtCore.qDebug(f"Settings are stored in '{self._settings.file_path}'.")

        self._initialized = True
        QtCore.qDebug("App initialized.")

    # -------------------------------------------------------------------------
    def run(self) -> int:
        """Create the main window and start the Qt event loop.

        The method loads the saved main-window settings, restores the last batch,
        and shows the window before entering the event loop.

        Returns:
            int: Exit code returned by the Qt event loop.
        """
        if not self._initialized:
            raise RuntimeError("Application is not initialized")

        assert self._config is not None
        assert self._settings is not None

        self._main_window = MainWindow(self._config, self._settings)
        self._main_window.load_settings()
        self._main_window.restore_last_batch()
        QtCore.qDebug("Previous app state restored.")
        self._main_window.show()

        return self.exec()

    # -------------------------------------------------------------------------
    def dispose(self) -> None:
        """Dispose of the application."""
        if self._main_window is not None:
            self._main_window.close()
            self._main_window = None

        self._localization = None
        self._config = None
        self._settings = None
        self._initialized = False
        QtCore.qDebug("App disposed.")

    # -------------------------------------------------------------------------
    @property
    def is_initialized(self) -> bool:
        """Whether the application is initialized by :meth:`initialize`."""
        return self._initialized

    # -------------------------------------------------------------------------
    @property
    def localization(self) -> Localization | None:
        """The localization service initialized by :meth:`initialize`."""
        return self._localization

    # -------------------------------------------------------------------------
    @property
    def settings(self) -> UserSettings | None:
        """The persistent user settings initialized by :meth:`initialize`."""
        return self._settings

    # -------------------------------------------------------------------------
    @property
    def main_window(self) -> MainWindow | None:
        """The unique main window initialized by :meth:`run`."""
        return self._main_window

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _on_about_to_quit(self) -> None:
        """Save application settings before the Qt event loop quits.

        This slot delegates persistence of the current application state to
        :meth:`_save_settings`.
        """
        QtCore.qDebug(f"Closing {self.objectName()}.")
        self._save_settings()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def _save_settings(self) -> None:
        """Save the current main-window settings.

        If the main window exists, delegate settings persistence to its
        ``save_settings`` method.
        """
        QtCore.qDebug(f"Saving {self.objectName()} settings.")
        if self._main_window is not None:
            self._main_window.save_settings()
