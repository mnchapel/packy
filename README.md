<div align="center">

<figure>
  <img src="resources/img/logo.png" alt="PackY logo" width="160px"/>
</figure>

# PackY

</div>

<p align="center">
  <strong>A simple and intuitive application for creating batch file archives.</strong>
</p>

<p align="center">
  <a rel="license" href="https://www.gnu.org/licenses/gpl-3.0.en.html"><img alt="license" src="https://img.shields.io/badge/license-GNU_GPLv3-brightgreen"></a>
  <img alt="platform" src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey">
  <img alt="stack" src="https://img.shields.io/badge/stack-Python3%20%7C%20PySide6-blue">
  <img alt="status" src="https://img.shields.io/badge/status-in_dev-orange">
  <a rel="ci" href="https://github.com/mnchapel/cooking/actions"><img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/mnchapel/cooking/pages-build-deployment?logo=github&label=Build/CI"></a>
  <img alt="GitHub deployments" src="https://img.shields.io/github/deployments/mnchapel/cooking/pages-build-deployment?logo=github&label=deployment">
  <img alt="Codecov" src="https://img.shields.io/codecov/c/github/mnchapel/cooking?logo=codecov">
  <img alt="No AI" src="https://custom-icon-badges.demolab.com/badge/No%20AI-2f2f2f?logo=non-ai&logoColor=white">
</p>

PackY is a simple and intuitive application designed to create batch file archives. A common use case is to archive configuration files from installed softwares into separate containers, all grouped within a single directory. This project is currently under development, and this page will be updated with additional information over time.

<p align="center">
  <a href="#-features">Features</a> &nbsp;&bull;&nbsp;
  <a href="#-overview">Overview</a> &nbsp;&bull;&nbsp;
  <a href="#-installation">Installation</a> &nbsp;&bull;&nbsp;
  <a href="#-usage">Usage</a> &nbsp;&bull;&nbsp;
  <a href="#️-development">Development</a> &nbsp;&bull;&nbsp;
  <a href="#-resources">Resources</a> &nbsp;&bull;&nbsp;
  <a href="#-contributing">Contributing</a> &nbsp;&bull;&nbsp;
  <a href="#️-roadmap">Roadmap</a> &nbsp;&bull;&nbsp;
  <a href="#️-credits">Credits</a> &nbsp;&bull;&nbsp;
  <a href="#️-license">License</a>
</p>

## ✨ Features

- **Designed for backups** - PackY was originally created as a tool to archive application data prior to backup operations.
- **A simple and practical tool** - PackY intentionally offers a limited set of features to remain accessible to everyone and easy to use.
- **High-quality code** - Thanks to strict linting rules and rigorous testing, the software is built on a reliable and robust codebase. The code aims to be as Pythonic as possible.

## 💠 Overview

### Screenshots

**TODO**

### Built with

