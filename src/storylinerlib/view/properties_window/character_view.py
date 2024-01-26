"""Provide a class for viewing and editing character properties.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from datetime import date
from tkinter import ttk

from storylinerlib.storyliner_globals import prefs
from storylinerlib.view.properties_window.basic_view import BasicView
from storylinerlib.widgets.folding_frame import FoldingFrame
from storylinerlib.widgets.label_entry import LabelEntry
from storylinerlib.widgets.my_string_var import MyStringVar
from storylinerlib.widgets.text_box import TextBox
from storylinerlib.storyliner_globals import _


class CharacterView(BasicView):
    """Class for viewing and editing character properties.

    Adds to the right pane:
    - A "Full name" entry.
    - A "Role" folding frame.
    - A "Goals" folding frame.
    """
    _LBL_X = 15
    # Width of left-placed labels.

    def __init__(self, parent, model, view, controller):
        """Initialize the view once before element data is available.
        
        Positional arguments:
            view: NoveltreeUi -- Reference to the user interface.
            parent -- Parent widget to display this widget.

        - Initialize element-specific tk entry data.
        - Place element-specific widgets in the element's info window.
        
        Extends the superclass constructor.
        """
        super().__init__(parent, model, view, controller)
        inputWidgets = []

        #--- 'Full name' entry.
        self._fullNameFrame = ttk.Frame(self._elementInfoWindow)
        self._fullNameFrame.pack(anchor='w', fill='x')
        self._fullName = MyStringVar()
        self._fullNameEntry = LabelEntry(self._fullNameFrame, text=_('Full name'), textvariable=self._fullName, lblWidth=self._LBL_X)
        self._fullNameEntry.pack(anchor='w', pady=2)
        inputWidgets.append(self._fullNameEntry)
        self._fullNameEntry.entry.bind('<Return>', self.apply_changes)

        ttk.Separator(self._elementInfoWindow, orient='horizontal').pack(fill='x')

        #--- 'Role' text box.
        self._roleEntry = TextBox(self._elementInfoWindow,
            wrap='word',
            undo=True,
            autoseparators=True,
            maxundo=-1,
            height=10,
            width=10,
            padx=5,
            pady=5,
            bg=prefs['color_text_bg'],
            fg=prefs['color_text_fg'],
            insertbackground=prefs['color_text_fg'],
            )
        ttk.Label(self._elementInfoWindow, text=_('Role')).pack(anchor='w')
        self._roleEntry.pack(fill='x')
        inputWidgets.append(self._roleEntry)

        for widget in inputWidgets:
            widget.bind('<FocusOut>', self.apply_changes)
            self._inputWidgets.append(widget)

    def apply_changes(self, event=None):
        """Apply changes.
        
        Extends the superclass method.
        """
        super().apply_changes()

        # 'Full name' entry.
        self._element.fullName = self._fullName.get()

        # 'Role' frame.
        if self._roleEntry.hasChanged:
            self._element.role = self._roleEntry.get_text()

    def set_data(self, elementId):
        """Update the view with element's data.
        
        Extends the superclass constructor.
        """
        self._element = self._mdl.story.characters[elementId]
        super().set_data(elementId)

        # 'Full name' entry.
        self._fullName.set(self._element.fullName)

        #--- 'Role' text box.
        self._roleEntry.set_text(self._element.role)

    def _create_frames(self):
        """Template method for creating the frames in the right pane."""
        self._create_index_card()
        self._create_element_info_window()
        self._add_separator()
        self._create_notes_window()
        self._create_button_bar()

