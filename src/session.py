"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

class Session(QtCore.QAbstractTableModel):
    
	# -------------------------------------------------------------------------
	def __init__(self, data=None):
		super(Session, self).__init__()
        
		# ----------------
		# MEMBER VARIABLES
		# ----------------
		self._data = [] if data is None else data
		self._headers = ["Status", "Output", "Progress"]
		self._name = ""

    # -------------------------------------------------------------------------
	def data(self, index, role):
		if role == Qt.ItemDataRole.DisplayRole:
			value = self._data[index.row()][index.column()]
			return str(value)
	
    # -------------------------------------------------------------------------
	def headerData(self, section: int, orientation, role):
		if role == Qt.ItemDataRole.DisplayRole:
			if orientation == Qt.Orientation.Horizontal:
				return self._headers[section]
		
    # -------------------------------------------------------------------------
	def rowCount(self, index=None):
		return len(self._data)

    # -------------------------------------------------------------------------
	def columnCount(self, index=None):
		if self._data:
			return len(self._data[0])
		return len(self._headers)
	
    # -------------------------------------------------------------------------
	def insertRow(self, data)->int:
		row = self.rowCount()
		self.rowsAboutToBeInserted.emit(QtCore.QModelIndex(), row, row)
		self._data.append(data)
		self.rowsInserted.emit(QtCore.QModelIndex(), row, row)
		return row

    # -------------------------------------------------------------------------
	def removeRow(self, row: int):
		if self.rowCount() > row and row >= 0:
			self.rowsAboutToBeRemoved.emit(QtCore.QModelIndex(), row, row)
			self._data.pop(row)
			self.rowsRemoved.emit(QtCore.QModelIndex(), row, row)
    
    # -------------------------------------------------------------------------
	#def save():
    
    # -------------------------------------------------------------------------
	#def load():
