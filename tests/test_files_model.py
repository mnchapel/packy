"""
author: Marie-Neige Chapel
"""

# Python
import os
import pytest

# PackY
from model.files_model import FilesModel

DIR_PATHS = ["dir_1/",
			 "dir_2/"]

FILE_PATHS = ["dir_1/file_1.txt",
			"dir_1/file_2.txt",
			"dir_1/file_3.txt",
			"dir_2/file_4.txt"]

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
	check_dict[os.path.join(tmp_path, FILE_PATHS[0])] = 2
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
