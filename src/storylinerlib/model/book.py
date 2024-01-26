"""Provide a class for a book representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from storylinerlib.model.basic_element import BasicElement


class Book(BasicElement):
    """Book representation for storyliner."""

    def __init__(self,
            nvPath=None,
            notes=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._nvPath = nvPath
        self._notes = notes

    @property
    def nvPath(self):
        return self._nvPath

    @nvPath.setter
    def nvPath(self, newVal):
        # str: path to the noveltree project, if any
        if self._nvPath != newVal:
            self._nvPath = newVal
            self.on_element_change()

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, newVal):
        if self._notes != newVal:
            self._notes = newVal
            self.on_element_change()

