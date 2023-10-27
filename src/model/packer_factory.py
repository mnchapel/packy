"""
author: Marie-Neige Chapel
"""

# PackY
from model.task import Task
from model.zip_packer import ZipPacker

# -------------------------------------------------------------------------
def createPacker(task: Task):
	extension = task.packerData().extension()

	match extension:
		case "zip" | "lzma":
			return ZipPacker(task)
		case _:
			raise Exception("[createPacker] extension not recognized.")
