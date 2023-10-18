"""
author: Marie-Neige Chapel
"""

# Python
import os
from zipfile import ZipFile

# PackY
from model.session import Session

###############################################################################
class Packer():

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def runAll(self, session: Session):
		tasks = session.tasks()

		for index, task in enumerate(tasks):
			checked_items = task.filesSelected().checks()
			items_to_pack = self.filterSelectedFiles(checked_items)

			destination_filename = task.destinationFile()
			
			with ZipFile(destination_filename, mode = "w") as m_zip:
				self.packItems(m_zip, items_to_pack)
			
			task.updateStatus(True)
			session.emitTaskDataChanged(index)

    # -------------------------------------------------------------------------
	def filterSelectedFiles(self, checked_items: dict):
		items_to_pack = []
		
		items_to_pack = {k: v for k, v in checked_items.items() if v == 2}
		dir_items = {item for item in items_to_pack if os.path.isdir(item)}
		files_items = {item for item in items_to_pack if os.path.isfile(item)}
		files_to_pack = {item for item in items_to_pack if os.path.isfile(item)}
		
		items_to_pack.clear()
		items_to_pack = dir_items

		for dir in dir_items:
			for file in files_items:
				if dir in file:
					files_to_pack.remove(file)
		
		items_to_pack = dir_items | files_to_pack

		return items_to_pack

    # -------------------------------------------------------------------------
	def packItems(self, m_zip: ZipFile, items: set):
		for item in items:
			if os.path.isdir(item):
				self.packDir(m_zip, item)
			else:
				self.packFile(m_zip, item)

    # -------------------------------------------------------------------------
	def packDir(self, m_zip, path):
		for root, _, files in os.walk(path):
			for file in files:
				m_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
	
    # -------------------------------------------------------------------------
	def packFile(self, m_zip, path):
				m_zip.write(path, os.path.basename(path))

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
