# Functional test case scenarios

This document describes the functional test scenarios implemented in the `tests/functional/` directory.

## Tests for the App lifecycle

### APP_STARTUP_001 - Startup when no previous session exists

Test Case ID: APP_STARTUP_001

Test Case Title: Startup when no previous session exists

Test Description: -

Module/Feature: -

Priority: -

Preconditions:

- The app must not be able to access any previous session: no user settings file exists on disk and no previous batch can be accessed.

Test Steps:

1. Launch the app.
‍
Test Data: -

Expected Results:

- The app metadata is initialized as follows:
  - `OrganizationName` = "PackY",
  - `OrganizationDomain` = "packy.com",
  - `ApplicationName` = "PackY",
  - `ApplicationDisplayName` = "PackY",
  - `ApplicationVersion` = `<AppConfig.VERSION>`.
- The current app language is the one defined by `<AppConfig.DEFAULT_LANGUAGE_CODE>`.
- No user settings file exists on disk.
- The batch workspace has no current batch, its history is empty, and an attempt to open a previous batch has been made once but failed.
- The main window has initiated the attempt to restore the last batch.
- The main window is visible, its title is "PackY", its file path is empty, and its status is "unmodified".
- The recent batches submenu is not enabled and is not visible. It contains, in order, a "Clear List" action, a separator, and as many *placeholder* actions as the maximum number of recent batches defined by `<AppConfig.MAX_RECENT_BATCHES>`.
- The "Save", "Save as", and "Close" menu buttons are disabled.
- All buttons in the main window interface are disabled.
- All button groups in the main window interface are disabled.
- The archive configuration panel components are connected to the panel's model.
- The archive configuration panel model has no current batch, and its properties are initialized with the same default values as those of a batch.
‍
Actual Results: -

Status: -

Notes: -

### APP_STARTUP_002 - Startup when previous batch is found

Test Case ID: APP_STARTUP_002

Test Case Title: Startup when previous batch is found

Test Description: -

Module/Feature: -

Priority: -

Preconditions:

- The app must be able to access the batch file of a previous session referenced by the `RecentBatches` settings key.

Test Steps:

1. Launch the app.
‍
Test Data:

- The batch file of the previous session.
- The user settings file with the `RecentBatches` key, which references the batch file from the previous session.

Expected Results:

- The app metadata is initialized as follows:
  - `OrganizationName` = "PackY",
  - `OrganizationDomain` = "packy.com",
  - `ApplicationName` = "PackY",
  - `ApplicationDisplayName` = "PackY",
  - `ApplicationVersion` = `<AppConfig.VERSION>`.
- The current app language is the one defined by `<AppConfig.DEFAULT_LANGUAGE_CODE>`.
- The app has loaded the user settings file.
- The batch workspace has successfully opened and activated the batch from the previous session, referenced it as the current batch, and added it to the history. A notification was sent to the user to inform them that the file was being uploaded.
- The batch from the previous session has been successfully loaded from disk and no error has been encountered.
- The main window has initiated the attempt to restore the last batch.
- The main window is visible, its title is `<current batch name> - PackY`, its file path is `<current batch file name>`, and its status is "unmodified".
- The recent batches submenu is enabled and is not visible. It contains, in order, a "Clear List" action, a separator, `<current batch name>`, and as many *placeholder* actions as the maximum number of recent batches defined by `<AppConfig.MAX_RECENT_BATCHES>`.
- The "Save", "Save as", and "Close" menu buttons are enabled.
- The main window interface "Create" button is enabled, and all other buttons are disabled.
- All button groups in the main window interface are disabled.
- The archive configuration panel components are connected to the panel's model.
- The archive configuration panel model has the same current batch as the batch workspace, and its properties are initialized with those of the current batch.
‍
Actual Results: -

Status: -

Notes: -

### APP_STARTUP_003 - Startup when previous batch is missing

Test Case ID: APP_STARTUP_003

