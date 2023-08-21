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
		self._packer_type = ""
		self._compression_type = ""
		self._compression_level = ""

    # -------------------------------------------------------------------------
	def updateType(self, type: str):
		self._type = type
