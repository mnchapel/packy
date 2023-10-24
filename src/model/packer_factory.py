"""
author: Marie-Neige Chapel
"""

# PackY
from model.task import Task
from model.zip_packer import ZipPacker

###############################################################################
# class PackerFactory:

# -------------------------------------------------------------------------
def createPacker(task: Task, index:int):
	extension = task.packerData().extension()

	match extension:
		case "zip" | "lzma":
			return ZipPacker(task, index)
		case _:
			raise Exception("[createPacker] extension not recognized.")
