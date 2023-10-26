"""
author: Marie-Neige Chapel
"""

# PyQt
from PyQt6.QtCore import QRunnable

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

		self._session = session
		self._progression = progression
		self.signals = PackerWorkerSignals()

    # -------------------------------------------------------------------------
	def run(self):
		tasks = self._session.tasks()

		for index, task in enumerate(tasks):
			self.signals.runTaskId.emit(index)
			packer = createPacker(task, index)
			packer.progress.connect(self._progression.updateTaskProgress)
			packer.finish.connect(self._progression.updateGlobalProgress)
			packer.run()