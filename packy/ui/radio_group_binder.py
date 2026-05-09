"""Qt widget binding utilities.

This module provides helper classes for binding Qt radio button groups to
Qt's model/view framework.

Copyright 2023-present, Marie-Neige Chapel and Joseph Garnier
All rights reserved.

See LICENCE.md file for more information.
"""

# Third-party
from PySide6 import QtCore
from PySide6.QtCore import Property, QCoreApplication, QEvent, QObject, Signal, Slot
from PySide6.QtWidgets import QAbstractButton, QButtonGroup, QWidget

# Standard library
from typing import final, override


###############################################################################
@final
class RadioGroupBinder(QWidget):
    """A QWidget wrapper exposing a QButtonGroup as a bindable property.

    This class enables integration between QButtonGroup instances and
    QDataWidgetMapper by exposing the currently selected button identifier
    as a Qt property.

    Signals:
        button_clicked (int): Emitted when a button is clicked.
        current_button_changed (int): Emitted when the selected button
            changes.
    """

    button_clicked = Signal(int)
    current_button_changed = Signal(int)

    # -------------------------------------------------------------------------
    def __init__(self, button_group: QButtonGroup, parent: QWidget | None = None) -> None:
        """Initialize the radio-group binder.

        Args:
            button_group (QButtonGroup): The button group to bind.
            parent (QWidget | None): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.__current_button_id: int = button_group.checkedId()  # -1 if no button is checked
        self.__group: QButtonGroup = button_group
        self.__group.buttonClicked.connect(self.__on_button_clicked)

        # QDataWidgetMappers only update the model when the mapped elements lose focus.
        # Here, we detect when the radio buttons lose focus and relay this information.
        for button in self.__group.buttons():
            button.installEventFilter(self)

    # -------------------------------------------------------------------------
    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Filters button focus events and forwards focus-out notifications.

        This ensures compatibility with QDataWidgetMapper auto-submit behavior,
        which updates the model only when widgets lose focus.

        Args:
            watched (QObject): The watched object.
            event (QEvent): The intercepted event.

        Returns:
            bool: True if the event was handled, otherwise False.
        """
        if event.type() == QtCore.QEvent.Type.FocusOut:
            QCoreApplication.sendEvent(self, event)
        return super().eventFilter(watched, event)

    # -------------------------------------------------------------------------
    @Slot(QAbstractButton, result=None)
    def __on_button_clicked(self, button: QAbstractButton) -> None:
        """Handles radio button click events.

        Updates the selected button state and emits the corresponding signals.

        Args:
            button (QAbstractButton): The clicked button.
        """
        self.button_clicked.emit(self.__group.id(button))
        self.set_checked(self.__group.id(button))

    # -------------------------------------------------------------------------
    @property
    def group(self) -> QButtonGroup:
        """The managed button group.

        Returns:
            QButtonGroup: The associated button group instance.
        """
        return self.__group

    # -------------------------------------------------------------------------
    def get_checked(self) -> int:
        """Returns the identifier of the currently checked button.

        Returns:
            int: The checked button identifier, or -1 if no button is selected.
        """
        return self.__group.checkedId()

    # -------------------------------------------------------------------------
    def set_checked(self, button_id: int) -> None:
        """Sets the checked button by identifier.

        Args:
            button_id (int): The identifier of the button to select.

        Raises:
            IndexError: No button exists for the given identifier.
        """
        button = self.__group.button(button_id)
        if not button:
            raise IndexError
        if button_id != self.__current_button_id:
            button.setChecked(True)
            self.__current_button_id = button_id
            self.current_button_changed.emit(button_id)

    selected_button = Property(
        int,
        fget=get_checked,
        fset=set_checked,
        notify=current_button_changed,
    )
