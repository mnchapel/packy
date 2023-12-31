"""
author: Marie-Neige Chapel
"""

# Python
import json

# Packy
from model.session import Session
from model.task import Task

###############################################################################
class SessionDecoder(json.JSONDecoder):

	# -------------------------------------------------------------------------
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.decodeSession, *args, **kwargs)
	
	# -------------------------------------------------------------------------
	def decodeSession(self, dict):
		if dict.get("session_name"):
			return self.deserializeSession(dict)
		
		return dict
	
	# -------------------------------------------------------------------------
	def deserializeSession(self, dict):
		session = Session(dict)
		dict_tasks = dict["tasks"]
		tasks = []
		for dict_task in dict_tasks:
			task = self.deserializeTask(dict_task)
			tasks.append(task)
		
		session.setTasks(tasks)

		return session
	
	# -------------------------------------------------------------------------
	def deserializeTask(self, dict):
		task = Task(0, dict)
		return task