- [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/main) - The package and environment manager
- [Python3](https://www.python.org/) - The programming language
- [PySide6](https://doc.qt.io/qtforpython-6/index.html) and [its tools](https://doc.qt.io/qtforpython-6/tools/index.html) - UI Qt framework for Python (in [pythonic version](https://doc.qt.io/qtforpython-6/considerations.html#features)).
- [JSON Schema in Python](https://pypi.org/project/jsonschema/) - An implementation of JSON Schema validation for Python
- [PyYAML](https://pypi.org/project/PyYAML/) - YAML parser
- [pytest](https://docs.pytest.org/en/stable/index.html) - A framework for unit tests
- [pipreqs](https://pypi.org/project/pipreqs/) - A requirements.txt file generator for any project based on imports
- [PyInstaller](https://pypi.org/project/pyinstaller/) - Tool to bundle the app and all its dependencies into a single package
- [Inno Setup](https://jrsoftware.org/isinfo.php) - An installation builder for Windows applications
- [Ruff](https://docs.astral.sh/ruff/) - Code formatter and linter for catching bugs

## 💾 Installation

### Install on Windows

1. Go to the [PackY download page](https://github.com/mnchapel/packy/releases), then download the `PackYInstaller-x.x.x.x.exe` installer.

2. Run the downloaded file to proceed with the installation.

### Install on Linux

The application is currently only available for Windows. A Linux version is planned and will be available in a future release.

### Install on macOS

The application is currently only available for Windows. A macOS version is planned and will be available in a future release.

### Build from source

## 📖 Usage

## 🛠️ Development

### Prerequisites

To build, test, and deploy PackY, the following tools are required:

- [Conda or Miniconda (latest version)](https://anaconda.org/).
- [Python 3.14 or later](https://www.python.org/).
- [The pip package management tool](https://www.anaconda.com/docs/getting-started/working-with-conda/packages/pip-install).

To verify that Conda, Python and pip are installed, open a terminal and run:

```bash
conda --version
python --version
pip --version
```

If all commands return a version number, the installation is successful.

If an error occurs, download and install Miniconda by following the [official documentation](https://www.anaconda.com/docs/getting-started/miniconda/install/overview).

### Development tools

The application is primarily developed using Visual Studio Code, as Qt provides useful integration tools to speed up development and simplify debugging.

Therefore, [Visual Studio Code](https://code.visualstudio.com/) is recommended, along with the following extensions:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) (see [the doc](https://github.com/Microsoft/vscode-python)).
- [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy) (see [the doc](https://github.com/microsoft/vscode-python-debugger)).
- [Python Environments](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs) (see [the doc](https://github.com/microsoft/vscode-python-environments)).
- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) (see [the doc](https://github.com/microsoft/pylance-release)).
- [Qt Python Extension Pack](https://marketplace.visualstudio.com/items?itemName=TheQtCompany.qt-python-pack) (see [the doc](https://doc.qt.io/qtforpython-6/tools/vscode-ext.html)).
- [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) (see [the doc](https://docs.astral.sh/ruff/)).

### Setup the environment

1. Get the project using one of these methods:

    - [Download the repository as a ZIP archive](https://github.com/mnchapel/packy/archive/refs/heads/main.zip) , then extract its contents to any folder.
    - Clone the repository with Git:

      ```bash
      git clone https://github.com/mnchapel/cooking.git
      ```

2. Open a terminal in the folder containing the downloaded project, then create and activate a virtual environment with Conda:

    ```bash
    conda create -n <ENV_NAME> python=<PYTHON_VERSION>
    conda activate <ENV_NAME>
    ```

    Replace the following:

    - `<ENV_NAME>` : A meaningful environment name.
    - `<PYTHON_VERSION>` : The installed python version number (PackY use 3.14.3).

3. Install the dependencies using one of the following methods:

    - To install them *all at once*:

      ```bash
      pip install -r requirements.txt
      ```

    - To install them *one by one*:

      ```bash
      pip install pyside6
      pip install pyyaml
      pip install jsonschema
      pip install pytest
      ```

4. Regenerate the Qt Python stub files using the `pyside6-genpyi` tool to enable the `snake_case` features and properties in the Qt API:

    ```bash
    pyside6-genpyi all --feature snake_case true_property
    ```

    For more information about the feature, see:

    - [Motivation behind the feature](https://doc.qt.io/qtforpython-6/developer/feature-motivation.html).
    - [pyside6-genpyi command documentation](https://doc.qt.io/qtforpython-6/tools/pyside-genpyi.html).

5. Verify that the installation was successful by running PackY:

    ```bash
    python "packy/main.py"
    ```

    The PackY development environment is now ready.

### Building

Building the application involves compiling resources, UI files, and QML files into a format that PySide can interpret, using the `build` subcommand of the [`pyside6-project` tool](https://doc.qt.io/qtforpython-6/tools/pyside-project.html). This Qt subcommand implicitly calls the [pyside6-uic](https://doc.qt.io/qtforpython-6/tools/pyside-uic.html) and [pyside6-rcc](https://doc.qt.io/qtforpython-6/tools/pyside-rcc.html) commands. To determine which files to compile, the `build` subcommand scans the list of files defined in the `tool.pyside6-project.files` table of the `pyproject.toml` file. This list must therefore always be kept up to date, but by default this process is manual. For this reason, the project provides the `update_pyproject_file.py` script, which scans the source files and updates the table accordingly. This script must be executed before running the `build` subcommand.

Thus, to **build PackY**, open a terminal in the project's Conda virtual environment, then run the following commands:

```bash
python "scripts/update_pyproject_file.py" --relative-to "." --include-directory "packy"
pyside6-project build "pyproject.toml"
```

In VS Code, the `PackY: Build` task can also be used to run these commands. The update script can also be executed independently using the `PackY: Update PyProject file` task.

To compile only the UI files, run the command `python "scripts/convert_ui_to_py.py"`, or, from VS Code, use the `PackY: Compile .ui` task. More information about these commands can be found in the [Useful commands](#useful-commands) section.

### Testing

### Deployment

Before deploying the application, it is important to ensure that all tests pass in order to meet the required minimum quality standards.

**Prerequisites**:

- [pipreqs](https://pypi.org/project/pipreqs/)
- [PyInstaller](https://pypi.org/project/pyinstaller/)
- [Inno Setup](https://jrsoftware.org/isinfo.php)

If the **prerequisites are not met**, [install Inno Setup](https://jrsoftware.org/isdl.php), then install the `pipreqs` and `PyInstaller` packages using the following commands:

```bash
pip install pipreqs
pip install pyinstaller
```

The deployment of PackY takes place in **two successive phases**:

- The generation of the [requirements file](https://pip.pypa.io/en/stable/reference/requirements-file-format/) `requirements.txt`, only if a new package has been added, since the pre-filled file already includes all dependencies.
- The creation of the installer.

To **deploy PackY**, follow these steps:

1. Optionally: Only if a new package has been added, generate a new requirements file using the following steps:

    1. Generate a preview of the dependencies that will be written to the file using the `pipreqs --print` command, then verify its contents.

    2. Export the requirements file using the `pipreqs --savepath requirements.txt` command, then verify its contents again.

2. Create an executable with PyInstaller: [**OUTDATED: will be replaced by PySide deploy**]

    1. Update the version in the `resources/yaml/metadata.yml` file.

    2. Create a version file and run PyInstaller with the following commands:

        ```bash
        create-version-file resources/yaml/metadata.yml --outfile packy_version.txt
        pyinstaller packy.spec
        ```

3. Create an installer with Inno Setup:

    1. Open the project in the `setup/inno_setup/` folder.

    2. Modify the value of the `MyAppVersion` variable.

    3. Modify the value of the `OutputBaseFilename` variable.

    4. Build the installer.

### Useful commands

Several *commands* and *scripts* are available for the development of this project, including building, documentation generation, test execution, and deployment. The scripts are stored in the `scripts/` folder, and the commands can be run from a command prompt.

For VS Code users, all commands have been defined as **Visual Studio Code [tasks](https://code.visualstudio.com/docs/debugtest/tasks)** in `.vscode/tasks.json` and can be launched from the [command palette](https://code.visualstudio.com/docs/editor/tasks).

The usage of commands and scripts is described below in the order of a typical development lifecycle. They must be executed from the root project directory:

- To **clean** build artifacts (remove compiled files in `packy/ui/` and the contents of the `build/` and `docs/` directories):

  ```bash
  pyside6-project clean "pyproject.toml"
  ```

  - VS Code task: `PackY: Clean`.
  - [pyside6-project command documentation](https://doc.qt.io/qtforpython-6/tools/pyside-project.html).

- To **build** the project (compile resources, UI files, and QML files if existing and necessary):

  ```bash
  pyside6-project build "pyproject.toml"
  ```

  - VS Code task: `PackY: Build`.
  - **Note:** this Qt command implicitly calls the `pyside6-uic` and `pyside6-rcc` commands.
  - [pyside6-project command documentation](https://doc.qt.io/qtforpython-6/tools/pyside-project.html).
  - [pyside6-uic command documentation](https://doc.qt.io/qtforpython-6/tools/pyside-uic.html) and [its options](https://doc.qt.io/qt-6/uic.html).
  - [pyside6-rcc command documentation](https://doc.qt.io/qtforpython-6/tools/pyside-rcc.html) and [its options](https://doc.qt.io/qt-6/rcc.html).

- To **update PyProject file** (automatically called by the build command):

  ```bash
  python "scripts/update_pyproject_file.py" --relative-to "." --include-directory "packy"
  ```

  - VS Code task: `PackY: Update PyProject file`.

- To manually **compile .ui** files:

  ```bash
  python "scripts/convert_ui_to_py.py"
  ```

  - VS Code task: `PackY: Compile .ui`.

- To **run** the PackY application (execute the main file):

  ```bash
  python "packy/main.py"
  ```

  - VS Code task: `PackY: Run`.

- To **run the tests`** (execute the pytest command):

  ```bash
  pytest -v
  ```

  - VS Code task: `PackY: Test`.

- To **generate the documentation**:

  ```bash
  ```

  - VS Code task: `PackY: Doc`.

- To **deploy the application** in production (produce the final executable):

  ```bash
  # The application must be rebuilt before deployment
  pyside6-project build "pyproject.toml"
  pyside6-deploy "packy/main.py" --config-file "build/pysidedeploy.spec" --verbose --dry-run --keep-deployment-files --name "PackY"
  ```

  - VS Code task: `PackY: Deploy`.
  - [pyside6-deploy command documentation](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html).

- Some additional useful commands for development:

  ```bash
  # Generate Qt Python stub files for pythonic UI. More options on <https://doc.qt.io/qtforpython-6/tools/pyside-genpyi.html>
  pyside6-genpyi all --feature snake_case true_property

  # Generate the requirements file
  pipreqs --savepath requirements.txt
  ```

### Project structure

```text
project-root/
├── .vscode/                       # IDE workspace configuration
│   └── tasks.json                 # Custom build and automation tasks for VS Code
├── build/                         # Generated files used during build and deployment processes
├── docs/                          # Project documentation (Markdown files)
├── i18n/                          # Internationalization files (translations, locale resources)
├── logs/                          # Application runtime logs and debugging output
├── packy/                         # Main application source code
│   ├── models/                    # Qt models used by the application
│   ├── ui/                        # Qt Designer .ui files (interface definitions)
│   ├── utils/                     # Shared utilities, helpers, and common functions
│   ├── views/                     # UI components and view logic
│   └── main.js                    # Application entry point and initialization logic
├── resources/                     # Static resources used by the application
│   ├── img/                       # Images, icons, and graphical assets
│   ├── json/                      # JSON configuration and schema files
│   └── yaml/                      # YAML configuration and metadata files
├── scripts/                       # Utility scripts for development, build, and automation tasks
├── tests/                         # Unit and integration tests
├── tmp/                           # Temporary files generated during development or runtime
├── CHANGELOG.md                   # Project changelog (version history and notable changes)
├── CODE_OF_CONDUCT.md             # Contribution guidelines and community standards
├── LICENSE.md                     # Project license information
├── packy.spec                     # PyInstaller configuration file for building the executable
├── pyproject.toml                 # Project configuration (build system, dependencies, tools)
├── pytest.ini                     # Pytest configuration file
├── README.md                      # Project overview and main documentation
├── requirements.txt               # List of Python dependencies required to run the project
├── ruff.toml                      # Linting and code formatting configuration (Ruff)
└── setup.py                       # Setup script for packaging and distributing the project
```

### Code conventions

The PackY codebase must follow the [PEP 8 style guides](https://peps.python.org/pep-0008/), the naming convention already in place, and the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings. Linting is performed using [Ruff](https://docs.astral.sh/ruff/) with the `ruff.toml` file located at the root of the project. Ruff is also used to format the source code.

When using VS Code, the [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) is strongly recommended to display issues and format the code using the `Ruff: Format document` and `Ruff: Format imports` commands. Similarly, the [Pylance extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) is strongly recommended for static type checking.

Coding style:

- [PEP 8 style guide](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings

Code formatting:

- [Ruff](https://docs.astral.sh/ruff/)

Code linting:

- [Ruff](https://docs.astral.sh/ruff/)
- [Pylance](https://github.com/microsoft/pylance-release)

### Commit message guidelines

Git commit messages should follow the [Conventional Commits specification](https://www.conventionalcommits.org/) to maintain a clear and informative project history:

- `feat`: New features.
- `fix`: Bug fixes.
- `docs`: Documentation updates.
- `style`: Code style changes.
- `refactor`: Code refactoring without changing functionality.
- `test`: Adding or modifying tests.
- `chore`: Maintenance tasks.
- `merge`: Merging branches or pull requests. Examples:
  - `merge: feature-branch-xxx into feature-branch`
  - `merge: remote feature-branch into local feature-branch`
  - `merge: pull request #12 from feature-branch`

## 📚 Resources

General links:

- [PEP 8 style guides](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits style](https://www.conventionalcommits.org/)

Qt documentation:

- [Qt for Python](https://doc.qt.io/qtforpython-6/index.html)
- [Qt Extension for VS Code](https://doc-snapshots.qt.io/vscodeext-dev/index.html)
- [Qt Python VSCode Extension](https://doc.qt.io/qtforpython-6/tools/vscode-ext.html)
- [PySide6 Tools](https://doc.qt.io/qtforpython-6/tools/index.html)
- [PySide Tutorials](https://doc.qt.io/qtforpython-6/tutorials/index.html)
- [Inno Setup](https://jrsoftware.org/ishelp.php)

Other tools documentation:

- [Python JSON Schema](https://github.com/python-jsonschema/jsonschema)
- [JSON Schema](https://json-schema.org/)
- [PyYAML](https://pyyaml.org/)
- [pytest](https://docs.pytest.org/en/stable/index.html)
- [pipreqs](https://github.com/bndr/pipreqs)
- [PyInstaller](https://pyinstaller.org/en/stable/)
- [Ruff](https://docs.astral.sh/ruff/)
- [Python VSCode extension](https://github.com/Microsoft/vscode-python)
- [Python Debugger VSCode extension](https://github.com/microsoft/vscode-python-debugger)
- [Python Environments VSCode extension](https://github.com/microsoft/vscode-python-environments)
- [Pylance VSCode extension](https://github.com/microsoft/pylance-release)

## 🤝 Contributing

Whether you have ideas to share, bugs to report, or features to implement, your contributions are welcome. There are several ways you can help, and any contributions, no matter how small, is greatly appreciated. You will be properly credited in the README - a big thank you to everyone who has contributed so far.

### Code of conduct

Help us keep PackY open and inclusive. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Add translations

Not available yet.

### Submit a PR

Contributing to the codebase or documentation is highly valuable. You can fix bugs, add new features, or improve existing ones:

1. Fork the repository and create a branch from `main`.

2. Implement your changes following the project's coding standards.

3. [Open a pull request](https://github.com/mnchapel/packy/pulls) targeting the `main` branch.

### Report issue

PackY is currently in an alpha version, which means you may encounter bugs during use. If so, you can report the issue by [opening a new issue](https://github.com/mnchapel/packy/issues/new) on this GitHub repository. Please check first that the issue has not already been reported. Include as much detail as possible, such as reproduction steps, screenshots, or logs.

### Join the discussion

Not available yet.

### Star, upvote or leave a review

If you can spare a few seconds to star the project or leave a review, it will help new users discover PackY.

### Code style and commit messages

To ensure consistency throughout the codebase, please follow these guidelines:

- All features and bug fixes must be covered by one or more tests (unit tests).
- The code must follow the [code conventions](#code-conventions).
- Commit messages must follow the [commit message guidelines](#commit-message-guidelines).

## 🗺️ Roadmap

The following features are planned:

- [ ] Add a preview window when clicking on Run.
- [ ] Add an option to check archive integrity.
- [ ] Add an option to pack only modified files since the last snapshot.
- [ ] Add icons to buttons.
- [ ] Add a way to run PackY from the command line.
- [ ] Internationalization.

This application is intended to remain simple, so there are no plans to add many more features.

## ❤️ Credits

### Stack

PackY is built with PySide6, JSON Schema and Ruff. We thank the contributors of all these projects for their awesome work!

### Contributors

This project is maintained and developed by [Marie-Neige Chapel](https://github.com/mnchapel) and [Joseph Garnier](https://www.joseph-garnier.fr/).

## ©️ License

This work is licensed under the terms of the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">GNU GPLv3</a>.  See the [LICENSE.md](LICENSE.md) file for details.
