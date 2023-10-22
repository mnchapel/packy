"""
author: Marie-Neige Chapel
"""

# Python
import os
import zipfile
from zipfile import ZipFile

# PackY
from model.packer import Packer
from model.packer_data import PackerData
from model.task import Task

class ZipPacker(Packer):

	# -------------------------------------------------------------------------
	def packItems(self, task: Task, items: set):

		destination_filename = task.destinationFile()
		packer_data = task.packerData()

		[c_method, c_level] = self.convertPackerData(packer_data)

		with ZipFile(destination_filename, mode = "w", compression=c_method, compresslevel=c_level) as m_zip:
			for item in items:
				if os.path.isdir(item):
					self.packDir(m_zip, item)
				else:
					self.packFile(m_zip, item)

	# -------------------------------------------------------------------------
	def convertPackerData(self, packer_data: PackerData):
		extension = packer_data.extension()
		method = packer_data.compressionMethod()
		level = packer_data.compressionLevel()

		c_method = zipfile.ZIP_STORED
		c_level = None

		match extension:
			case "zip":
				if method == 1:
					c_method = zipfile.ZIP_DEFLATED

					if level == 0: # No compression
						c_level = 0
					elif level == 1: # Best compression
						c_level = 9
					elif level == 2: # Default
						c_level == 6
					elif level == 3: # Fastest
						c_level = 1

			case "lzma":
				c_method = zipfile.ZIP_LZMA
				level = None
			case _:
				print("Exception")
		
		return [c_method, c_level]
	
	# -------------------------------------------------------------------------
	def packDir(self, m_zip, path):
		for root, _, files in os.walk(path):
			for file in files:
				m_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
	
    # -------------------------------------------------------------------------
	def packFile(self, m_zip, path):
		m_zip.write(path, os.path.basename(path))
