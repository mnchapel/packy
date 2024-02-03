"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

import os
import sys

# -----------------------------------------------------------------------------
def resources_path():
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, "resources")
	
	current_dir = os.path.dirname(__file__)
	return os.path.join(current_dir, "../../resources")