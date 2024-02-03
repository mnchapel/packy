"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
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
