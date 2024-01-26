"""Provide a class for storyliner turning point representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement


class TurningPoint(BasicElement):
    """Turning point representation."""

    def __init__(self,
            position=None,
            notes=None,
            books=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)

        self._position = position
        # int: position on the arc's timeline

        self._notes = notes

        self._books = books
        # list of associated book IDs

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, newVal):
        if self._position != newVal:
            self._position = newVal
            self.on_element_change()

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, newVal):
        if self._notes != newVal:
            self._notes = newVal
            self.on_element_change()

    @property
    def books(self):
        try:
            return self._books[:]
        except TypeError:
            return None

    @books.setter
    def books(self, newVal):
        if self._books != newVal:
            self._books = newVal
            self.on_element_change()
