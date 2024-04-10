"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
import zipfile
from zipfile import ZipFile

# PackY
from model.packer import Packer
from model.packer_data import PackerData
from model.task import Task

###############################################################################
class ZipPacker(Packer):

	###########################################################################
	# SPECIAL METHODS
	###########################################################################

    # -------------------------------------------------------------------------
	def __init__(self, task: Task):
		super(ZipPacker, self).__init__(task)

	###########################################################################
	# PUBLIC MEMBER FUNCTIONS
	###########################################################################
		
	# -------------------------------------------------------------------------
	def packTmpFolder(self, task: Task, tmp_folder_path: str):
		try:
			destination_filename = task.destFile()
			packer_data = task.packerData()

			[c_method, c_level] = self.__convertPackerData(packer_data)

			with ZipFile(destination_filename, mode = "w", compression=c_method, compresslevel=c_level) as m_zip:
				self.__packDir(m_zip, tmp_folder_path)
		except OSError as ex:
			raise ex
	
	###########################################################################
	# PRIVATE MEMBER FUNCTIONS
	###########################################################################

	# -------------------------------------------------------------------------
	def __convertPackerData(self, packer_data: PackerData):
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
				raise Exception("Packer extension not recognized")
		
		return [c_method, c_level]

	# -------------------------------------------------------------------------
	def __packDir(self, m_zip, path):
		try:
			for root, dirs, files in os.walk(path):
				for dir in dirs:
					info_msg: str = f"Packing \"{dir}\""
					self.signals.info.emit(info_msg)
					m_zip.write(os.path.join(root, dir), os.path.relpath(os.path.join(root, dir), os.path.join(path, '.')))

				for file in files:
					info_msg: str = f"Packing \"{file}\""
					self.signals.info.emit(info_msg)
					m_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '.')))
		except OSError as ex:
			raise ex
