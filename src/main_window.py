"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6 import QtWidgets
from ui_main_window import Ui_MainWindow

# PackY
from about import About
from session import Session

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    
	# -------------------------------------------------------------------------
	def __init__(self, *args, obj=None, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
		self.setupUi(self)

		self.connectFileMenuActions()
		self.connectHelpMenuActions()
		self.connectTaskManagement()
		self.connectTaskRunning()

		session = Session()
		self.table_view_session.setModel(session)

		self.table_view_session.horizontalHeader().setVisible(True)

		self.show()

	# -------------------------------------------------------------------------
	def connectFileMenuActions(self):
		self.action_save.triggered.connect(self.save)
		self.action_options.triggered.connect(self.openOptions)
		self.action_exit.triggered.connect(self.close)
	
	# -------------------------------------------------------------------------
	def save(self, s):
		print("save (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def openOptions(self, s):
		print("openOptions (not implemented yet)")

	# -------------------------------------------------------------------------
	def connectHelpMenuActions(self):
		self.action_documentation.triggered.connect(self.openDocumentation)
		self.action_about.triggered.connect(self.openAbout)

	# -------------------------------------------------------------------------
	def openDocumentation(self, s):
		print("openDocumentation (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def openAbout(self, s):
		dlg = About(self)
		dlg.exec()
	
	# -------------------------------------------------------------------------
	def connectTaskManagement(self):
		self.push_button_create.clicked.connect(self.clickOnCreate)
		self.push_button_remove.clicked.connect(self.clickOnRemove)
		self.push_button_edit.clicked.connect(self.clickOnEdit)
	
	# -------------------------------------------------------------------------
	def clickOnCreate(self):
		model = self.table_view_session.model()
		model.insertRow(["a", "b", "c"])
		model.submit()
	
	# -------------------------------------------------------------------------
	def clickOnRemove(self):
		print("clickOnRemove (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def clickOnEdit(self):
		print("clickOnEdit (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def connectTaskRunning(self):
		self.push_button_run_all.clicked.connect(self.clickOnRunAll)
		self.push_button_cancel.clicked.connect(self.clickOnCancel)
	
	# -------------------------------------------------------------------------
	def clickOnRunAll(self):
		print("clickOnRunAll (not implemented yet)")
	
	# -------------------------------------------------------------------------
	def clickOnCancel(self):
		print("clickOnCancel (not implemented yet)")