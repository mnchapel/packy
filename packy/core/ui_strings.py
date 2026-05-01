"""UI string definitions and translation helpers for Qt internationalization.

This module provides utility functions and constants to define translatable
UI strings using Qt's translation system. It centralizes all user-facing
text and ensures consistent context-based translation.

Typical usage example:

  text = UIStrings.tr(UIStrings.Menu.CLEAR)

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Third-party
from PySide6.QtCore import QT_TR_NOOP, QT_TRANSLATE_NOOP, QCoreApplication

# Standard library
from typing import Final, cast


###############################################################################
def PACKY_TR_NOOP(text: str) -> str:  # noqa: N802
    """Marks a string for translation without translating it immediately.

    Args:
        text (str): The source text to mark for translation.

    Returns:
        str: The marked text, usable with Qt translation tools.
    """
    return cast("str", QT_TR_NOOP(text))


###############################################################################
def PACKY_TRANSLATE_NOOP(context: str, text: str) -> str:  # noqa: N802
    """Marks a string with a specific context for deferred translation.

    Args:
        context (str): The translation context.
        text (str): The source text to mark for translation.

    Returns:
        str: The marked text associated with the given context.
    """
    return cast("str", QT_TRANSLATE_NOOP(context, text))


###############################################################################
class UIStrings:
    """Container for all translatable UI string constants.

    Provides grouped string definitions by UI context and a helper method
    to translate them at runtime.
    """

    class Menu:
        """Translatable strings related to application menus."""

        HELP: Final = PACKY_TRANSLATE_NOOP("Menu", "Help")
        CLEAR: Final = PACKY_TRANSLATE_NOOP("Menu", "Clear")

    class MessagesView:
        """Translatable strings for message display operations."""

        OP_SUCCESS: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Done: ")
        OP_ERROR: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Error: ")
        OP_INFO: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Info: ")
        OP_COPY: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Copy file {}")
        OP_MOVE: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Move file {}")
        OP_DELETE: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Delete file {}")
        OP_WIPE: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Wipe file {}")
        OP_LINK: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Create link {}")
        OP_SYM_LINK: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Create symlink {}")
        OP_MK_DIR: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Create directory {}")
        OP_RM_DIR: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Remove directory {}")
        OP_WIPE_DIR: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Wipe directory {}")
        OP_PACK: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Pack to file {}")
        OP_EXTRACT: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Extract file {}")
        OP_TEST: Final = PACKY_TRANSLATE_NOOP("MessagesView", "Test file integrity {}")

    @staticmethod
    def tr(txt_constant: str, *args: object) -> str:
        """Translates a UI string constant using its inferred context.

        The context is determined dynamically based on the class where the
        constant is defined.

        Args:
            txt_constant (str): The string constant to translate.
            *args (object): Optional arguments for string formatting.

        Returns:
            str: The translated and formatted string.
        """
        context = "UIStrings"
        for cls in UIStrings.__dict__.values():
            if isinstance(cls, type) and txt_constant in cls.__dict__.values():
                context = cls.__name__
                break
        translated = QCoreApplication.translate(context, txt_constant)
        return translated.format(*args) if args else translated
