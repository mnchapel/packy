"""
author: Marie-Neige Chapel
"""

# Python
import json

# Packy
from session import Session
from task import Task
from files_model import FilesModel

###############################################################################
class SessionDecoder(json.JSONDecoder):

	# -------------------------------------------------------------------------
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.decodeSession, *args, **kwargs)
	
	# -------------------------------------------------------------------------
	def decodeSession(self, dict):
		if dict.get("session_name"):
			session = Session()
			session.setTasks(dict["tasks"])
			return session
		elif dict.get("task_name"):
			task = Task()
			task.setFilesSelected(dict["files_model"])
			return task
		elif dict.get("root_path"):
			files_model = FilesModel(dict["root_path"])
			files_model.setChecks(dict["check"])
			return files_model
		return dict
