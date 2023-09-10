"""
author: Marie-Neige Chapel
"""

# Python
import json

# PackY
from task import Task

class TaskEncoder(json.JSONEncoder):

	# -------------------------------------------------------------------------
	def default(self, obj):
		if isinstance(obj, Task):
			return json.JSONEncoder().encode({"output_name": obj.output()})
		else:
			return json.JSONEncoder.default(self, obj)
