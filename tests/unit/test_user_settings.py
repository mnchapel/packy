"""Unit tests for :class:`UserSettings`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# pyright: reportPrivateUsage=false

# Local application
from packy.core.app import UserSettings

# Third-party
import pytest
from PySide6.QtCore import QByteArray, QObject, QSettings
from PySide6.QtWidgets import QApplication, QWidget

# Standard library
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture
    from pytestqt.qtbot import QtBot

    # Standard library
    from pathlib import Path


###############################################################################
### Helpers
###############################################################################
# -----------------------------------------------------------------------------
class Theme(StrEnum):
    """Provide representative enum-backed application setting values."""

    LIGHT = "light"
    DARK = "dark"


# -----------------------------------------------------------------------------
class RetryPolicy(IntEnum):
    """Provide representative enum-backed application setting values."""

    NEVER = 0
    ALWAYS = 1


###############################################################################
### Test Contexts
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class RestoreLayoutContext:
    """Expose saved source state and a target widget to restore."""

    user_settings: UserSettings
    persistent_config: QSettings
    saved_state_widget: QWidget
    widget_to_restore: QWidget


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def hidden_layout_widget(qtbot: QtBot) -> QWidget:
    """Provide a named hidden widget with deterministic geometry."""
    # Setup
    widget = QWidget()
    widget.setObjectName("Sidebar")
    widget.setGeometry(150, 150, 320, 240)
    widget.hide()
    qtbot.addWidget(widget)

    return widget


# -----------------------------------------------------------------------------
@pytest.fixture
def restore_layout_context(
    qtbot: QtBot,
) -> RestoreLayoutContext:
    """Provide saved widget state and a target with different initial state."""
    # Setup
    user_settings = UserSettings()
    persistent_config = user_settings._persistent_config

    saved_state_widget = QWidget()
    saved_state_widget.setGeometry(50, 50, 100, 100)
    saved_state_widget.setVisible(True)
    qtbot.addWidget(saved_state_widget)

    widget_to_restore = QWidget()
    widget_to_restore.setObjectName("Sidebar")
    widget_to_restore.setGeometry(150, 150, 320, 240)
    widget_to_restore.setVisible(False)
    qtbot.addWidget(widget_to_restore)

    return RestoreLayoutContext(
        user_settings=user_settings,
        persistent_config=persistent_config,
        saved_state_widget=saved_state_widget,
        widget_to_restore=widget_to_restore,
    )


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestUserSettingsConstruction:
    """Unit tests for :class:`UserSettings` construction."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_preserves_parent_and_sets_object_name(
        self,
        qapp: QApplication,
    ) -> None:
        """Construction preserves QObject ownership and exposes the class object name."""
        # Arrange
        parent = QObject(qapp)

        # Act
        settings = UserSettings(parent)

        # Assert
        assert settings.parent() is parent
        assert settings.objectName() == "UserSettings"


