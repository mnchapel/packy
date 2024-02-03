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

# PackY
from model.files_model import FilesModel
from model.warnings import Warnings

# PackY tests
from utils_func import camelCaseToSnakeCase

###############################################################################
# FILE HIERARCHY
#
# -----------------------------------------------------------------------------
# tmp_path
# ├─ dir_1
# │  ├─ file_1.txt
# │  └─ file_2.txt
# ├─ dir_2
# │  ├─ file_3.txt
# │  └─ file_4.txt
# └─ dir_3
#    ├─ dir_4
#    │  └─ file_5.txt
#    ├─ file_6.txt
#    └─ file_7.txt
#
###############################################################################

###############################################################################
# GLOBAL VARIABLES
###############################################################################

test_data_folder = pathlib.Path("tests", "data", "files_model")

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
def loadData(request, tmp_path):
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
# TEST JSON INITIALIZATION
#
# -----------------------------------------------------------------------------
# test1
# -----------------------------------------------------------------------------
#
# Description:
#		Test a normal initialization.
#
# Expected:
#		FilesModel created without exception.
#
# -----------------------------------------------------------------------------
# test2
# -----------------------------------------------------------------------------
#
# Description:
#		Test a wrong initialization with an empty dictionary.
#
# Expected:
#		KeyError
#
###############################################################################
class TestJsonInit():
		
	# -------------------------------------------------------------------------
	@pytest.fixture
	def createJsonDict(self, loadData, request, tmp_path):
		test_name = request.getfixturevalue("test_name")
		data = loadData[test_name]["data"]

		yield data

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test1"])
	def test(self, test_name, createFileHierarchy, createJsonDict):
		json_dict = createJsonDict
		FilesModel(json_dict)
	
	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test2"])
	def testKeyError(self, test_name, createFileHierarchy, createJsonDict):
		with pytest.raises(KeyError):
			json_dict = createJsonDict
			FilesModel(json_dict)

###############################################################################
# TEST CHECK INTEGRITY
#
# -----------------------------------------------------------------------------
# test1
# -----------------------------------------------------------------------------
#
# Description:
#		Test check integrity with no warnings.
#
# Expected:
#		warnings:
#		- added_items = [{}],
#		- removed_items = [{}]
#
# -----------------------------------------------------------------------------
# test2
# -----------------------------------------------------------------------------
#
# Description:
#		Test check integrity with warnings.
#
# Expected:
#		warnings:
#		- added_items = [{"tmp_path/dir_1/file_2.txt"}], 
#		- removed_items = [{
#			"tmp_path/dir_5",
#			"tmp_path/dir_5/file_8.txt"
#		  }]
#
###############################################################################
class TestCheckIntegrity():

	# -------------------------------------------------------------------------
	@pytest.fixture
	def computeWarnings(self, loadData, tmp_path, request) -> str:		
		test_name = request.getfixturevalue("test_name")
		json_dict = loadData[test_name]["data"]

		files_model = FilesModel(json_dict)
		warnings = files_model.warnings()

		yield warnings

	# -------------------------------------------------------------------------
	@pytest.fixture
	def loadExpected(self, loadData, tmp_path, request):
		test_name = request.getfixturevalue("test_name")
		data = loadData[test_name]["expected"]

		expected_warnings = Warnings()
		for item in data["added_items"]:
			expected_warnings.addAddedItem(item)
		for item in data["removed_items"]:
			expected_warnings.addRemovedItem(item)

		yield expected_warnings

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test1", "test2"])
	def test(self, createFileHierarchy, computeWarnings, loadExpected, test_name):
		assert computeWarnings == loadExpected

###############################################################################
# TEST UPDATE MODEL
#
# -----------------------------------------------------------------------------
# test1
# -----------------------------------------------------------------------------
#
# Description:
#		Test update model with added_items.
#
# Expected:
#		files_model:
#		- root_path = "tmp_path",
#		- check = {
#			"tmp_path/dir_1": 2,
#			"tmp_path/dir_1/file_1.txt": 2,
#			"tmp_path/dir_1/file_2.txt": 2,
#			"tmp_path/dir_2": 1,
#			"tmp_path/dir_2/file_3.txt": 2"
#		  }
#
# -----------------------------------------------------------------------------
# test2
# -----------------------------------------------------------------------------
#
# Description:
#		Test update model with removed_items.
#
# Expected:
#		files_model:
#		- root_path = "tmp_path",
#		- check = {
#			"tmp_path/dir_1/": 2,
#			"tmp_path/dir_1/file_1.txt": 2,
#			"tmp_path/dir_1/file_2.txt": 2,
#			"tmp_path/dir_2/": 1,
#			"tmp_path/dir_2/file_3.txt": 2
#		  }
#
# -----------------------------------------------------------------------------
# test3
# -----------------------------------------------------------------------------
#
# Description:
#		Test update model with added_items and removed_items.
#
# Expected:
#		files_model:
#		- root_path = "tmp_path",
#		- check = {
#			"tmp_path/dir_1/": 2,
#			"tmp_path/dir_1/file_1.txt": 2,
#			"tmp_path/dir_1/file_2.txt": 2,
#			"tmp_path/dir_2/": 1,
#			"tmp_path/dir_2/file_3.txt": 2
#		  }
#
###############################################################################
class TestUpdateModel():

	# -------------------------------------------------------------------------
	@pytest.fixture
	def computeFilesModel(self, loadData, tmp_path, request):
		test_name = request.getfixturevalue("test_name")
		data = loadData[test_name]["data"]

		files_model = FilesModel(data)
		files_model.updateModel()

		yield files_model

	# -------------------------------------------------------------------------
	@pytest.fixture
	def loadExpected(self, loadData, tmp_path, request):
		test_name = request.getfixturevalue("test_name")
		data = loadData[test_name]["expected"]

		expected_files_model = FilesModel(data)

		yield expected_files_model

# -----------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test1", "test2", "test3"])
	def test(self, createFileHierarchy, computeFilesModel, loadExpected, test_name):
		assert computeFilesModel == loadExpected
