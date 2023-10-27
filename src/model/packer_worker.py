"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import Qt, QRunnable

# PackY
from model.packer_factory import createPacker
from model.progression import Progression
from model.session import Session
from model.packer_worker_signals import PackerWorkerSignals

###############################################################################
class PackerWorker(QRunnable):

    # -------------------------------------------------------------------------
	def __init__(self, session: Session, progression: Progression):
		super(PackerWorker, self).__init__()

		self.__session = session
		self.__progression = progression
		self.signals = PackerWorkerSignals()

    # -------------------------------------------------------------------------
	def run(self):
		tasks = self.__session.tasks()

		for index, task in enumerate(tasks):
			if task.isChecked() == Qt.CheckState.Checked.value:
				self.signals.runTaskId.emit(index)
				packer = createPacker(task)
				packer.progress.connect(self.__progression.updateTaskProgress)
				packer.finish.connect(self.__progression.updateGlobalProgress)
				packer.run()