Test Case Title: Startup when previous batch is missing

Test Description: -

Module/Feature: -

Priority: -

Preconditions:

- The `RecentBatches` settings key references a batch file from a previous session that does not or no longer exist on disk.

Test Steps:

1. Launch the app.
‍
Test Data:

- The user settings file with the `RecentBatches` key referencing a batch file that does not exist on disk.

Expected Results:

- The app metadata is initialized as follows:
  - `OrganizationName` = "PackY",
  - `OrganizationDomain` = "packy.com",
  - `ApplicationName` = "PackY",
  - `ApplicationDisplayName` = "PackY",
  - `ApplicationVersion` = `<AppConfig.VERSION>`.
- The current app language is the one defined by `<AppConfig.DEFAULT_LANGUAGE_CODE>`.
- The app has loaded the user settings file.
- The batch workspace has no current batch, its history contains the batch from the previous session, and an attempt to open the previous batch was made once but failed. A warning was issued to the user to inform them of the situation.
- The batch from the previous session could not be loaded from disk because the file could not be found.
- The main window has initiated the attempt to restore the last batch.
- The main window is visible, its title is "PackY", its file path is empty, and its status is "unmodified".
- The recent batches submenu is enabled and not visible. It contains, in order, a "Clear List" action, a separator, `<previous session batch name>`, and as many *placeholder* actions as the maximum number of recent batches defined by `<AppConfig.MAX_RECENT_BATCHES>`.
- The "Save", "Save as", and "Close" menu buttons are disabled.
- All buttons in the main window interface are disabled.
- All button groups in the main window interface are disabled.
- The archive configuration panel components are connected to those of its model.
- The archive configuration panel model has no current batch and its fields are initialized with the same values as the defaults of a batch.
‍
Actual Results: -

Status: -

Notes: -

## Test for Batch usages

### NEW_BATCH_001 - New batch when workspace is empty

Test Case ID: NEW_BATCH_001

Test Case Title: New batch when workspace is empty

Test Description: -

Module/Feature: -

Priority: -

Preconditions:

- The app must not be able to access any previous session: no user settings file exists on disk and no previous batch can be accessed.

Test Steps:

1. Launch the app and ensure that the workspace is empty.
2. Click on **New Batch**.
3. Select a folder or leave the default one, then click on **Save**.

Test Data: -

Expected Results:

- The app metadata is initialized as follows:
  - `OrganizationName` = "PackY",
  - `OrganizationDomain` = "packy.com",
  - `ApplicationName` = "PackY",
  - `ApplicationDisplayName` = "PackY",
  - `ApplicationVersion` = `<AppConfig.VERSION>`.
- The current app language is the one defined by `<AppConfig.DEFAULT_LANGUAGE_CODE>`.
- No user settings file exists on disk.
- The batch workspace created the new batch on disk, then, after the user accepted opening it, successfully activated it, set it as the current batch, and added it to the history. No information was provided to the user to inform them that it was opened.
- The batch workspace attempted once to open a previous batch but failed.
- The new batch was successfully saved to disk and no error was encountered.
- The main window has initiated the attempt to restore the last batch.
- The main window is visible, its title is `<current batch name> - PackY`, its file path is `<current batch file name>`, and its status is "unmodified".
- The recent batches submenu is enabled and is not visible. It contains, in order, a "Clear List" action, a separator, `<current batch name>`, and as many *placeholder* actions as the maximum number of recent batches defined by `<AppConfig.MAX_RECENT_BATCHES>`.
- The "Save", "Save as", and "Close" menu buttons are enabled.
- The main window interface "Create" button is enabled, and all other buttons are disabled.
- All button groups in the main window interface are disabled.
- The archive configuration panel components are connected to the panel's model.
- The archive configuration panel model has the same current batch as the batch workspace, and its properties are initialized with those of the current batch.

Actual Results: -

Status: -

Notes: -
