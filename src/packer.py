"""
author: Marie-Neige Chapel
"""

import zipfile

class Packer():

	# -------------------------------------------------------------------------
	def __init__(self):

		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._type = ""
		self._compression_type = ""
		self._compression_level = ""

    # -------------------------------------------------------------------------
	def type(self):
		return self._type
	
    # -------------------------------------------------------------------------
	def compressionType(self):
		return self._compression_type
	
    # -------------------------------------------------------------------------
	def compressionLevel(self):
		return self._compression_level

    # -------------------------------------------------------------------------
	def updateType(self, type: str):
		self._type = type
