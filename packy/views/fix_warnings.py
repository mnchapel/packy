"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PyQt
from json import load

from PySide6.QtWidgets import QDialog, QAbstractButton
from PySide6.QtUiTools import QUiLoader

# PackY
from packy.models.files_model import FilesModel
from packy.models.warnings import Warnings
from packy.utils.external_data_access import ExternalData, external_data_path


###############################################################################
class FixWarnings(QDialog):
    ###########################################################################
    # PRIVATE MEMBER VARIABLES
    #
    # __ui :
    # __model: the model
    ###########################################################################

    ###########################################################################
    # SPECIAL METHODS
    ###########################################################################

    # -------------------------------------------------------------------------
    def __init__(self, files_model: FilesModel, parent=None) -> None:
        super(FixWarnings, self).__init__()

        ui_path = external_data_path(ExternalData.UI_FIX_WARNINGS)
        loader = QUiLoader()
        self.__ui = loader.load(ui_path, self)
        self.__model = files_model
        self.__init()

    ###########################################################################
    # PRIVATE MEMBER FUNCTIONS
    ###########################################################################

    # -------------------------------------------------------------------------
    def __init(self) -> None:
        warnings = self.__model.warnings()
        self.__initAddedItems(warnings)
        self.__initRemovedItems(warnings)

        self.__initConnect()

    # -------------------------------------------------------------------------
    def __initAddedItems(self, warnings: Warnings) -> None:
        added_items = warnings.addedItems()
        self.added_items.addItems(added_items)

    # -------------------------------------------------------------------------
    def __initRemovedItems(self, warnings: Warnings) -> None:
        removed_items = warnings.removedItems()
        self.removed_items.addItems(removed_items)

    # -------------------------------------------------------------------------
    def __initConnect(self) -> None:
        self.__ui.button_box.clicked.connect(self.__buttonClicked)

    ###########################################################################
    # PRIVATE SLOT
    ###########################################################################

    # -------------------------------------------------------------------------
    def __buttonClicked(self, button: QAbstractButton) -> None:
        if button.text() == "Apply":
            self.__model.updateModel()
            super().accept()
