"""Provide a class for storyliner character representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement


class Character(BasicElement):
    """storyliner character representation."""

    def __init__(self,
            fullName=None,
            role=None,
            notes=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)
        self._fullName = fullName
        self._role = role
        self._notes = notes

    @property
    def fullName(self):
        return self._fullName

    @fullName.setter
    def fullName(self, newVal):
        if self._fullName != newVal:
            self._fullName = newVal
            self.on_element_change()

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, newVal):
        if self._role != newVal:
            self._role = newVal
            self.on_element_change()

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, newVal):
        if self._notes != newVal:
            self._notes = newVal
            self.on_element_change()

