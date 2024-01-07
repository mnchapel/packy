"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
import pathlib
from zipfile import is_zipfile
import pytest
import re

# PackY
from model.task import Task
from model.zip_packer import ZipPacker

###############################################################################
# FILE HIERARCHY
# -----------------------------------------------------------------------------
#
# tmp_path
# ├─ folder
# │  ├─ file1.txt
# │  └─ dir1
# │     ├─ file2.txt
# │     └─ file3.txt
# └─ results
#
# - tmp_path/folder: contains the files and the folders that will be packed.
# - tmp_path/results: contains the archive (result of the packer). 
#
###############################################################################

###############################################################################
# GLOBAL VARIABLES
###############################################################################

test_data_folder = pathlib.Path("tests", "data", "packer")

###############################################################################
# UTIL FUNCTIONS
###############################################################################

# -----------------------------------------------------------------------------
def camelCaseToSnakeCase(value: str) -> str:
	return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()

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
	a_tmp_path = str(tmp_path).replace("\\", "/")
	file_txt = file_txt.replace("tmp_path", a_tmp_path)
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
# TEST ZIP PACKER
#
# -----------------------------------------------------------------------------
# testPackFile
# -----------------------------------------------------------------------------
#
# Description:
#		TODO
#
# Expected:
#		TODO
#
###############################################################################
class TestZipPacker():

	# -------------------------------------------------------------------------
	@pytest.fixture
	def runZipPacker(self, loadTestData, test_name):
		task_dict = loadTestData[test_name]["data"]
		task = Task(task_dict["id"], task_dict)
		zip_packer = ZipPacker(task)
		zip_packer.run()

	# -------------------------------------------------------------------------
	@pytest.fixture
	def outputPath(self, loadTestData, test_name):
		data = loadTestData[test_name]["expected"]
		dirname = data["dst_folder"]

		suffix_pattern_date = "_[0-9]{4}_[0-9]{2}_[0-9]{2}"
		suffix_pattern_version = "_[0-9]+"

		file_pattern_date = data["dst_raw_basename"] + suffix_pattern_date + ".zip"
		file_pattern_version = data["dst_raw_basename"] + suffix_pattern_version + ".zip"

		snapshot_date = [f for f in filter(re.compile(file_pattern_date).match, os.listdir(dirname))]
		snapshot_version = [f for f in filter(re.compile(file_pattern_version).match, os.listdir(dirname))]

		snapshot = snapshot_date + snapshot_version

		if len(snapshot) == 1:
			yield os.path.join(dirname, snapshot[0])
		else:
			yield ""

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test_pack_file1", "test_pack_file2", "test_pack_folder1"])
	def testPackFile(self, createFileHierarchy, runZipPacker, outputPath, test_name):
		output_path = outputPath

		assert output_path
		assert is_zipfile(output_path)
