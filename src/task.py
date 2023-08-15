"""
author: Marie-Neige Chapel
"""

import json

class Task("""Find the Qt Model"""):
	
	# -------------------------------------------------------------------------
	def __init__(self):
		
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._output = "output_name"
    
	# -------------------------------------------------------------------------
	def save(self):
		json.dump(self.output, indent=4)
