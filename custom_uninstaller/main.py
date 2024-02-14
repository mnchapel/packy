"""
Copyright 2023-present, Marie-Neige Chapel
All rights reserved.

This source code is licensed under the license found in the
COPYING.md file in the root directory of this source tree.
"""

# Python
import os
import re
import sys
import yaml

# PyQt
from PyQt6.QtCore import QCoreApplication, QStandardPaths

# -----------------------------------------------------------------------------
def metadataPath():
	# current_dir = os.path.dirname(__file__)
	# return os.path.join(current_dir, "../resources/yaml/metadata.yml")

	resources_path =  os.path.join(sys._MEIPASS, "resources")
	return os.path.join(resources_path, "yaml/metadata.yml")

# -----------------------------------------------------------------------------
def initApplication() -> None:
	metadata_path = metadataPath()
	with open(metadata_path, "r") as metadata_file:
		metadata = yaml.safe_load(metadata_file)
		QCoreApplication.setOrganizationName(metadata["CompanyName"])
		QCoreApplication.setApplicationName(metadata["ProductName"])
		QCoreApplication.setOrganizationDomain("packy.fr")
		QCoreApplication.setApplicationVersion(metadata["Version"])

# -----------------------------------------------------------------------------
def packyExtraFolders():
	app_data_location = QStandardPaths.StandardLocation.AppDataLocation
	app_data_path = QStandardPaths.writableLocation(app_data_location)

	extra_folders: list[str] = []
	extra_folders.append(app_data_path)
	extra_folders.append(os.path.dirname(app_data_path))

	for i, folder in enumerate(extra_folders):
		folder = folder + "/"
		extra_folders[i] = folder.replace("/", "\\\\")

	return extra_folders

# -----------------------------------------------------------------------------
def packyExtraFiles():
	app_data_location = QStandardPaths.StandardLocation.AppDataLocation
	app_data_path = QStandardPaths.writableLocation(app_data_location)

	extra_files = []
	extra_files.append(os.path.join(app_data_path, "log.txt").replace("\\", "/"))
	extra_files.append(os.path.join(os.path.dirname(app_data_path), "PackY.ini").replace("\\", "/"))

	return extra_files

# -----------------------------------------------------------------------------
# Create a file to log custome_uninstaller
curr_path = os.path.dirname(__file__)
log_file = open("log_custom_uninstaller.txt", "w")

# Modify Uninstall.dat file

uninstall_dat_path = "../Uninstall.dat"
if os.path.exists(uninstall_dat_path):
	log_file.write("The file Uninstall.dat exists.\n")
	log_file.write(f"	metadata_path = {metadataPath()}\n")
	initApplication()
	log_file.write("test.\n")

	file_content = []
	with open(uninstall_dat_path, "r") as uninstall_file:
		file_content = uninstall_file.readlines()

	log_file.write("Uninstall.dat file content:\n")
	log_file.writelines(file_content)

	# Add folders
	folders_index = [i for i, item in enumerate(file_content) if re.search("^\s*\"Folders\"\s*:\s*\[", item)]
	
	extra_folders = packyExtraFolders()
	folders_insertion_index = folders_index[0] + 1
	for folder in extra_folders:
		folder_dat = f"\"Path\": \"{folder}\"\n"
		file_content.insert(folders_insertion_index, "},\n")
		file_content.insert(folders_insertion_index, folder_dat)
		file_content.insert(folders_insertion_index, "{\n")

	# Add files
	files_index = [i for i, item in enumerate(file_content) if re.search("^\s*\"Files\"\s*:\s*\[", item)]
	extra_files = packyExtraFiles()
	files_insertion_index = files_index[0] + 1
	for file in extra_files:
		file_dat = f"\"Path\": \"{file}\"\n"
		file_content.insert(files_insertion_index, "},\n")
		file_content.insert(files_insertion_index, file_dat)
		file_content.insert(files_insertion_index, "{\n")

	# Write the new content in the .dat file
	with open(uninstall_dat_path, "w") as uninstall_file:
		uninstall_file.writelines(file_content)

else:
	log_file.write("The file Uninstall.dat doesn't exist.")

log_file.close()
