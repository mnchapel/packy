"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
import sys
from enum import Enum

# -----------------------------------------------------------------------------
class ExternalData(Enum):
	METADATA = "yaml/metadata.yml"
	LOGO = "img/logo.ico"
	PACKER_INFO = "json/packer_info.json"
	JSON_SCHEMA = "json/session_schema.json"
	UI_ABOUT = "ui/about.ui"
	UI_FIX_WARNINGS = "ui/fix_warnings.ui"
	UI_OPTIONS = "ui/options.ui"

# -----------------------------------------------------------------------------
def external_data_path(ExternalData):
	resources_path = ""
	
	if getattr(sys, "frozen", False):
		resources_path = os.path.join(os.path.dirname(sys.executable), "resources")
		print(f"frozen {resources_path}")
	else:
		current_dir = os.path.dirname(__file__)
		resources_path = os.path.join(current_dir, "../../resources")
		print(f"dev {resources_path}")
	
	return os.path.join(resources_path, ExternalData.value)