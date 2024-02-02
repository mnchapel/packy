"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QCoreApplication, QSettings

# -----------------------------------------------------------------------------
def packySettings():
	return QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, QCoreApplication.organizationName(), QCoreApplication.applicationName())
