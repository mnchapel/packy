"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
import re

# -----------------------------------------------------------------------------
def camelCaseToSnakeCase(value: str) -> str:
	return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()

# -----------------------------------------------------------------------------
def joinPath(path, *paths):
	return os.path.join(path, *paths).replace("\\", "/")