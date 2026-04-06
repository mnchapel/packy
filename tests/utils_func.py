"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
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
