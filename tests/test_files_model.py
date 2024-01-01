"""
author: Marie-Neige Chapel
"""

# Python
import json
import os
import pathlib
import pytest

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

CHECKED = Qt.CheckState.Checked.value
PARTIALLY_CHECKED = Qt.CheckState.PartiallyChecked.value
UNCHECKED = Qt.CheckState.Unchecked.value

###############################################################################
# UTIL FUNCTIONS
###############################################################################

# -----------------------------------------------------------------------------
def joinPath(path_1, path_2):
	return os.path.join(path_1, path_2).replace("\\", "/")

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
	def loadData(self, request):
		file = pathlib.Path(request.config.rootdir, "tests", "data", "files_model", "json_init").with_suffix(".json")
		data = json.loads(file.read_text())

		yield data
		
	# -----------------------------------------------------------------------------
	@pytest.fixture
	def createJsonDict(self, loadData, request, tmp_path):
		test_name = request.getfixturevalue("test_name")
		test_data = loadData[test_name]["data"]

		json_dict = {}

		if "root_path" in test_data:
			json_dict["root_path"] = str(tmp_path)

		if "check" in test_data:
			json_dict["check"] = test_data["check"]

		yield json_dict

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
#		warnings: added_items = [{}], removed_items = [{}]
#
# -----------------------------------------------------------------------------
# test2
# -----------------------------------------------------------------------------
#
# Description:
#		Test check integrity with warnings.
#
# Expected:
#		warnings: added_items = [{"tmp_path/dir_1/file_2.txt"}], 
#		removed_items = [{"tmp_path/dir_5", "tmp_path/dir_5/file_8.txt"}]
#
###############################################################################
class TestCheckIntegrity():

	# -----------------------------------------------------------------------------
	@pytest.fixture
	def computeWarnings(self, tmp_path, request) -> str:
		json_dict = {}
		json_dict["root_path"] = str(tmp_path)
		
		file = pathlib.Path(request.config.rootdir, "tests", "data", "files_model", "check_integrity").with_suffix(".json")
		data = json.loads(file.read_text())
		test_name = request.getfixturevalue("test_name")
		data_check = data[test_name]["data"]["check"]
		new_data_check = {}

		for key in data_check:
			new_key = joinPath(tmp_path, key)
			new_data_check[new_key] = data_check[key]
		
		json_dict["check"] = new_data_check

		files_model = FilesModel(json_dict)
		warnings = files_model.warnings()

		yield warnings

	# -----------------------------------------------------------------------------
	@pytest.fixture
	def loadExpected(self, tmp_path, request):
		file = pathlib.Path(request.config.rootdir, "tests", "data", "files_model", "check_integrity").with_suffix(".json")
		data = json.loads(file.read_text())
		test_name = request.getfixturevalue("test_name")
		warnings_data = data[test_name]["expected"]

		expected_warnings = Warnings()
		for item in warnings_data["added_items"]:
			expected_warnings.addAddedItem(joinPath(tmp_path, item))
		for item in warnings_data["removed_items"]:
			expected_warnings.addRemovedItem(joinPath(tmp_path, item))

		yield expected_warnings

	# -----------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test1", "test2"])
	def test(self, createFileHierarchy, computeWarnings, loadExpected, test_name):
		assert computeWarnings == loadExpected
	
