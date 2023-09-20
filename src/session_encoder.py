"""
author: Marie-Neige Chapel
"""

# Python
import json

# Packy
from session import Session
from task import Task
from files_model import FilesModel

class SessionEncoder(json.JSONEncoder):

	# -------------------------------------------------------------------------
	def default(self, obj):
		if isinstance(obj, Session):
			return {"tasks": obj.tasks()}
		elif isinstance(obj, Task):
			return {"name": obj._output_name, "check": obj.filesSelected()}
		elif isinstance(obj, FilesModel):
			return obj.checksToStr()
		else:
			return super.default(obj)
