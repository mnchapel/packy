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
import re
from unittest.mock import MagicMock, Mock
from zipfile import is_zipfile, ZipFile, ZipInfo

# PyQt
from PyQt6.QtCore import QStandardPaths

# PackY
import model.task
from model.preferences import PreferencesKeys
from model.task import Task
from model.files_model import FilesModel
from model.zip_packer import ZipPacker
from utils.settings_access import packySettings

# PackY tests
from utils_func import camelCaseToSnakeCase
from utils_func import joinPath

###############################################################################
# FILE HIERARCHY
#
# -----------------------------------------------------------------------------
# tmp_path
# ├─ folder
# │  ├─ file1.txt
# │  └─ dir1
# │     ├─ file2.txt
# │     └─ file3.txt
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

test_data_folder = pathlib.Path("tests", "data", "packer")

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

# -----------------------------------------------------------------------------
@pytest.fixture
def checkArchiveHierarchy(loadTestData, outputPath, test_name):
	data = loadTestData[test_name]["expected"]
	expected_hierarchy = data["archive_hierarchy"]

	output_path = outputPath
	zip = ZipFile(output_path)

	output_name = os.path.basename(output_path)
	output_name = output_name.rsplit(".", 1)[0]
	expected_hierarchy = [output_name + "/" + item for item in expected_hierarchy]

	assert zip.namelist() == expected_hierarchy

###############################################################################
# TEST ZIP PACKER
#
# -----------------------------------------------------------------------------
# test_pack_file_1
# -----------------------------------------------------------------------------
#
# Description:
#		Pack a file at the root.
#
# Expected:
#		tmp_path/output_<snapshot_retention_options>.zip
#
# -----------------------------------------------------------------------------
# test_pack_file_2
# -----------------------------------------------------------------------------
#
# Description:
#		Pack a file inside a folder.
#
# Expected:
#		tmp_path/output_<snapshot_retention_options>.zip
#
# -----------------------------------------------------------------------------
# test_pack_folder_1
# -----------------------------------------------------------------------------
#
# Description:
#		Pack a folder and the files inside.
#
# Expected:
#		tmp_path/output_<snapshot_retention_options>.zip
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
			yield joinPath(dirname, snapshot[0])
		else:
			yield ""

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", ["test_pack_file_1", "test_pack_file_2", "test_pack_folder_1"])
	def testPackFile(self, createFileHierarchy, runZipPacker, outputPath, checkArchiveHierarchy, test_name):
		output_path = outputPath

		assert output_path
		assert is_zipfile(output_path)
		
###############################################################################
# TEST TMP FOLDER PATH
#
# -----------------------------------------------------------------------------
# Description:
#		Produce the temporary folder path according to the output archive name.
#
# -----------------------------------------------------------------------------
# - simple_test: output archive name with one word.
# - complex_test: output archive name with several words (separated by "_").
# - spaces_test: output archive name with several words (separated by " ").
#
###############################################################################
class TestTmpFolderPath():

	test_list = [
		"simple_test",
		"complex_test",
		"spaces_test"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, loadTestData, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]

		mock_task = Mock(Task)
		mock_task.destFile = MagicMock(return_value = input)
		
		zip_packer = ZipPacker(mock_task)
		tmp_folder_path = zip_packer._Packer__tmpFolderPath()
		tmp_folder_path = tmp_folder_path.replace("\\", "/")

		expected = joinPath(os.path.dirname(model.task.__file__), expected)

		assert tmp_folder_path == expected

###############################################################################
# TEST FILTER SELECTED FILES
#
# -----------------------------------------------------------------------------
# Description:
#		The function selects the items (files and directories) that are checked
#		or partially checked to be packed.
#
# -----------------------------------------------------------------------------
# - no_items: no items.
# - item_checked: one item is checked.
# - item_partially_checked: one item is partially cheched.
# - item_unchecked: one item is unchecked.
# - item_mixed: items are unchecked, checked and partially checked.
#
###############################################################################
class TestFilterSelectedFiles():

	test_list = [
		"no_items",
		"item_checked",
		"item_partially_checked",
		"item_unchecked",
		"item_mixed"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, loadTestData, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]

		mock = Mock(Task)
		mock_files_model = Mock(FilesModel)
		mock_files_model.checks = MagicMock(return_value = input)
		mock.filesSelected = MagicMock(return_value = mock_files_model)

		zip_packer = ZipPacker(mock)
		items_to_pack = zip_packer._Packer__filterSelectedFiles()

		assert items_to_pack == expected


