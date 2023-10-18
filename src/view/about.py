"""
author: Marie-Neige Chapel
"""

from PyQt6.QtWidgets import QDialog
from PyQt6.uic import loadUi

class About(QDialog):
    
    # -------------------------------------------------------------------------
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("../resources/about.ui", self)
