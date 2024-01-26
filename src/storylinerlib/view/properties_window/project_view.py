"""Provide a tkinter based class for viewing and editing project properties.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""

from storylinerlib.view.properties_window.basic_view import BasicView


class ProjectView(BasicView):
    """Class for viewing and editing project properties.
    
    """

    def __init__(self, parent, model, view, controller):
        """Initialize the view once before element date is available.
        
        Positional arguments:
            view: NoveltreeUi -- Reference to the user interface.
            parent -- Parent widget to display this widget.

        - Initialize element-specific tk entry data.
        - Place element-specific widgets in the element's info window.
        
        Extends the superclass constructor.
        """
        super().__init__(parent, model, view, controller)

    def set_data(self, elementId):
        """Update the view with element's data.
        
        Extends the superclass constructor.
        """
        self._element = self._mdl.story
        super().set_data(elementId)

    def _create_frames(self):
        """Template method for creating the frames in the right pane."""
        self._create_index_card()