###############################################################################
# TEST COPY ITEMS TO TMP FOLDER
#
# -----------------------------------------------------------------------------
# Description:
#		Copy items to pack into a temporary folder.
#
# -----------------------------------------------------------------------------
# - no_items: no items.
# - one_file: one file.
# - complete_dir: a folder and its files.
#
###############################################################################
class TestCopyItemsToTmpFolder():

	test_list = [
		"no_items",
		"one_file",
		"complete_dir"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, createFileHierarchy, loadTestData, test_name, tmp_path):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]
		
		mock_files_model = Mock(FilesModel)
		mock_files_model.rootPath = MagicMock(return_value = joinPath(tmp_path, "folder"))

		mock_task = Mock(Task)
		mock_task.filesSelected = MagicMock(return_value = mock_files_model)

		zip_packer = ZipPacker(mock_task)
		tmp_path_task = joinPath(tmp_path, "results", test_name)
		zip_packer._Packer__copyItemsToTmpFolder(input, tmp_path_task)

		for item in expected:
			assert os.path.exists(item)

###############################################################################
# TEST FIND SNAPSHOTS
#
# -----------------------------------------------------------------------------
# Description
#		TODO
#
# -----------------------------------------------------------------------------
# - input: 
# - expected: 
#
# -----------------------------------------------------------------------------
# - 
#
###############################################################################
class TestFindSnapshots():

	test_list = [
		"find_4_snapshots"
	]

	# -------------------------------------------------------------------------
	@pytest.fixture
	def configureSettings(self, loadTestData, test_name):
		settings = packySettings()
		task_suffix = settings.value(PreferencesKeys.TASK_SUFFIX.value, type = int)

		test_task_suffix = loadTestData[test_name]["input"]["task_suffix"]
		settings.setValue(PreferencesKeys.TASK_SUFFIX.value, test_task_suffix)

		yield 

		settings.setValue(PreferencesKeys.TASK_SUFFIX.value, task_suffix)

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, createFileHierarchy, loadTestData, configureSettings, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]
		
		mock_task = Mock(Task)
		mock_task.rawDestFile = MagicMock(return_value = input["raw_dest_file"])
		mock_task.destExtension = MagicMock(return_value = input["dest_extension"])

		zip_packer = ZipPacker(mock_task)
		snapshots = zip_packer._Packer__findSnapshots()

		assert snapshots == expected

###############################################################################
# TEST REMOVE SNAPSHOTS
#
# -----------------------------------------------------------------------------
# Description
#		Remove snapshots according to the snapshot retention.
#
# -----------------------------------------------------------------------------
# - input: 
# - expected: 
#
###############################################################################
class TestRemoveSnapshots():

	test_list = [
		"no_snapshot_to_remove",
		"one_snapshot_to_remove",
		"several_snapshot_to_remove"
	]

	# -------------------------------------------------------------------------
	@pytest.fixture
	def configureSettings(self, loadTestData, test_name):
		settings = packySettings()
		nb_snapshot = settings.value(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, type = int)

		test_nb_snapshot = loadTestData[test_name]["input"]["nb_snapshot"]
		settings.setValue(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, test_nb_snapshot)

		yield 

		settings.setValue(PreferencesKeys.GENERAL_NB_SNAPSHOT.value, nb_snapshot)

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, createFileHierarchy, loadTestData, configureSettings, test_name):
		input = loadTestData[test_name]["input"]
		expected = loadTestData[test_name]["expected"]

		mock_task = Mock(Task)
		raw_dest_file = input["raw_dest_file"]
		mock_task.rawDestFile = MagicMock(return_value = raw_dest_file)

		zip_packer = ZipPacker(mock_task)
		zip_packer._Packer__removeSnapshots(input["snapshots"])

		snapshots_dir = os.path.dirname(raw_dest_file)
		assert len(os.listdir(snapshots_dir)) == len(expected)

		for item in expected:
			assert os.path.exists(item)

###############################################################################
# TEST CLEAN TMP FOLDER
#
# -----------------------------------------------------------------------------
# Description
#		TODO
#
# -----------------------------------------------------------------------------
# - input:  
#
###############################################################################
class TestCleanTmpFolder():

	test_list = [
		"files",
		"tree_hierarchy"
	]

	# -------------------------------------------------------------------------
	@pytest.mark.parametrize("test_name", test_list)
	def test(self, createFileHierarchy, loadTestData, test_name):
		input = loadTestData[test_name]["input"]

		mock_task = Mock(Task)

		zip_packer = ZipPacker(mock_task)
		zip_packer._Packer__cleanTmpFolder(input)

		assert os.path.exists(input) is False
