"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# PyQt
from PyQt6.QtCore import QCoreApplication, QSettings

# -----------------------------------------------------------------------------
def packySettings():
	return QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, QCoreApplication.organizationName(), QCoreApplication.applicationName())
