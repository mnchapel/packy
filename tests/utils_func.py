"""
author: Marie-Neige Chapel
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