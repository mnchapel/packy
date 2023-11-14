"""
author: Marie-Neige Chapel
"""

# Python
import json

###############################################################################
class SessionEncoder(json.JSONEncoder):

	# -------------------------------------------------------------------------
	def default(self, obj):
		# if isinstance(obj, (Session, Task, FilesModel, PackerData)):
		if hasattr(obj, "serialize"):
			return obj.serialize()
		else:
			return super.default(obj)
