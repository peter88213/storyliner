"""Provide a class for storyliner arc representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement


class Arc(BasicElement):
    """Arc representation."""

    def __init__(self,
            shortName=None,
            notes=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)

        self._shortName = shortName
        # str -- name of the arc

        self._notes = notes

    @property
    def shortName(self):
        return self._shortName

    @shortName.setter
    def shortName(self, newVal):
        if self._shortName != newVal:
            self._shortName = newVal
            self.on_element_change()

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, newVal):
        if self._notes != newVal:
            self._notes = newVal
            self.on_element_change()

