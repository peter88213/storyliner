"""Provide a class for viewing and editing turning points.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk

from storylinerlib.view.properties_window.basic_view import BasicView
from storylinerlib.widgets.collection_box import CollectionBox
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import _
import tkinter as tk


class TurningPointView(BasicView):
    """Class for viewing and editing turning points.

    Adds to the right pane:
    - A label showing book associated with the turnong point. 
    - A button bar for managing the book assignments.
    """
    _HEIGHT_LIMIT = 10

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

        self._lastSelected = ''
        self._treeSelectBinding = None
        self._uiEscBinding = None

        ttk.Separator(self._elementInfoWindow, orient='horizontal').pack(fill='x')

        # 'Books' listbox.
        self._bkTitles = ''
        self._bookLabel = ttk.Label(self._elementInfoWindow, text=_('Books'))
        self._bookLabel.pack(anchor='w')
        self._bookCollection = CollectionBox(
            self._elementInfoWindow,
            cmdAdd=self._pick_book,
            cmdRemove=self._remove_book,
            cmdOpen=self._go_to_book,
            cmdActivate=self._activate_book_buttons,
            lblOpen=_('Go to'),
            iconAdd=self._ui.icons.addIcon,
            iconRemove=self._ui.icons.removeIcon,
            iconOpen=self._ui.icons.gotoIcon
            )
        self._bookCollection.pack(fill='x')
        inputWidgets.extend(self._bookCollection.inputWidgets)

        for widget in inputWidgets:
            self._inputWidgets.append(widget)

    def set_data(self, elementId):
        """Update the widgets with element's data.
        
        Extends the superclass constructor.
        """
        self._element = self._mdl.story.turningPoints[elementId]
        super().set_data(elementId)

        # 'Books' window.
        self._bkTitles = self._get_element_titles(self._element.books, self._mdl.story.books)
        self._bookCollection.cList.set(self._bkTitles)
        listboxSize = len(self._bkTitles)
        if listboxSize > self._HEIGHT_LIMIT:
            listboxSize = self._HEIGHT_LIMIT
        self._bookCollection.cListbox.config(height=listboxSize)
        if not self._bookCollection.cListbox.curselection() or not self._bookCollection.cListbox.focus_get():
            self._bookCollection.deactivate_buttons()

    def _activate_book_buttons(self, event=None):
        if self._element.books:
            self._bookCollection.activate_buttons()
        else:
            self._bookCollection.deactivate_buttons()

    def _add_book(self, event=None):
        # Add the selected element to the collection, if applicable.
        bkList = self._element.books
        bkId = self._ui.tv.tree.selection()[0]
        if not bkId.startswith(BOOK_PREFIX):
            # Restore the previous section selection mode.
            self._end_picking_mode()
        elif not bkId in bkList:
            bkList.append(bkId)
            self._element.books = bkList

    def _create_frames(self):
        """Template method for creating the frames in the right pane."""
        self._create_index_card()
        self._create_element_info_window()
        self._create_notes_window()
        self._create_button_bar()

    def _get_element_titles(self, elemIds, elements):
        """Return a list of element titles.
        
        Positional arguments:
            elemIds -- list of element IDs.
            elements -- list of element objects.          
        """
        elemTitles = []
        if elemIds:
            for elemId in elemIds:
                try:
                    elemTitles.append(elements[elemId].title)
                except:
                    pass
        return elemTitles

    def _go_to_book(self, event=None):
        """Go to the book selected in the listbox."""
        try:
            selection = self._bookCollection.cListbox.curselection()[0]
        except:
            return

        self._ui.tv.go_to_node(self._element.books[selection])

    def _pick_book(self, event=None):
        """Enter the "add book" selection mode."""
        self._start_picking_mode()
        self._ui.tv.tree.bind('<<TreeviewSelect>>', self._add_book)
        self._ui.tv.tree.see(BK_ROOT)

    def _remove_book(self, event=None):
        """Remove the book selected in the listbox from the section books."""
        try:
            selection = self._bookCollection.cListbox.curselection()[0]
        except:
            return

        bkId = self._element.books[selection]
        title = self._mdl.novel.books[bkId].title
        if self._ui.ask_yes_no(f'{_("Remove book")}: "{title}"?'):
            bkList = self._element.books
            del bkList[selection]
            self._element.books = bkList

