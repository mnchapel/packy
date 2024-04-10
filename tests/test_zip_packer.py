"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import json
import os
import pathlib
import pytest
import zipfile
from unittest.mock import MagicMock, Mock
from zipfile import ZipFile, ZipInfo

# PyQt
from PyQt6.QtCore import QStandardPaths

# PackY
from model.task import Task
from model.zip_packer import ZipPacker

# PackY tests
from utils_func import camelCaseToSnakeCase

###############################################################################
# FILE HIERARCHY
#
# -----------------------------------------------------------------------------
# tmp_path
# ├─ folder
# │  ├─ file1.txt
# │  ├─ dir1
# │  │  ├─ file2.txt
# │  │  └─ file3.txt
# │  └─ dir2
# ├─ snapshots
# │  ├─ output_1.zip
# │  ├─ output_2.zip
# │  ├─ output_3.zip
# │  └─ output_4.zip
# └─ results 
#
###############################################################################

###############################################################################
# GLOBAL VARIABLES
###############################################################################

test_data_folder = pathlib.Path("tests", "data", "zip_packer")

###############################################################################
# MODULE FIXTURE SCOPE
###############################################################################

# -----------------------------------------------------------------------------
@pytest.fixture
def loadFileHierarchy(request, tmp_path):
	file = pathlib.Path(request.config.rootdir, test_data_folder, "file_hierarchy").with_suffix(".json")
	file_txt = file.read_text()
	a_tmp_path = str(tmp_path).replace("\\", "/")
	file_txt = file_txt.replace("tmp_path", a_tmp_path)
	data = json.loads(file_txt)

	yield data

# -----------------------------------------------------------------------------
@pytest.fixture
def loadTestData(request, tmp_path):
	json_filename = camelCaseToSnakeCase(request.cls.__name__[4:])
	file = pathlib.Path(request.config.rootdir, test_data_folder, json_filename).with_suffix(".json")
	file_txt = file.read_text()
	
	# Replace tmp_path
	a_tmp_path = str(tmp_path).replace("\\", "/")
	file_txt = file_txt.replace("tmp_path", a_tmp_path)

	# Replace tmp_os_path
	tmp_os_location = QStandardPaths.StandardLocation.TempLocation
	tmp_os_path = QStandardPaths.writableLocation(tmp_os_location)
	tmp_os_path = tmp_os_path.replace("\\", "/")
	file_txt = file_txt.replace("tmp_os_path", tmp_os_path)

	data = json.loads(file_txt)

	yield data

# -----------------------------------------------------------------------------
def recursive(fh_dict):
	for node in fh_dict:
		type = node["type"]

		match type:
			case "file":
				open(node["path"], "w").close()
			case "folder":
				os.makedirs(node["path"])
			case "zip":
				with ZipFile(node["path"], mode = "w") as zip:
					zip.writestr(ZipInfo("empty/"), "")
			case _:
				raise Exception("")

		if "children" in node:
			recursive(node["children"])

# -----------------------------------------------------------------------------
@pytest.fixture
def createFileHierarchy(loadFileHierarchy):
	fh_dict = loadFileHierarchy

	recursive(fh_dict["root"])
		
###############################################################################
# TEST PACK TMP FOLDER
#
# -----------------------------------------------------------------------------
# Description:
#		???.
#
# -----------------------------------------------------------------------------
# - one_file: ???.
# - one_dir: ???.
# - empty_dir: ???.
#
###############################################################################
class TestPackTmpFolder:
	
	test_list = [
		"one_file",
		"one_dir",
		"empty_dir",
		"complex_dir"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, createFileHierarchy, loadTestData, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]

		mock_task = Mock(Task)
		mock_task.destFile = MagicMock(return_value = input["destination_file"])
		
		tmp_folder_path = input["tmp_dir_path"]
		destination_filename = input["destination_file"]
		c_method = zipfile.ZIP_STORED
		c_level = 0
		zip_packer = ZipPacker(mock_task)

		with ZipFile(destination_filename, mode = "w", compression=c_method, compresslevel=c_level) as m_zip:
			zip_packer._ZipPacker__packDir(m_zip, tmp_folder_path)
		
		m_zip = zipfile.ZipFile(destination_filename, "r")
		for item in expected:
			assert(item in m_zip.namelist())
		
		assert(len(expected) == len(m_zip.namelist()))
