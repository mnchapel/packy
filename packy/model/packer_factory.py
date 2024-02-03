"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# PackY
from model.task import Task
from model.zip_packer import ZipPacker

# -----------------------------------------------------------------------------
def createPacker(task: Task):
	extension = task.packerData().extension()

	match extension:
		case "zip" | "lzma":
			return ZipPacker(task)
		case _:
			raise Exception("[createPacker] extension not recognized.")
