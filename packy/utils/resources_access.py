"""
author: Marie-Neige Chapel
"""

import os
import sys

# -----------------------------------------------------------------------------
def resources_path():
	if hasattr(sys, "_MEIPASS"):
		return os.path.join(sys._MEIPASS, "resources")
	
	current_dir = os.path.dirname(__file__)
	return os.path.join(current_dir, "../../resources")