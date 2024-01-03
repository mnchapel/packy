"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
import pathlib
import pytest
import re

# PyQt
from PyQt6.QtCore import Qt

# PackY
from model.files_model import FilesModel
from model.warnings import Warnings

# ------------------------------
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
# ------------------------------

DIR_1 = "dir_1/"
FILE_1 = "dir_1/file_1.txt"
FILE_2 = "dir_1/file_2.txt"
DIR_2 = "dir_2/"
FILE_3 = "dir_2/file_3.txt"
FILE_4 = "dir_2/file_4.txt"
DIR_3 = "dir_3/"
DIR_4 = "dir_3/dir_4/"
FILE_5 = "dir_3/dir_4/file_5.txt"
FILE_6 = "dir_3/file_6.txt"
FILE_7 = "dir_3/file_7.txt"

DIR_PATHS = [DIR_1,
			 DIR_2,
			 DIR_3,
			 DIR_4]

FILE_PATHS = [FILE_1,
			  FILE_2,
			  FILE_3,
			  FILE_4,
			  FILE_5,
			  FILE_6,
			  FILE_7]

test_data_folder = pathlib.Path("tests", "data", "files_model")

###############################################################################
# UTIL FUNCTIONS
###############################################################################

# -----------------------------------------------------------------------------
def joinPath(path_1, path_2):
	return os.path.join(path_1, path_2).replace("\\", "/")

# -----------------------------------------------------------------------------
def camelCaseToSnakeCase(value: str) -> str:
	print("camelCaseToSnakeCase, value = ", value)
	return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()

###############################################################################
# MODULE FIXTURE SCOPE
###############################################################################

# -----------------------------------------------------------------------------
@pytest.fixture
def createFileHierarchy(tmp_path):
	for dir_path in DIR_PATHS:
		os.makedirs(joinPath(tmp_path, dir_path))
	
	for file_path in FILE_PATHS:
		open(joinPath(tmp_path, file_path), "w").close()

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
		
	# -----------------------------------------------------------------------------
	@pytest.fixture
	def createJsonDict(self, loadData, request, tmp_path):
		test_name = request.getfixturevalue("test_name")
		data = loadData[test_name]["data"]

		yield data

	# -----------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test1"])
	def test(self, test_name, createFileHierarchy, createJsonDict):
		json_dict = createJsonDict
		FilesModel(json_dict)
	
	# -----------------------------------------------------------------------------
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

	# -----------------------------------------------------------------------------
	@pytest.fixture
	def computeWarnings(self, loadData, tmp_path, request) -> str:		
		test_name = request.getfixturevalue("test_name")
		json_dict = loadData[test_name]["data"]

		files_model = FilesModel(json_dict)
		warnings = files_model.warnings()

		yield warnings

	# -----------------------------------------------------------------------------
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

	# -----------------------------------------------------------------------------
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

	# -----------------------------------------------------------------------------
	@pytest.fixture
	def computeFilesModel(self, loadData, tmp_path, request):
		test_name = request.getfixturevalue("test_name")
		data = loadData[test_name]["data"]

		files_model = FilesModel(data)
		files_model.updateModel()

		yield files_model

	# -----------------------------------------------------------------------------
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
