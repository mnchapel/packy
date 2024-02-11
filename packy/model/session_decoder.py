"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import json
from jsonschema import SchemaError, ValidationError, validate

# PyQt
from PyQt6 import QtCore

# PackY
from model.session import Session
from model.task import Task
from utils.external_data_access import ExternalData, external_data_path

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
		try:
			if dict.get("session_name"):
				self.__validateJson(dict)
				return self.__deserializeSession(dict)
			
			return dict
		except (ValidationError, SchemaError) as ex:
			debug_msg = type(ex).__name__ + ": " + str(ex)
			QtCore.qDebug(debug_msg)

			critical_msg = "Cannot open the file. Wrong format detected."
			QtCore.qCritical(critical_msg)
	
	# -------------------------------------------------------------------------
	def __validateJson(self, session_dict):
		session_schema_path = external_data_path(ExternalData.JSON_SCHEMA)
		session_schema = json.load(open(session_schema_path))
		validate(session_dict, session_schema)
	
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
