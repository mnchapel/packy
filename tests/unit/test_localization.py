"""Unit tests for :class:`Localization`.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Local application
import packy.core.localization as localization_module
from packy.core.localization import Localization

# Third-party
import pytest

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Third-party
    from pytest_mock import MockerFixture

    # Standard library
    from unittest.mock import MagicMock, Mock


###############################################################################
### Test Doubles
###############################################################################
# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class QtLocalizationMocks:
    """Expose patched Qt boundaries used by Localization."""

    locale_cls: Mock
    remove_translator: Mock
    install_translator: Mock
    library_path: Mock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class TranslatorInstallationContext:
    """Expose dependencies used to test translator installation behavior."""

    localization: Localization
    qt: QtLocalizationMocks
    qt_translator: Mock
    app_translator: Mock
    translator_cls: Mock
    locale: Mock


# -----------------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class AvailableLanguagesContext:
    """Expose dependencies used to test language discovery behavior."""

    localization: Localization
    directory_cls: Mock
    directory: Mock


###############################################################################
### Fixtures
###############################################################################
# -----------------------------------------------------------------------------
@pytest.fixture
def qt_localization_mocks(
    mocker: MockerFixture,
) -> QtLocalizationMocks:
    """Patch process-global Qt localization boundaries shared across tests."""
    # Setup
    locale_cls_mock: MagicMock = mocker.patch.object(
        localization_module,
        "QLocale",
        autospec=True,
        spec_set=True,
    )
    remove_translator_mock: MagicMock = mocker.patch.object(
        localization_module.QCoreApplication,
        "removeTranslator",
        autospec=True,
    )
    install_translator_mock: MagicMock = mocker.patch.object(
        localization_module.QCoreApplication,
        "installTranslator",
        autospec=True,
    )
    library_path_mock: MagicMock = mocker.patch.object(
        localization_module.QLibraryInfo,
        "path",
        autospec=True,
    )

    return QtLocalizationMocks(
        locale_cls=locale_cls_mock,
        remove_translator=remove_translator_mock,
        install_translator=install_translator_mock,
        library_path=library_path_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def translator_installation_context(
    mocker: MockerFixture,
    qt_localization_mocks: QtLocalizationMocks,
) -> TranslatorInstallationContext:
    """Provide a localization service with isolated translation dependencies."""
    # Setup
    qt_translator_mock: MagicMock = mocker.Mock(name="qt_translator")
    app_translator_mock: MagicMock = mocker.Mock(name="app_translator")

    translator_cls_mock: MagicMock = mocker.patch.object(
        localization_module,
        "QTranslator",
        autospec=True,
        spec_set=True,
    )
    translator_cls_mock.side_effect = [
        qt_translator_mock,
        app_translator_mock,
    ]

    locale_mock = mocker.Mock(name="locale")
    qt_localization_mocks.locale_cls.return_value = locale_mock
    qt_localization_mocks.library_path.return_value = "/qt/translations"

    # Construct after patching QTranslator so the service owns the test doubles.
    localization = Localization()  # Must be created after mocks

    return TranslatorInstallationContext(
        localization=localization,
        qt=qt_localization_mocks,
        qt_translator=qt_translator_mock,
        app_translator=app_translator_mock,
        translator_cls=translator_cls_mock,
        locale=locale_mock,
    )


# -----------------------------------------------------------------------------
@pytest.fixture
def available_languages_context(
    mocker: MockerFixture,
) -> AvailableLanguagesContext:
    """Provide a localization service with isolated language discovery."""
    # Setup
    directory_cls_mock: MagicMock = mocker.patch.object(
        localization_module,
        "QDir",
        autospec=True,
        spec_set=True,
    )
    directory_mock = directory_cls_mock.return_value

    localization = Localization()  # Must be created after mocks

    return AvailableLanguagesContext(
        localization=localization,
        directory_cls=directory_cls_mock,
        directory=directory_mock,
    )


###############################################################################
### Tests
###############################################################################
###############################################################################
class TestLocalizationInstallTranslators:
    """Cover public language-change and translator-installation behavior."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    @pytest.mark.parametrize(
        "default_language_code",
        ["en-US", "fr-FR"],
        ids=["default-code", "custom-code"],
    )
    def test_matching_current_language_does_not_reconfigure_translators(
        self,
        default_language_code: str,
        qt_localization_mocks: QtLocalizationMocks,
    ) -> None:
        """A request for the current language performs no localization work."""
        # Arrange
        mocks = qt_localization_mocks
        localization = Localization(default_language_code)

        # Act
        localization.install_translators(default_language_code)

        # Assert
        assert localization.current_language == default_language_code
        mocks.locale_cls.assert_not_called()
        mocks.remove_translator.assert_not_called()
        mocks.install_translator.assert_not_called()
        mocks.library_path.assert_not_called()

    # -------------------------------------------------------------------------
    @pytest.mark.technique_decision_table
    @pytest.mark.parametrize(
        (
            "qtbase_loaded",
            "app_loaded",
            "expected_installed",
        ),
        [
            pytest.param(
                True,
                True,
                ("qt", "app"),
                id="both-load",
                marks=pytest.mark.scenario_happy_path,
            ),
            pytest.param(
                False,
                True,
                ("app",),
                id="qtbase-missing",
                marks=pytest.mark.scenario_failure_error_path,
            ),
            pytest.param(
                True,
                False,
                ("qt",),
                id="app-missing",
                marks=pytest.mark.scenario_failure_error_path,
            ),
            pytest.param(
                False,
                False,
                (),
                id="both-missing",
                marks=pytest.mark.scenario_failure_error_path,
            ),
        ],
    )
    def test_changed_language_installs_only_successfully_loaded_translators(
        self,
        translator_installation_context: TranslatorInstallationContext,
        qtbase_loaded: bool,  # noqa: FBT001
        app_loaded: bool,  # noqa: FBT001
        expected_installed: tuple[str, ...],
    ) -> None:
        """Install only translators whose translation catalogs load successfully."""
        # Arrange
        context = translator_installation_context
        context.qt_translator.load.return_value = qtbase_loaded
        context.app_translator.load.return_value = app_loaded

        # Act
        context.localization.install_translators("fr-FR")

        # Assert
        assert context.localization.current_language == "fr-FR"
        context.qt.locale_cls.assert_called_once_with("fr-FR")
        context.qt.locale_cls.setDefault.assert_called_once_with(context.locale)
        context.qt.library_path.assert_called_once_with(
            localization_module.QLibraryInfo.LibraryPath.TranslationsPath,
        )

        assert context.qt.remove_translator.call_count == 2
        context.qt.remove_translator.assert_any_call(context.qt_translator)
        context.qt.remove_translator.assert_any_call(context.app_translator)

        context.qt_translator.load.assert_called_once_with(
            context.locale,
            "qtbase",
            "_",
            "/qt/translations",
        )
        context.app_translator.load.assert_called_once_with(
            context.locale,
            "packy",
            "_",
            ":/i18n",
        )

        assert context.qt.install_translator.call_count == len(expected_installed)
        translator_by_name = {
            "qt": context.qt_translator,
            "app": context.app_translator,
        }
        for translator_name in expected_installed:
            context.qt.install_translator.assert_any_call(
                translator_by_name[translator_name],
            )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_repeated_language_after_successful_load_does_not_reconfigure_translators(
        self,
        translator_installation_context: TranslatorInstallationContext,
    ) -> None:
        """Requesting a successfully configured language again performs no reconfiguration."""
        # Arrange
        context = translator_installation_context
        context.qt_translator.load.return_value = True
        context.app_translator.load.return_value = True

        # Act
        context.localization.install_translators("fr-FR")
        context.localization.install_translators("fr-FR")

        # Assert
        assert context.localization.current_language == "fr-FR"
        context.qt.locale_cls.assert_called_once_with("fr-FR")
        context.qt.locale_cls.setDefault.assert_called_once_with(context.locale)
        context.qt.library_path.assert_called_once_with(
            localization_module.QLibraryInfo.LibraryPath.TranslationsPath,
        )
        assert context.qt.remove_translator.call_count == 2
        context.qt_translator.load.assert_called_once()
        context.app_translator.load.assert_called_once()
        assert context.qt.install_translator.call_count == 2

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_failure_error_path
    @pytest.mark.technique_state_transition
    def test_repeated_language_after_failed_load_does_not_retry_translation_loading(
        self,
        translator_installation_context: TranslatorInstallationContext,
    ) -> None:
        """Requesting the same language again does not retry failed catalog loads."""
        # Arrange
        context = translator_installation_context
        context.qt_translator.load.return_value = False
        context.app_translator.load.return_value = False

        # Act
        context.localization.install_translators("fr-FR")
        context.localization.install_translators("fr-FR")

        # Assert
        assert context.localization.current_language == "fr-FR"
        context.qt.locale_cls.assert_called_once_with("fr-FR")
        context.qt.locale_cls.setDefault.assert_called_once_with(context.locale)
        context.qt.library_path.assert_called_once_with(
            localization_module.QLibraryInfo.LibraryPath.TranslationsPath,
        )

        assert context.qt.remove_translator.call_count == 2
        context.qt.remove_translator.assert_any_call(context.qt_translator)
        context.qt.remove_translator.assert_any_call(context.app_translator)

        context.qt_translator.load.assert_called_once_with(
            context.locale,
            "qtbase",
            "_",
            "/qt/translations",
        )
        context.app_translator.load.assert_called_once_with(
            context.locale,
            "packy",
            "_",
            ":/i18n",
        )
        context.qt.install_translator.assert_not_called()


