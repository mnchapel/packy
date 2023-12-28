"""
author: Marie-Neige Chapel
"""

# Python
import os
import pytest

# PyQt
from PyQt6.QtCore import Qt

# PackY
from model.files_model import FilesModel

# ------------------------------
# tmp_path
# ├─ dir_1
# │  ├─ file_1.txt
# │  └─ file_2.txt
# ├─ dir_2
# │  ├─ file_3.txt
# │  └─ file_4.txt
# └─ dir_3
#    ├─ file_5.txt
#    └─ file_6.txt
# ------------------------------

DIR_PATHS = ["dir_1/",
			 "dir_2/",
			 "dir_3/"]

FILE_PATHS = ["dir_1/file_1.txt",
			"dir_1/file_2.txt",
			"dir_2/file_3.txt",
			"dir_2/file_4.txt",
			"dir_3/file_5.txt",
			"dir_3/file_6.txt"]

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

# -----------------------------------------------------------------------------
def createFileHierarchy(tmp_path):
	for dir_path in DIR_PATHS:
		os.makedirs(joinPath(tmp_path, dir_path))
	
	for file_path in FILE_PATHS:
		open(joinPath(tmp_path, file_path), "w").close()

# -----------------------------------------------------------------------------
def createJsonDict1(tmp_path) -> str:
	# ------------------------------
	# tmp_path
	# ├─ dir_1            checked
	# │  ├─ file_1.txt    checked
	# │  └─ file_2.txt    checked
	# ├─ dir_2            partially cheked
	# │  ├─ file_3.txt    checked
	# │  └─ file_4.txt    unchecked
	# └─ dir_3            unchecked
	#    ├─ file_5.txt    unchecked
	#    └─ file_6.txt    unchecked
	# ------------------------------

	json_dict = {}
	json_dict["root_path"] = str(tmp_path)
	check_dict = {}
	check_dict[joinPath(tmp_path, DIR_PATHS[0])] = CHECKED # dir_1/
	check_dict[joinPath(tmp_path, FILE_PATHS[0])] = CHECKED # dir_1/file_1.txt
	check_dict[joinPath(tmp_path, FILE_PATHS[1])] = CHECKED # dir_1/file_2.txt
	check_dict[joinPath(tmp_path, DIR_PATHS[1])] = PARTIALLY_CHECKED # dir_2/
	check_dict[joinPath(tmp_path, FILE_PATHS[2])] = CHECKED # dir_2/file_3.txt
	json_dict["check"] = check_dict
	print(check_dict)

	return json_dict

# -----------------------------------------------------------------------------
def createJsonDict2(tmp_path) -> str:
	# ------------------------------
	# tmp_path
	# ├─ dir_1            checked
	# │  └─ file_1.txt    checked
	# ├─ dir_2            partially cheked
	# │  ├─ file_3.txt    checked
	# │  └─ file_4.txt    unchecked
	# ├─ dir_3            unchecked
	# │  └─ file_5.txt    unchecked
	# └─ dir_4            checked
	# │  └─ file_7.txt    checked
	# ------------------------------

	json_dict = {}
	json_dict["root_path"] = str(tmp_path)
	check_dict = {}
	check_dict[joinPath(tmp_path, DIR_PATHS[0])] = CHECKED # dir_1/
	check_dict[joinPath(tmp_path, FILE_PATHS[0])] = CHECKED # dir_1/file_1.txt
	check_dict[joinPath(tmp_path, DIR_PATHS[1])] = PARTIALLY_CHECKED # dir_2/
	check_dict[joinPath(tmp_path, FILE_PATHS[2])] = CHECKED # dir_2/file_3.txt
	check_dict[joinPath(tmp_path, "dir_4/")] = CHECKED # dir_4/
	check_dict[joinPath(tmp_path, "dir_4/file_7.txt")] = CHECKED # dir_4/file_7.txt
	json_dict["check"] = check_dict

	return json_dict
		
# -------------------------------------------------------------------------
# Test check integrity with no warnings
# -------------------------------------------------------------------------
def testCheckIntegrity1(tmp_path):
	createFileHierarchy(tmp_path)
	json_dict = createJsonDict1(tmp_path)

	files_model = FilesModel(json_dict)
	warnings = files_model.warnings()

	added_items = warnings.addedItems()
	removed_items = warnings.removedItems()

	assert not len(added_items)
	assert not len(removed_items)
		
# -------------------------------------------------------------------------
# Test check integrity with warnings
#
# expected_added_items = ["tmp_path/dir_1/file_1.txt"]
# expected_removed_items = ["tmp_path/dir_4/", "tmp_path/dir_4/file_7.txt""]
# -------------------------------------------------------------------------
def testCheckIntegrity2(tmp_path):
	createFileHierarchy(tmp_path)
	json_dict = createJsonDict2(tmp_path)

	files_model = FilesModel(json_dict)
	warnings = files_model.warnings()

	added_items = warnings.addedItems()
	removed_items = warnings.removedItems()

	expected_added_items = [joinPath(tmp_path, FILE_PATHS[1])]
	expected_removed_items = [joinPath(tmp_path, "dir_4/"),
						   joinPath(tmp_path, "dir_4/file_7.txt")]

	assert added_items == expected_added_items
	assert removed_items == expected_removed_items