###############################################################################
class TestUserSettingsFilePath:
    """Unit tests for :meth:`UserSettings.file_path`."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_uses_isolated_user_settings_directory(
        self,
        tmp_path: Path,
    ) -> None:
        """The settings filename belongs to the per-test UserScope directory."""
        # Arrange
        user_settings = UserSettings()
        expected_root = (tmp_path / "settings_user").resolve()

        # Act
        result = user_settings.file_path

        # Assert
        assert result.is_absolute()
        assert result.is_relative_to(expected_root)


###############################################################################
class TestUserSettingsBeginGroup:
    """Unit tests for :meth:`UserSettings.begin_group`."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_reads_from_group_namespace(
        self,
    ) -> None:
        """Beginning a group changes subsequent reads to the group namespace."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Key", "root_value")
        persistent_config.beginGroup("Group")
        persistent_config.setValue("Key", "child_value")
        persistent_config.endGroup()

        # Act
        root_key_value = persistent_config.value("Key")
        user_settings.begin_group("Group")
        child_key_value = persistent_config.value("Key")

        # Assert
        assert root_key_value == "root_value"
        assert child_key_value == "child_value"

        # Cleanup
        persistent_config.endGroup()


###############################################################################
class TestUserSettingsEndGroup:
    """Unit tests for :meth:`UserSettings.end_group`."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    def test_returns_to_parent_namespace(
        self,
    ) -> None:
        """Ending a group restores subsequent reads to its parent namespace."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Key", "root_value")
        persistent_config.beginGroup("Group")
        persistent_config.setValue("Key", "child_value")

        # Act
        user_settings.end_group()

        # Assert
        assert persistent_config.value("Key") == "root_value"


###############################################################################
class TestUserSettingsSetValue:
    """Unit tests for :meth:`UserSettings.set_value`."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_changed_value_without_callback_is_stored(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A changed value is persisted and reports that a change occurred."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Key", "old_value")
        value_spy = mocker.spy(persistent_config, "value")
        set_value_spy = mocker.spy(persistent_config, "setValue")

        # Act
        changed = user_settings.set_value("Key", "new_value")

        # Assert
        assert changed is True
        value_spy.assert_called_once_with("Key")
        set_value_spy.assert_called_once_with("Key", "new_value")
        assert persistent_config.value("Key") == "new_value"

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_changed_value_is_stored_before_callback(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A change callback runs after the new setting has been persisted."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Key", "old_value")
        set_value_spy = mocker.spy(persistent_config, "setValue")

        def assert_value_is_stored(value: str) -> None:
            assert persistent_config.value("Key") == value

        callback_mock = mocker.Mock(
            name="on_changed",
            side_effect=assert_value_is_stored,
        )

        # Act
        changed = user_settings.set_value("Key", "new_value", callback_mock)

        # Assert
        assert changed is True
        set_value_spy.assert_called_once_with("Key", "new_value")
        callback_mock.assert_called_once_with("new_value")
        assert persistent_config.value("Key") == "new_value"

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_decision_table
    @pytest.mark.technique_branch
    def test_unchanged_value_returns_false_without_write_or_callback(
        self,
        mocker: MockerFixture,
    ) -> None:
        """An unchanged value performs no write and emits no change callback."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Key", "value")
        value_spy = mocker.spy(persistent_config, "value")
        set_value_spy = mocker.spy(persistent_config, "setValue")
        callback_mock = mocker.Mock(name="on_changed")

        # Act
        changed = user_settings.set_value("Key", "value", callback_mock)

        # Assert
        assert changed is False
        value_spy.assert_called_once_with("Key")
        set_value_spy.assert_not_called()
        callback_mock.assert_not_called()
        assert persistent_config.value("Key") == "value"


###############################################################################
class TestUserSettingsValue:
    """Unit tests for :meth:`UserSettings.value`."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    def test_returns_stored_value(
        self,
        mocker: MockerFixture,
    ) -> None:
        """An ordinary typed setting returns its value from isolated QSettings."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Count", 7)
        value_spy = mocker.spy(persistent_config, "value")

        # Act
        setting_value = user_settings.value("Count", 3)

        # Assert
        assert setting_value == 7
        value_spy.assert_called_once_with("Count", 3, int)

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_branch
    @pytest.mark.parametrize(
        ("stored_value", "expected"),
        [
            pytest.param(
                Theme.DARK.value,
                Theme.DARK,
                id="valid-enum-value",
            ),
            pytest.param(
                "sepia",
                Theme.LIGHT,
                id="invalid-raw-value",
            ),  # invalid raw value returns default
        ],
    )
    def test_enum_value_returns_expected_member(
        self,
        mocker: MockerFixture,
        stored_value: object,
        expected: Theme,
    ) -> None:
        """Enum reads convert stored values or fall back to the default member."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("Theme", stored_value)
        value_spy = mocker.spy(persistent_config, "value")

        # Act
        setting_value = user_settings.value("Theme", Theme.LIGHT)

        # Assert
        assert setting_value is expected
        value_spy.assert_called_once_with("Theme", Theme.LIGHT)

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    def test_missing_enum_value_returns_default_member(
        self,
        mocker: MockerFixture,
    ) -> None:
        """A missing enum setting returns its default enum member."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        value_spy = mocker.spy(persistent_config, "value")

        assert persistent_config.contains("Theme") is False

        # Act
        setting_value = user_settings.value("Theme", Theme.LIGHT)

        # Assert
        assert setting_value is Theme.LIGHT
        value_spy.assert_called_once_with("Theme", Theme.LIGHT.value)

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_enum_with_integer_values_returns_expected_member(
        self,
        mocker: MockerFixture,
    ) -> None:
        """Enums backed by integers are restored as enum members."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.setValue("RetryPolicy", RetryPolicy.ALWAYS.value)
        value_spy = mocker.spy(persistent_config, "value")

        # Act
        setting_value = user_settings.value(
            "RetryPolicy",
            RetryPolicy.NEVER,
        )

        # Assert
        assert setting_value is RetryPolicy.ALWAYS
        value_spy.assert_called_once_with("RetryPolicy", RetryPolicy.NEVER.value)


