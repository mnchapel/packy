"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# Python
import pytest

# PyQt
from PyQt6.QtCore import QCoreApplication


# -----------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def initQCoreApplication():
    QCoreApplication.setOrganizationName("PackYCorp")
    QCoreApplication.setOrganizationDomain("packy.com")
    QCoreApplication.setApplicationName("PackY")
