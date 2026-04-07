"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

See LICENCE.md file for more information.
"""

# PackY
from models.task import Task
from models.zip_packer import ZipPacker


# -----------------------------------------------------------------------------
def createPacker(task: Task):
    extension = task.packerData().extension()

    match extension:
        case "zip" | "lzma":
            return ZipPacker(task)
        case _:
            raise Exception("[createPacker] extension not recognized.")
