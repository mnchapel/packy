"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import json

# PackY
from model.session import Session
from model.task import Task

###############################################################################
class SessionDecoder(json.JSONDecoder):

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.__decodeSession, *args, **kwargs)
	
	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################
	
	# -------------------------------------------------------------------------
	def __decodeSession(self, dict):
		if dict.get("session_name"):
			return self.__deserializeSession(dict)
		
		return dict
	
	# -------------------------------------------------------------------------
	def __deserializeSession(self, dict):
		session = Session(dict)
		dict_tasks = dict["tasks"]
		tasks = []
		for dict_task in dict_tasks:
			task = self.__deserializeTask(dict_task)
			tasks.append(task)
		
		session.setTasks(tasks)

		return session
	
	# -------------------------------------------------------------------------
	def __deserializeTask(self, dict):
		task = Task(0, dict)
		return task
