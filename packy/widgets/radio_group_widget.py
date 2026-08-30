"""Provide a Qt widget interface for an exclusive button group.

The widget exposes the checked button ID through a Qt property and emits
signals when a button is clicked or the selected button changes.
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
class RadioGroupWidget(QWidget):
    """Wrap a button group as a widget with an integer selection.

    The ``selected_button`` Qt property exposes the checked button ID. Focus-out
    events from the group's buttons are forwarded to this widget so mapped data
    can be committed when a button loses focus.

    Signals:
        button_clicked (int): Emitted when a button is clicked, with its group ID
          as ``button_id``.
        current_button_changed (int): Emitted after a different valid button is
          checked, with its group ID as ``button_id``.
    """

    button_clicked = Signal(int, arguments=["button_id"])
    current_button_changed = Signal(int, arguments=["button_id"])

    # -------------------------------------------------------------------------
    def __init__(self, button_group: QButtonGroup, parent: QWidget | None = None) -> None:
        """Initialize the widget for the specified button group.

        Args:
            button_group (QButtonGroup): Button group whose checked button is exposed
              and controlled by this widget.
            parent (QWidget | None): Parent widget, or ``None`` to create a top-level
              widget.
        """
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)

        self._current_button_id: int = button_group.checkedId()  # -1 if no button is checked
        self._button_group: QButtonGroup = button_group
        self._button_group.buttonClicked.connect(self._on_button_clicked)

        # QDataWidgetMappers can only update the model when the mapped elements lose focus.
        # Here, we detect when the radio buttons lose focus and relay this information.
        for button in self._button_group.buttons():
            button.installEventFilter(self)

    # -------------------------------------------------------------------------
    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Forward relevant button focus-out events to this widget.

        When a button loses focus while the group has a checked button, the same event
        is sent to this widget before normal event-filter processing continues.

        Args:
            watched (QObject): Object whose event is being filtered.
            event (QEvent): Event received by the watched object.

        Returns:
            bool: Result of the base widget's event filter.
        """
        if event.type() == QtCore.QEvent.Type.FocusOut:
            selected_button: QAbstractButton | None = self.get_checked_button()
            if selected_button is not None:
                QCoreApplication.sendEvent(self, event)
        return super().eventFilter(watched, event)

    # -------------------------------------------------------------------------
    @Slot(QAbstractButton, result=None)
    def _on_button_clicked(self, button: QAbstractButton) -> None:
        """Process a button click from the wrapped group.

        This slot emits :attr:`button_clicked` and updates the current selection.

        Args:
            button (QAbstractButton): Button that was clicked.
        """
        self.button_clicked.emit(self._button_group.id(button))
        self.check_button(self._button_group.id(button))

    # -------------------------------------------------------------------------
    @property
    def button_group(self) -> QButtonGroup:
        """The button group wrapped by this widget."""
        return self._button_group

    # -------------------------------------------------------------------------
    @override
    def setEnabled(self, enabled: bool) -> None:
        if super().isEnabled() == enabled:
            return

        for button in self._button_group.buttons():
            button.setEnabled(enabled)
        super().setEnabled(enabled)

    # -------------------------------------------------------------------------
    def get_checked_button(self) -> QAbstractButton | None:
        """Return the currently checked button.

        Returns:
            QAbstractButton | None: The checked button, or ``None`` when no button is
              checked.
        """
        button_id = self._button_group.checkedId()
        return self._button_group.button(button_id)

    # -------------------------------------------------------------------------
    def get_checked_button_id(self) -> int:
        """Return the ID of the currently checked button.

        Returns:
            int: The checked button ID, or ``-1`` when no button is checked.
        """
        return self._button_group.checkedId()

    # -------------------------------------------------------------------------
    def check_button(self, button_id: int) -> None:
        """Set the checked button by its group ID.

        A valid ID checks the corresponding button and emits
        :attr:`current_button_changed` when the ID differs from the current selection.
        An unknown ID clears every checked button without emitting the signal.

        Args:
            button_id (int): ID of the button to check, or an unknown ID to clear the
              selection.

        Raises:
            IndexError: No button exists for the given identifier.
        """
        if button_id != self._current_button_id:
            self._current_button_id = button_id
            selected_button: QAbstractButton | None = self._button_group.button(button_id)
            if selected_button is None:  # pyright: ignore[reportUnnecessaryComparison] A selected button really can be None
                for button in self._button_group.buttons():
                    button.setChecked(False)
            else:
                selected_button.setChecked(True)
                self.current_button_changed.emit(button_id)

    # -------------------------------------------------------------------------
    selected_button = Property(
        int,
        fget=get_checked_button_id,
        fset=check_button,
        notify=current_button_changed,  # Notify property is only used with QML
    )
