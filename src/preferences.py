"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QSettings

###############################################################################
class Preferences:

	# -------------------------------------------------------------------------
	def __init__(self):
		filename = "options.ini"
		format = QSettings.Format.IniFormat
		self._settings = QSettings(filename, format)