###############################################################################
class TestUserSettingsSaveLayout:
    """Unit tests for :meth:`UserSettings.save_layout_geometry_for`."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_without_active_group_saves_widget_state(
        self,
        hidden_layout_widget: QWidget,
        mocker: MockerFixture,
    ) -> None:
        """Saving outside a group persists the widget state under its name."""
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        begin_group_spy = mocker.spy(persistent_config, "beginGroup")
        set_value_spy = mocker.spy(persistent_config, "setValue")
        end_group_spy = mocker.spy(persistent_config, "endGroup")

        geometry = hidden_layout_widget.saveGeometry()

        # Act
        user_settings.save_layout_geometry_for(hidden_layout_widget)

        # Assert
        begin_group_spy.assert_called_once_with("Sidebar")
        end_group_spy.assert_called_once_with()

        assert set_value_spy.call_count == 2
        set_value_spy.assert_any_call("Visible", False)
        set_value_spy.assert_any_call("Geometry", geometry)

        assert persistent_config.value("Sidebar/Visible", type=bool) is False
        assert persistent_config.value("Sidebar/Geometry", type=QByteArray) == geometry

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_with_active_group_saves_state_without_changing_group(
        self,
        hidden_layout_widget: QWidget,
        mocker: MockerFixture,
    ) -> None:
        """Saving inside an active group stores state without changing that group."""
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        persistent_config.beginGroup("ActiveGroup")

        begin_group_spy = mocker.spy(persistent_config, "beginGroup")
        set_value_spy = mocker.spy(persistent_config, "setValue")
        end_group_spy = mocker.spy(persistent_config, "endGroup")

        geometry = hidden_layout_widget.saveGeometry()

        # Act
        user_settings.save_layout_geometry_for(hidden_layout_widget)

        # Assert
        begin_group_spy.assert_not_called()
        end_group_spy.assert_not_called()

        assert set_value_spy.call_count == 2
        set_value_spy.assert_any_call("Visible", False)
        set_value_spy.assert_any_call("Geometry", geometry)

        assert persistent_config.group() == "ActiveGroup"
        assert persistent_config.value("Visible", type=bool) is False
        assert persistent_config.value("Geometry", type=QByteArray) == geometry

        # Cleanup
        persistent_config.endGroup()


###############################################################################
class TestUserSettingsRestoreLayout:
    """Cover restoration of QWidget visibility and geometry."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_without_active_group_restores_widget_state(
        self,
        restore_layout_context: RestoreLayoutContext,
        mocker: MockerFixture,
    ) -> None:
        """Restoring without an active group reads state from a temporary widget group."""
        # Arrange
        user_settings = restore_layout_context.user_settings
        persistent_config = restore_layout_context.persistent_config
        saved_state_widget = restore_layout_context.saved_state_widget
        widget_to_restore = restore_layout_context.widget_to_restore

        persistent_config.beginGroup(widget_to_restore.objectName())
        persistent_config.setValue("Visible", saved_state_widget.isVisible())
        persistent_config.setValue("Geometry", saved_state_widget.saveGeometry())
        persistent_config.endGroup()

        begin_group_spy = mocker.spy(persistent_config, "beginGroup")
        value_spy = mocker.spy(persistent_config, "value")
        end_group_spy = mocker.spy(persistent_config, "endGroup")
        show_spy = mocker.spy(widget_to_restore, "show")

        assert persistent_config.group() == ""
        assert widget_to_restore.isVisible() != saved_state_widget.isVisible()
        assert widget_to_restore.geometry() != saved_state_widget.geometry()

        # Act
        user_settings.restore_layout_geometry_for(widget_to_restore)

        # Assert
        begin_group_spy.assert_called_once_with(widget_to_restore.objectName())
        end_group_spy.assert_called_once_with()

        assert value_spy.call_count == 2
        value_spy.assert_any_call("Visible", defaultValue=True, type=bool)
        value_spy.assert_any_call("Geometry", QByteArray(), type=QByteArray)
        show_spy.assert_called_once_with()

        assert widget_to_restore.isVisible() == saved_state_widget.isVisible()
        assert widget_to_restore.geometry() == saved_state_widget.geometry()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.technique_branch
    def test_with_active_group_restores_widget_state(
        self,
        restore_layout_context: RestoreLayoutContext,
        mocker: MockerFixture,
    ) -> None:
        """Restoring inside an active group reads state without changing that group."""
        # Arrange
        user_settings = restore_layout_context.user_settings
        persistent_config = restore_layout_context.persistent_config
        saved_state_widget = restore_layout_context.saved_state_widget
        widget_to_restore = restore_layout_context.widget_to_restore

        persistent_config.beginGroup("ActiveGroup")
        persistent_config.setValue("Visible", saved_state_widget.isVisible())
        persistent_config.setValue("Geometry", saved_state_widget.saveGeometry())

        begin_group_spy = mocker.spy(persistent_config, "beginGroup")
        value_spy = mocker.spy(persistent_config, "value")
        end_group_spy = mocker.spy(persistent_config, "endGroup")
        show_spy = mocker.spy(widget_to_restore, "show")

        assert widget_to_restore.isVisible() != saved_state_widget.isVisible()
        assert widget_to_restore.geometry() != saved_state_widget.geometry()

        # Act
        user_settings.restore_layout_geometry_for(widget_to_restore)

        # Assert
        begin_group_spy.assert_not_called()
        end_group_spy.assert_not_called()

        assert value_spy.call_count == 2
        value_spy.assert_any_call("Visible", defaultValue=True, type=bool)
        value_spy.assert_any_call("Geometry", QByteArray(), type=QByteArray)
        show_spy.assert_called_once_with()

        assert persistent_config.group() == "ActiveGroup"
        assert widget_to_restore.isVisible() == saved_state_widget.isVisible()
        assert widget_to_restore.geometry() == saved_state_widget.geometry()

        # Cleanup
        persistent_config.endGroup()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    def test_missing_settings_use_default_visibility_and_preserve_geometry(
        self,
        hidden_layout_widget: QWidget,
        mocker: MockerFixture,
    ) -> None:
        """Missing settings make the widget visible without changing its geometry."""
        # Arrange
        user_settings = UserSettings()
        persistent_config = user_settings._persistent_config

        initial_geometry = hidden_layout_widget.geometry()

        begin_group_spy = mocker.spy(persistent_config, "beginGroup")
        value_spy = mocker.spy(persistent_config, "value")
        end_group_spy = mocker.spy(persistent_config, "endGroup")
        show_spy = mocker.spy(hidden_layout_widget, "show")

        assert persistent_config.group() == ""

        # Act
        user_settings.restore_layout_geometry_for(hidden_layout_widget)

        # Assert
        begin_group_spy.assert_called_once_with(hidden_layout_widget.objectName())
        end_group_spy.assert_called_once_with()

        assert value_spy.call_count == 2
        value_spy.assert_any_call("Visible", defaultValue=True, type=bool)
        value_spy.assert_any_call("Geometry", QByteArray(), type=QByteArray)
        show_spy.assert_called_once_with()

        assert persistent_config.group() == ""
        assert hidden_layout_widget.isVisible() is True
        assert hidden_layout_widget.geometry() == initial_geometry
