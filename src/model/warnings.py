"""
author: Marie-Neige Chapel
"""

###############################################################################
class Warnings():

	###########################################################################
	# MEMBER VARIABLES
	#
	# - __added_item_candidates: 
	# - __added_items: 
	# - __removed_items: 
	###########################################################################

	# -------------------------------------------------------------------------
	def __init__(self) -> None:
		self.__added_item_candidates = []
		self.__added_items = []
		self.__removed_items = []

	###########################################################################
	# GETTERS
	###########################################################################

	# -------------------------------------------------------------------------
	def addedItems(self):
		return self.__added_items
	
	# -------------------------------------------------------------------------
	def removedItems(self):
		return self.__removed_items

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def addCandidateAddedItem(self, item_path: str) -> None:
		if item_path not in self.__added_item_candidates:
			self.__added_item_candidates.append(item_path)
	
	# -------------------------------------------------------------------------
	def addAddedItem(self, item_path: str) -> None:
		if item_path not in self.__added_items:
			self.__added_items.append(item_path)

			if self.isInAddedCandidateItems(item_path):
				self.__added_item_candidates.remove(item_path)
	
	# -------------------------------------------------------------------------
	def addRemovedItem(self, item_path: str) -> None:
		if item_path not in self.__removed_items:
			self.__removed_items.append(item_path)

	# -------------------------------------------------------------------------
	def isInAddedCandidateItems(self, item_path: str) -> bool:
		if item_path in self.__added_item_candidates:
			return True
		
		return False
	
	# -------------------------------------------------------------------------
	def clear(self):
		self.__added_item_candidates.clear()
		self.__added_items.clear()
		self.__removed_items.clear()