"""Provide a dialog displaying application information.

This module defines a Qt dialog responsible for loading and displaying
the "About" user interface from an external UI file using QUiLoader.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Local application
from packy.ui.ui_about_dialog import Ui_AboutDialog

# Third-party
from PySide6.QtWidgets import QDialog


###############################################################################
class AboutDialog(QDialog):
    """A dialog that displays application information.

    This dialog dynamically loads its interface from an external `.ui` file.
    """

    # -------------------------------------------------------------------------
    def __init__(self, parent: QDialog | None = None) -> None:
        """Initialize the About dialog and load its UI definition.

        Args:
            parent (QDialog | None, optional):
                The parent widget of the dialog. Defaults to None.
        """
        super().__init__(parent)
        self.__ui: Ui_AboutDialog = Ui_AboutDialog()
        self.__ui.setupUi(self)
