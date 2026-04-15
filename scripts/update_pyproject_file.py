"""Update the ``tool.pyside6-project.files`` section in a pyproject.toml file.

This module provides utilities to validate command-line arguments, collect
project files from directories and explicit paths, and update the
``pyproject.toml`` configuration accordingly. It is designed to automate the
maintenance of the file list used by PySide6 project tooling.

Typical usage example:

  python update_pyproject_file.py \
      --relative-to /path/to/project \
      --include-directory src \
      --include-file main.py

Copyright 2026-present, Elias Mueller (<https://github.com/trin94>)
All rights reserved.

See this link for more info: <https://github.com/trin94/PySide6-project-template>
"""

# Standard library
import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Standard library
    from collections.abc import Iterable


###############################################################################
class PyProjectFileError(Exception):
    """Base class for exceptions raised while processing pyproject.toml."""


class SectionNotFoundError(PyProjectFileError):
    """A required section is missing from pyproject.toml."""

    def __init__(self, section: str) -> None:
        """Initialize the exception with the missing section name.

        Args:
            section: The name of the missing section.
        """
        msg = f'Could not find "{section}" in pyproject.toml'
        super().__init__(msg)


class KeyNotFoundError(PyProjectFileError):
    """A required key is missing from a specific table in pyproject.toml."""

    def __init__(self, key: str, table: str) -> None:
        """Initialize the exception with the missing key and table.

        Args:
            key: The name of the missing key.
            table: The table in which the key was expected.
        """
        msg = f'Could not find {key} in "{table}" table in pyproject.toml'
        super().__init__(msg)


class MalformedFileError(PyProjectFileError):
    """The pyproject.toml file structure prevents updating the files section."""

    def __init__(self) -> None:
        """Initialize the exception with a default error message."""
        super().__init__("Could not update yproject.toml")


###############################################################################
class CmdArgumentValidator:
    """Validate command-line arguments related to filesystem paths.

    This class performs validation of directories and files provided via
    command-line arguments. It accumulates validation errors and provides
    a mechanism to terminate execution if any invalid input is detected.

    Attributes:
        __errors: A list of error messages collected during validation.
    """

    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """Initializes the validator with an empty error list."""
        self.__errors: list[str] = []

    # -------------------------------------------------------------------------
    def validate_directory(self, directory: Path) -> None:
        """Validate that a given path exists and is a directory.

        Args:
            directory: The path to validate as a directory.
        """
        if not directory.exists():
            self.__errors.append(f"Directory {directory} does not exist")
        elif not directory.is_dir():
            self.__errors.append(f"Directory {directory} is not a directory")

    # -------------------------------------------------------------------------
    def validate_directories(self, directories: list[Path]) -> None:
        """Validate a list of directory paths.

        Args:
            directories: A list of paths to validate as directories.
        """
        for directory in directories:
            self.validate_directory(directory)

    # -------------------------------------------------------------------------
    def validate_files(self, files: list[Path]) -> None:
        """Validate a list of file paths.

        Args:
            files: A list of paths to validate as files.
        """
        for file in files:
            self._validate_file(file)

    # -------------------------------------------------------------------------
    def _validate_file(self, file: Path) -> None:
        """Validate that a given path exists and is a file.

        Args:
            file: The path to validate as a file.
        """
        if not file.exists():
            self.__errors.append(f"File {file} does not exist")
        elif not file.is_file():
            self.__errors.append(f"File {file} is not a file")

    # -------------------------------------------------------------------------
    def break_on_errors(self) -> None:
        """Print all collected errors and terminate execution if any exist."""
        if errors := self.__errors:
            for error in errors:
                print(error, file=sys.stderr)  # noqa: T201
            sys.exit(1)


