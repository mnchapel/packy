"""
author: Marie-Neige Chapel
"""

# Python
import json

# Packy
from session import Session
from task import Task
from files_model import FilesModel
from packer_data import PackerData

###############################################################################
class SessionDecoder(json.JSONDecoder):

	# -------------------------------------------------------------------------
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.decodeSession, *args, **kwargs)
	
	# -------------------------------------------------------------------------
	def decodeSession(self, dict):
		if dict.get("session_name"):
			return self.deserializeSession(dict)
		elif dict.get("task_name"):
			return self.deserializeTask(dict)
		elif dict.get("root_path"):
			return self.deserializeFilesModel(dict)
		elif dict.get("compression_method"):
			return self.deserializePackerData(dict)
		return dict
	
	# -------------------------------------------------------------------------
	def deserializeSession(self, dict):
		session = Session()
		session.setTasks(dict["tasks"])
		return session
	
	# -------------------------------------------------------------------------
	def deserializeTask(self, dict):
		task = Task(dict["packer_data"])
		task.setFilesSelected(dict["files_model"])
		task.setDestinationFile(dict["destination_file"])
		return task
	
	# -------------------------------------------------------------------------
	def deserializeFilesModel(self, dict):
		files_model = FilesModel(dict["root_path"])
		files_model.setChecks(dict["check"])
		return files_model
	
	# -------------------------------------------------------------------------
	def deserializePackerData(self, dict):
		packer_data = PackerData(dict)
		return packer_data
