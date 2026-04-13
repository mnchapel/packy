"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# Python
import json
from typing import override


###############################################################################
class SessionEncoder(json.JSONEncoder):
    ###########################################################################
    # PUBLIC MEMBER FUNCTIONS
    ###########################################################################

    # -------------------------------------------------------------------------
    @override
    def default(self, obj):
        if hasattr(obj, "serialize"):
            return obj.serialize()
        else:
            return super.default(obj)
