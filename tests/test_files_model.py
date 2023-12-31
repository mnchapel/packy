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

def joinPath(path_1, path_2):
	return os.path.join(path_1, path_2).replace("\\", "/")

###############################################################################
# TEST JSON INITIALIZATION
###############################################################################
	
# -----------------------------------------------------------------------------
# Test a normal initialization
# -----------------------------------------------------------------------------
def testJsonInit1(tmp_path):
	json_dict = {}
	json_dict["root_path"] = str(tmp_path)
	check_dict = {}
	check_dict[joinPath(tmp_path, FILE_PATHS[0])] = 2
	json_dict["check"] = check_dict

	FilesModel(json_dict)

# -----------------------------------------------------------------------------
# Test a wrong initialization: empty dictionary
# Expect a KeyError
# -----------------------------------------------------------------------------
def testJsonInit2(tmp_path):
	json_dict = {}

	try:
		FilesModel(json_dict)
	except KeyError:
		assert True

###############################################################################
# TEST CHECK INTEGRITY
###############################################################################

# -------------------------------------------------------------------------
# test1: test check integrity with no warnings
# -------------------------------------------------------------------------
# test2: test check integrity with warnings
#
# expected_added_items = ["tmp_path/dir_1/file_2.txt"]
# expected_removed_items = ["tmp_path/dir_4/", "tmp_path/dir_4/file_7.txt""]
# -------------------------------------------------------------------------

# -----------------------------------------------------------------------------
@pytest.fixture
def createFileHierarchy(tmp_path):
	for dir_path in DIR_PATHS:
		os.makedirs(joinPath(tmp_path, dir_path))
	
	for file_path in FILE_PATHS:
		open(joinPath(tmp_path, file_path), "w").close()

# -----------------------------------------------------------------------------
@pytest.fixture
def computeWarnings(tmp_path, request) -> str:
	json_dict = {}
	json_dict["root_path"] = str(tmp_path)
	
	file = pathlib.Path(request.config.rootdir, "tests", "test_files_model").with_suffix(".json")
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

# -------------------------------------------------------------------------
@pytest.fixture
def loadExpected(tmp_path, request):
	file = pathlib.Path(request.config.rootdir, "tests", "test_files_model").with_suffix(".json")
	data = json.loads(file.read_text())
	test_name = request.getfixturevalue("test_name")
	warnings_data = data[test_name]["expected"]

	expected_warnings = Warnings()
	for item in warnings_data["added_items"]:
		expected_warnings.addAddedItem(joinPath(tmp_path, item))
	for item in warnings_data["removed_items"]:
		expected_warnings.addRemovedItem(joinPath(tmp_path, item))

	yield expected_warnings

# -------------------------------------------------------------------------
@pytest.mark.parametrize("test_name", ["test1", "test2"])
def testCheckIntegrity(createFileHierarchy, computeWarnings, loadExpected, test_name):
	createFileHierarchy
	warnings = computeWarnings
	expected = loadExpected

	assert warnings == expected
	
