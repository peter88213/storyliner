"""Provide a class for a story representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from novxlib.model.basic_element import BasicElement


class Story(BasicElement):
    """Novel representation."""

    def __init__(self,
            tree=None,
            **kwargs):
        """Extends the superclass constructor."""
        super().__init__(**kwargs)

        self.plotLines = {}
        # key = arc ID, value = Arc instance.
        self.plotPoints = {}
        # key = point ID, value = TurningPoint instance.
        self.books = {}
        # key = book ID, value = WorldElement instance.
        self.characters = {}
        # key = character ID, value = Character instance.
        self.tree = tree

