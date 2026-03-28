import os
import sys
import subprocess

src_dir = os.path.abspath(os.path.dirname(__file__))
ui_dir = os.path.join(src_dir, "../resources/ui");
py_dir = os.path.join(src_dir, "view");

for filename in os.listdir(ui_dir):
	if filename.endswith(".ui"):
		ui_path = os.path.join(ui_dir, filename)
		ui_abs_path = os.path.abspath(ui_path)
		py_path = os.path.join(py_dir, "ui_" + filename.replace(".ui", ".py"))
		py_abs_path = os.path.abspath(py_path)
		subprocess.run([sys.executable, "-m", "PyQt6.uic.pyuic", ui_path, "-o", py_path])