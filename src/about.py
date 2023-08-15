"""
author: Marie-Neige Chapel
"""

from PyQt6.QtWidgets import QDialog
from ui_about import Ui_About

class About(QDialog):
    
    # -------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        
		# ----------------
		# MEMBER VARIABLES
		# ----------------
        self._ui = Ui_About()
        self._ui.setupUi(self)
