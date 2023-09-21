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
			return self.serializeSession(obj)
		elif isinstance(obj, Task):
			return self.serializeTask(obj)
		elif isinstance(obj, FilesModel):
			return self.serializeFilesModel(obj)
		else:
			return super.default(obj)
	
	# -------------------------------------------------------------------------
	def serializeSession(self, session: Session):
		dict = {}

		dict["session_name"] = session.name()
		dict["tasks"] = session.tasks()

		return dict

	# -------------------------------------------------------------------------
	def serializeTask(self, task: Task):
		dict = {}

		dict["task_name"] = task.name()
		dict["files_model"] = task.filesSelected()

		return dict
	
	# -------------------------------------------------------------------------
	def serializeFilesModel(self, files_model: FilesModel):
		dict = {}

		dict["root_path"] = files_model.rootPath()
		dict["check"] = files_model.checksToStr()

		return dict
