"""
author: Marie-Neige Chapel
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