###############################################################################
class TestAvailableLanguages:
    """Cover public language discovery and lazy caching behavior."""

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_happy_path
    @pytest.mark.technique_equivalence_partitioning
    def test_available_languages_returns_codes_from_translation_filenames(
        self,
        available_languages_context: AvailableLanguagesContext,
    ) -> None:
        """Return language codes extracted from matching translation filenames."""
        # Arrange
        context = available_languages_context
        context.directory.entryList.return_value = [
            "packy_fr-FR.ts",
            "packy_en-US.ts",
        ]

        # Act
        languages = context.localization.available_languages

        # Assert
        assert set(languages) == {"fr-FR", "en-US"}
        assert len(languages) == 2
        context.directory_cls.assert_called_once_with(":/i18n")
        context.directory.entryList.assert_called_once_with(
            ["packy_*.ts"],
            context.directory_cls.Filter.Files,
        )

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_state_transition
    def test_available_languages_reuses_nonempty_discovery_result(
        self,
        available_languages_context: AvailableLanguagesContext,
    ) -> None:
        """Reuse a nonempty discovery result on subsequent accesses."""
        # Arrange
        context = available_languages_context
        context.directory.entryList.return_value = [
            "packy_fr-FR.ts",
        ]

        # Act
        first_result = context.localization.available_languages
        context.directory.entryList.return_value = [
            "packy_fr-FR.ts",
            "packy_en-US.ts",
        ]
        second_result = context.localization.available_languages

        # Assert
        assert first_result == ["fr-FR"]
        assert second_result == ["fr-FR"]
        context.directory.entryList.assert_called_once()

    # -------------------------------------------------------------------------
    @pytest.mark.scenario_alternate_path
    @pytest.mark.technique_equivalence_partitioning
    @pytest.mark.technique_state_transition
    def test_available_languages_retries_discovery_after_empty_result(
        self,
        available_languages_context: AvailableLanguagesContext,
    ) -> None:
        """Retry language discovery when the previous result was empty."""
        # Arrange
        context = available_languages_context
        context.directory.entryList.side_effect = [
            [],
            ["packy_de-DE.ts"],
        ]

        # Act
        first_result = context.localization.available_languages
        second_result = context.localization.available_languages

        # Assert
        assert first_result == []
        assert second_result == ["de-DE"]
        assert context.directory.entryList.call_count == 2
