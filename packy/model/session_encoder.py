"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import json
from typing_extensions import override

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
