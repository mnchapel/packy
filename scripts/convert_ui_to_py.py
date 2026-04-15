"""Module to convert PyQt6 UI files to Python view files.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Standard library
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Main function."""
    pyside_script_base_dir = Path(sys.executable).parent
    pyside_script_dir = pyside_script_base_dir / "Scripts"
    if sys.platform == "win32":
        pyside_script_path = pyside_script_dir / "pyside6-uic.exe"
    else:
        pyside_script_path = pyside_script_dir / "pyside6-uic"

    if not pyside_script_path.exists():
        raise FileNotFoundError(pyside_script_path)

    project_dir = Path(__file__).parent.parent.resolve()
    ui_dir = (project_dir / "packy" / "ui").resolve()

    for ui_path in ui_dir.iterdir():
        if ui_path.suffix == ".ui":
            py_path = ui_dir / f"ui_{ui_path.stem}.py"

            subprocess.run(# noqa: S603
                [str(pyside_script_path), str(ui_path), "-o", str(py_path)],
                check=True,
                shell=False, # Explicitly disabled for security
            )
            print(f"Generated: {py_path}") # noqa: T201


if __name__ == "__main__":
    main()
