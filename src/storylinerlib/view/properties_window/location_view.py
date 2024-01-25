"""Provide a class for viewing and editing location properties.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from storylinerlib.view.properties_window.world_element_view import WorldElementView


class LocationView(WorldElementView):
    """Class for viewing and editing location properties."""

    def set_data(self, elementId):
        """Update the view with element's data.
        
        Extends the superclass constructor.
        """
        self._element = self._mdl.novel.locations[elementId]
        super().set_data(elementId)
