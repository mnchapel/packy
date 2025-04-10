<p align="center"><img src="https://github.com/mnchapel/packy/blob/main/resources/img/logo.png" width="160px"></p>

# PackY

PackY is a simple and intuitive software for creating batch file archives. A common use case is to archive the configuration files of installed software in separate containers but grouped together in a single folder. This project is currently under development and this page will be updated later with more information.

## Installation

### Windows

- Go to the [Releases page](https://github.com/mnchapel/packy/releases)
- Download the Windows installer named `PackYInstaller-x.x.x.x` in the assets of the latest release.
- Run the installer and follow the steps.

### Linux

Unfortunately, the software is currently only available for Windows but a Linux installer will soon be available, so stay tuned!

## Report issue

PackY is currently available in alpha version, which means you may encounter bugs during use. If this is the case, you can report the problem by creating a new issue on this github repository. Of course, you should first check that the problem has not already been reported by someone else.

## Roadmap

The following features will soon be available:

- Add a preview window when click on run.
- Add an option to check archive integrity.
- Add an option to pack only modified files since the last snapshot.
- Add icons on buttons.
- Add a way to run PackY in command line.
- Internationalization.

This software is intended to remain simple, so there are no plans to add many more features.

## Development

### Pre-requisites

1. Create a virtual environment with conda:

    ```console
    conda create -n <env_name> python=3.11
    ```

2. Activate the virtual environment:

    ```console
    conda activate <env_name>
    ```

3. Install the dependencies:

    - All in one with the requirements file:

      ```console
      pip install -r requirements.txt
      ```

    - Individually:

      ```console
      pip install PyQt6
      pip install pyyaml
      pip install typing_extensions
      pip install jsonschema
      ```

4. Run Packy:

    ```console
    python packy\main.py
    ```
