"""Provide locale configuration and application translation discovery.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENSE.md file for more information.
"""

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import QCoreApplication, QDir, QLibraryInfo, QLocale, QTranslator


###############################################################################
class Localization:
    """Configure Qt localization and discover application languages.

    The localization service manages Qt and application translator objects and
    discovers language codes from application translation files.
    """

    # -------------------------------------------------------------------------
    def __init__(self, default_language_code: str = "en-US") -> None:
        """Initialize the localization service.

        Args:
            default_language_code (str): Initial language code recorded as the current
              application language.
        """
        self._current_lang: str = default_language_code
        self._app_translations_dir = ":/i18n"
        self._languages: list[str] = []
        self._qt_translator: QTranslator = QTranslator()
        self._app_translator: QTranslator = QTranslator()
        QtCore.qDebug(f"{self.__class__.__name__} initialized.")

    # -------------------------------------------------------------------------
    def install_translators(self, language_code: str) -> None:
        """Configure translation resources for the specified locale.

        The method returns without changes when ``language_code`` matches the
        currently recorded language. Otherwise, it sets the default Qt locale,
        removes the existing translators, and attempts to load the Qt and PackY
        translation catalogs.

        Args:
            language_code (str): ISO locale code identifying the target
              language, such as ``"en-US"`` or ``"fr-FR"``.
        """
        if self._current_lang == language_code:
            return

        QtCore.qDebug(f"Install translators for the {language_code} locale.")
        self._current_lang = language_code
        locale = QLocale(language_code)
        QLocale.setDefault(locale)

        QCoreApplication.removeTranslator(self._qt_translator)
        QCoreApplication.removeTranslator(self._app_translator)

        qt_trans_dir_path = QLibraryInfo.path(
            QLibraryInfo.LibraryPath.TranslationsPath,
        )
        if self._qt_translator.load(locale, "qtbase", "_", qt_trans_dir_path):
            if not QCoreApplication.installTranslator(self._qt_translator):
                QtCore.qWarning(
                    "Translations for qtbase cannot be installed.",
                )
        else:
            QtCore.qWarning(
                f"Translations for qtbase not loaded:\
                    {qt_trans_dir_path} not found",
            )

        app_trans_dir_path = self._app_translations_dir
        if self._app_translator.load(locale, "packy", "_", app_trans_dir_path):
            if not QCoreApplication.installTranslator(self._app_translator):
                QtCore.qWarning(
                    f"Translations for {language_code} cannot be installed.",
                )
        else:
            QtCore.qWarning(
                f"Translations for {language_code} not loaded:\
                      '{self._app_translations_dir}' not found.",
            )

    # -------------------------------------------------------------------------
    @property
    def current_language(self) -> str:
        """The current application language code, such as ``"en-US"`` or ``"fr-FR"``."""
        return self._current_lang

    # -------------------------------------------------------------------------
    @property
    def available_languages(self) -> list[str]:
        """The available application translation language codes.

        The codes are loaded lazily from regular files named ``packy_*.ts`` in the
        application translations directory. Each returned value is the filename
        suffix after ``packy_``.

        Language identifiers follow the ISO locale format ``<LANG_CODE>-<COUNTRY_CODE>``.
        The ``<LANG_CODE>`` part is a two-letter language code from the
        `ISO 639 <https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes>`__
        standard, and the ``<COUNTRY_CODE>`` part is a two-letter country code
        from the `ISO 3166-1 <https://en.wikipedia.org/wiki/ISO_3166-1>`__
        standard. For example: ``fr_FR``, ``en-US``, ``de-DE``, etc.
        """
        if not self._languages:
            self._load_available_languages()
        return self._languages

    # -------------------------------------------------------------------------
    def _load_available_languages(self) -> None:
        """Reload the cached language codes from application translation files.

        Only regular files whose names match ``packy_*.ts`` are included.
        """
        translations_dir = QDir(self._app_translations_dir)
        self._languages = [
            filename.removeprefix("packy_").removesuffix(".ts")
            for filename in translations_dir.entryList(
                ["packy_*.ts"],
                QDir.Filter.Files,
            )
        ]
