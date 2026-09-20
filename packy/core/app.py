"""Provide the PackY Qt application and its execution lifecycle.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.core.app_config import AppConfig
from packy.core.app_lifecycle import AppLifecycle, AppState, Transition
from packy.core.localization import Localization
from packy.core.user_settings import UserSettings
from packy.ui.main_window import MainWindow

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication

# Standard library
from typing import Final, final


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

        self._lifecycle: Final = AppLifecycle()

        self._localization: Localization | None = None
        self._config: AppConfig | None = None
        self._settings: UserSettings | None = None
        self._main_window: MainWindow | None = None

        self.aboutToQuit.connect(self.post_run)

    # -------------------------------------------------------------------------
    @property
    def state(self) -> AppState:
        """The current application lifecycle state."""
        return self._lifecycle.state

    # -------------------------------------------------------------------------
    def initialize(self, config: AppConfig) -> None:
        """Initialize application components.

        Args:
            config (AppConfig): Configuration.
        """
        with self._lifecycle.transition(Transition.INITIALIZE):
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

            QtCore.qDebug("App initialized.")

    # -------------------------------------------------------------------------
    def run(self) -> int:
        """Create the main window and start the Qt event loop.

        The method loads the saved main-window settings, restores the last batch,
        and shows the window before entering the event loop.

        The application must first be initialized by calling :meth:`initialize`.

        Returns:
            int: Exit code returned by the Qt event loop.

        Raises:
            RuntimeError: The application is not initialized.
        """
        with self._lifecycle.transition(Transition.RUN):
            assert self._config is not None
            assert self._settings is not None

            self._main_window = MainWindow(self._config, self._settings)
            self._main_window.load_settings()
            self._main_window.show()
            self._main_window.restore_last_batch()
            QtCore.qDebug("Previous app state restored.")

        return self.exec()

    # -------------------------------------------------------------------------
    @Slot(result=None)
    def post_run(self) -> None:
        """Save application state before the Qt event loop quits.

        This slot does not need to be called explicitly. It is connected to the
        :attr:`~PySide6.QtCore.QCoreApplication.aboutToQuit` signal of the
        application in the constructor and is invoked automatically when the
        application is about to quit, for example after a call to
        :meth:`~PySide6.QtCore.QCoreApplication.quit` or when the user logs out
        or shuts down the desktop session.

        The application must first be initialized by calling :meth:`initialize`.
        """
        with self._lifecycle.transition(Transition.FINISH):
            assert self._main_window is not None
            assert self._main_window.isVisible() is False
            self._save_app_state()
            QtCore.qDebug(f"{self.objectName()} state saved.")

    # -------------------------------------------------------------------------
    def dispose(self) -> None:
        """Dispose of the application.

        Dispose an application already disposed has no effect.
        """
        if self._lifecycle.state is AppState.DISPOSED:
            return

        with self._lifecycle.transition(Transition.DISPOSE):
            self._localization = None
            self._config = None
            self._settings = None
            self._main_window = None
            QtCore.qDebug("App disposed.")

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
    def _save_app_state(self) -> None:
        """Save the current state of the app and the UI.

        If the main window exists, delegate settings persistence to its
        :meth:`~MainWindow.save_settings` method.
        """
        QtCore.qDebug(f"Saving {self.objectName()} state.")
        if self._main_window is not None:
            self._main_window.save_settings()