###############################################################################
class ProjectFileUpdater:
    """Collect and update project file entries in pyproject.toml.

    This class aggregates files from specified directories and individual
    file paths, filters them based on extension rules, and updates the
    ``tool.pyside6-project.files`` section in the ``pyproject.toml`` file.

    Attributes:
        __root_dir: The root directory used to compute relative paths.
        __files: A set of collected file paths.
    """

    __FILENAME = "pyproject.toml"
    __EXTENSIONS_IGNORED = frozenset({".pyc", ".qm"})

    # -------------------------------------------------------------------------
    def __init__(self, root_dir: Path) -> None:
        """Initialize the updater with a root directory.

        Args:
            root_dir: The root directory used to relativize collected files.
        """
        self.__root_dir = root_dir
        self.__files: set[Path] = set()

    # -------------------------------------------------------------------------
    def add(self, directories: list[Path], files: list[Path]) -> None:
        """Add files from directories and explicit file paths.

        Recursively scans provided directories and includes all files except
        those with ignored extensions. Explicit file paths are also added if
        valid and not ignored.

        Args:
            directories: A list of directories to scan recursively.
            files: A list of individual files to include.
        """
        for directory in directories:
            for path in directory.rglob("*"):
                if path.is_file() and path.suffix not in self.__EXTENSIONS_IGNORED:
                    self.__files.add(path)
        for file in files:
            if file.is_file() and file.suffix not in self.__EXTENSIONS_IGNORED:
                self.__files.add(file)

    # -------------------------------------------------------------------------
    def make_files_relative(self) -> None:
        """Convert all collected file paths to paths relative to root_dir."""
        self.__files = {p.relative_to(self.__root_dir) for p in self.__files}

    # -------------------------------------------------------------------------
    def sorted_files_as_str(self) -> list[str]:
        """Return sorted collected file paths as POSIX-style strings.

        Returns:
            A list of sorted file paths as POSIX-formatted strings.
        """
        return [str(p.as_posix()) for p in sorted(self.__files)]

    # -------------------------------------------------------------------------
    def update_pyproject_toml(self) -> None:
        """Update the pyproject.toml file with collected file entries.

        Reads the existing pyproject.toml file, determines the correct section
        to update, and writes the updated content if changes are detected.

        Raises:
            SystemExit: If the required section or keys cannot be found.
        """
        pyproject_path = Path(self.__FILENAME)
        original = pyproject_path.read_text(encoding="utf-8").splitlines(keepends=True)

        try:
            updated = ProjectFileUpdater.determine_new_pyproject_lines(
                existing_lines=original,
                qt_files=self.sorted_files_as_str(),
            )
        except KeyError as e:
            print(str(e), file=sys.stderr)  # noqa: T201
            sys.exit(1)
        except ValueError as e:
            print(str(e), file=sys.stderr)  # noqa: T201
            sys.exit(1)

        if updated != original:
            pyproject_path.write_text("".join(updated), encoding="utf-8")

    # -------------------------------------------------------------------------
    @staticmethod
    def determine_new_pyproject_lines(
        existing_lines: list[str],
        qt_files: Iterable[str],
    ) -> list[str]:
        """Generate updated lines for the pyproject.toml file.

        Replaces the existing ``files`` section within the
        ``[tool.pyside6-project]`` table with a newly generated list of files.

        Args:
            existing_lines: The original lines of the pyproject.toml file.
            qt_files: An iterable of file paths to include in the files section.

        Returns:
            A list of updated lines for the pyproject.toml file.
        """
        start, end = ProjectFileUpdater.determine_line_to_overwrite(existing_lines)
        lines: list[str] = [
            "files = [\n",
            "  # WARNING! This list is auto updated by the just build helper\n",
            *[f'  "{path}",\n' for path in qt_files],
            "]\n",
        ]
        return existing_lines[: start - 1] + lines + existing_lines[end:]

    # -------------------------------------------------------------------------
    @staticmethod
    def determine_line_to_overwrite(lines: list[str]) -> tuple[int, int]:
        """Locate the line range of the ``files`` section to overwrite.

        Scans the provided lines to find the ``[tool.pyside6-project]`` section
        and determines the start and end indices of the ``files`` entry.

        Args:
            lines: The lines of the pyproject.toml file.

        Raises:
            SectionNotFoundError: If the ``[tool.pyside6-project]`` section
                cannot be found in the provided lines.
            KeyNotFoundError: If the ``files`` key is missing within the
                ``[tool.pyside6-project]`` section.
            MalformedFileError: If the ``files`` section boundaries cannot
                be determined due to malformed content.

        Returns:
            A tuple (start, end) representing the line indices to replace.
        """
        in_section = False
        files_start: int | None = None

        for i, raw in enumerate(lines):
            line = raw.strip()

            if not in_section:
                if line == "[tool.pyside6-project]":
                    in_section = True
                continue

            if files_start is None and line.startswith("files ="):
                if line.endswith("]"):
                    return i + 1, i + 1
                files_start = i + 1
                continue

            if files_start is not None and ("]" in line) and not line.startswith("#"):
                return files_start, i + 1

        if not in_section:
            raise SectionNotFoundError("[tool.pyside6-project]")
        if files_start is None:
            raise KeyNotFoundError("files", "[tool.pyside6-project]")
        raise MalformedFileError


# -------------------------------------------------------------------------
def main() -> None:
    """Parse command-line arguments and execute the update process."""
    parser = argparse.ArgumentParser(
        description="Update tool.pyside6-project.files table in pyproject.toml",
    )
    parser.add_argument(
        "--relative-to",
        type=str,
        required=True,
        help="Root directory to make files relative to",
    )
    parser.add_argument(
        "--include-directory",
        type=str,
        action="append",
        default=[],
        help="Directory to include",
    )
    parser.add_argument(
        "--include-file",
        type=str,
        action="append",
        default=[],
        help="File to include",
    )
    run(parser.parse_args())


# -------------------------------------------------------------------------
def run(args: argparse.Namespace) -> None:
    """Execute the file collection and pyproject update workflow.

    Args:
        args: Parsed command-line arguments containing input paths.
    """
    root_dir = Path(args.relative_to).absolute()
    directories = [Path(p).absolute() for p in args.include_directory]
    files = [Path(p).absolute() for p in args.include_file]

    validator = CmdArgumentValidator()
    validator.validate_directory(root_dir)
    validator.validate_directories(directories)
    validator.validate_files(files)
    validator.break_on_errors()

    updater = ProjectFileUpdater(root_dir)
    updater.add(directories, files)
    updater.make_files_relative()
    updater.update_pyproject_toml()


if __name__ == "__main__":
    main()
