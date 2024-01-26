"""Provide a class for viewing and editing book properties.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from storylinerlib.view.properties_window.basic_view import BasicView


class BookView(BasicView):
    """Class for viewing and editing book properties."""

    def set_data(self, elementId):
        """Update the view with element's data.
        
        Extends the superclass constructor.
        """
        self._element = self._mdl.story.books[elementId]
        super().set_data(elementId)

    def _create_frames(self):
        """Template method for creating the frames in the right pane."""
        self._create_index_card()
        self._create_element_info_window()
        self._create_notes_window()
        self._create_button_bar()
