"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PyQt
from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

# PackY
from utils.external_data_access import ExternalData, external_data_path


###############################################################################
class About(QDialog):
    ###########################################################################
    # SPECIAL METHODS
    ###########################################################################

    # -------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = external_data_path(ExternalData.UI_ABOUT)
        loadUi(ui_path, self)
