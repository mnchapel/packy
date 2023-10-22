"""
author: Marie-Neige Chapel
"""

# Python
import os

# PackY
from model.task import Task

###############################################################################
class Packer():

	###########################################################################
	# MEMBER FUNCTIONS
	###########################################################################

    # -------------------------------------------------------------------------
	def run(self, task: Task):
		checked_items = task.filesSelected().checks()
		items_to_pack = self.filterSelectedFiles(checked_items)

		self.packItems(task, items_to_pack)
			
		task.updateStatus(True)

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
