"""
author: Marie-Neige Chapel
"""

# PackY
from model.zip_packer import ZipPacker

###############################################################################
# class PackerFactory:

# -------------------------------------------------------------------------
def createPacker(extension: str):
	match extension:
		case "zip" | "lzma":
			return ZipPacker()
		case _:
			raise Exception("[createPacker] extension not recognized.")
