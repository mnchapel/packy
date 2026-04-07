"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PyQt
from PySide6.QtWidgets import QDialog
from PySide6.QtUiTools import QUiLoader

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
        loader = QUiLoader()
        loader.load(ui_path, self)
