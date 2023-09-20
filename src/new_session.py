"""
author: Marie-Neige Chapel
"""

from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

class NewSession(QDialog):
    
    # -------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("../resources/new_session.ui", self)
