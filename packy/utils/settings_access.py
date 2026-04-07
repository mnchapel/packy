"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PyQt
from PySide6.QtCore import QCoreApplication, QSettings


# -----------------------------------------------------------------------------
def packySettings():
    return QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        QCoreApplication.organizationName(),
        QCoreApplication.applicationName(),
    )
