"""
author: Marie-Neige Chapel
"""

# Python
import zipfile

# PackY
from session import Session

###############################################################################
class Packer():

	# # -------------------------------------------------------------------------
	# def __init__(self, session: Session):

	# 	# ----------------
	# 	# MEMBER VARIABLES
	# 	# ----------------
	# 	print("[Packer][__init__]")
	# 	self._type = ""
	# 	self._compression_type = ""
	# 	self._compression_level = ""

	# 	with zipfile.ZipFile("output.zip", mode = "w") as m_zip:
	# 		m_zip.write("ui_new_session.py")

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def runAll(self, session: Session):
		tasks = session.tasks()

		for task in tasks:
			destination_filename = task.destinationFile()
			with zipfile.ZipFile(destination_filename, mode = "w") as m_zip:
				m_zip.write("ui_main_window.py")

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
