"""Toolbar class for storyliner.


Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import _
import tkinter as tk


class Toolbar:
    """Toolbar plugin class."""

    def __init__(self, view, controller):
        """Add a toolbar.
        
        Positional arguments:
            view -- reference to the main view instance of the application.
            controller -- reference to the main controller instance of the application.
        """
        self._ctrl = controller
        self._ui = view

        # Add a toolbar to the editor window.
        self._buttonBar = tk.Frame(self._ui.mainWindow)

        # "Go back" button.
        self._goBackButton = ttk.Button(
            self._buttonBar,
            text=_('Back'),
            image=self._ui.icons.goBackIcon,
            command=self._ui.tv.go_back
            )
        self._goBackButton.pack(side='left')
        self._goBackButton.image = self._ui.icons.goBackIcon

        # "Go forward" button.
        self._goForwardButton = ttk.Button(
            self._buttonBar,
            text=_('Forward'),
            image=self._ui.icons.goForwardIcon,
            command=self._ui.tv.go_forward
            )
        self._goForwardButton.pack(side='left')
        self._goForwardButton.image = self._ui.icons.goForwardIcon

        # Separator.
        tk.Frame(self._buttonBar, bg='light gray', width=1).pack(side='left', fill='y', padx=4)

        # "View Books" button.
        self._viewBooksButton = ttk.Button(
            self._buttonBar,
            text=_('Books'),
            image=self._ui.icons.viewBookIcon,
            command=lambda: self._ui.tv.show_branch(BK_ROOT)
            )
        self._viewBooksButton.pack(side='left')
        self._viewBooksButton.image = self._ui.icons.viewBookIcon

        # "View Characters" button.
        self._viewCharactersButton = ttk.Button(
            self._buttonBar,
            text=_('Characters'),
            image=self._ui.icons.viewCharactersIcon,
            command=lambda: self._ui.tv.show_branch(CR_ROOT)
            )
        self._viewCharactersButton.pack(side='left')
        self._viewCharactersButton.image = self._ui.icons.viewCharactersIcon

        # "View Arcs" button.
        self._viewArcsButton = ttk.Button(
            self._buttonBar,
            text=_('Arcs'),
            image=self._ui.icons.viewArcsIcon,
            command=lambda: self._ui.tv.show_branch(AC_ROOT)
            )
        self._viewArcsButton.pack(side='left')
        self._viewArcsButton.image = self._ui.icons.viewArcsIcon

        # Separator.
        tk.Frame(self._buttonBar, bg='light gray', width=1).pack(side='left', fill='y', padx=4)

        # "Save" button.
        self._saveButton = ttk.Button(
            self._buttonBar,
            text=_('Save'),
            image=self._ui.icons.saveIcon,
            command=self._ctrl.save_project
            )
        self._saveButton.pack(side='left')
        self._saveButton.image = self._ui.icons.saveIcon

        # Separator.
        tk.Frame(self._buttonBar, bg='light gray', width=1).pack(side='left', fill='y', padx=4)

        # "Add" button.
        self._addElementButton = ttk.Button(
            self._buttonBar,
            text=_('Add'),
            image=self._ui.icons.addIcon,
            command=self._ctrl.add_element
            )
        self._addElementButton.pack(side='left')
        self._addElementButton.image = self._ui.icons.addIcon

        # "Add Child" button.
        self._addChildButton = ttk.Button(
            self._buttonBar,
            text=_('Add'),
            image=self._ui.icons.addChildIcon,
            command=self._ctrl.add_child
            )
        self._addChildButton.pack(side='left')
        self._addChildButton.image = self._ui.icons.addChildIcon

        # "Add Parent" button.
        self._addParentButton = ttk.Button(
            self._buttonBar,
            text=_('Add'),
            image=self._ui.icons.addParentIcon,
            command=self._ctrl.add_parent
            )
        self._addParentButton.pack(side='left')
        self._addParentButton.image = self._ui.icons.addParentIcon

        # "Remove" button.
        self._removeElementButton = ttk.Button(
            self._buttonBar,
            text=_('Add'),
            image=self._ui.icons.removeIcon,
            command=self._ctrl.delete_elements
            )
        self._removeElementButton.pack(side='left')
        self._removeElementButton.image = self._ui.icons.removeIcon

        # Reverse order (side='right').

        # "Toggle properties" button.
        self._propertiesButton = ttk.Button(
            self._buttonBar,
            text=_('Toggle Properties'),
            image=self._ui.icons.propertiesIcon,
            command=self._ui.toggle_properties_view
            )
        self._propertiesButton.pack(side='right')
        self._propertiesButton.image = self._ui.icons.propertiesIcon

        self._buttonBar.pack(expand=False, before=self._ui.appWindow, fill='both')

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self._saveButton.config(state='disabled')
        self._viewCharactersButton.config(state='disabled')
        self._viewBooksButton.config(state='disabled')
        self._viewArcsButton.config(state='disabled')
        self._goBackButton.config(state='disabled')
        self._goForwardButton.config(state='disabled')
        self._propertiesButton.config(state='disabled')
        self._addElementButton.config(state='disabled')
        self._addChildButton.config(state='disabled')
        self._addParentButton.config(state='disabled')
        self._removeElementButton.config(state='disabled')

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self._saveButton.config(state='normal')
        self._viewCharactersButton.config(state='normal')
        self._viewBooksButton.config(state='normal')
        self._viewArcsButton.config(state='normal')
        self._goBackButton.config(state='normal')
        self._goForwardButton.config(state='normal')
        self._propertiesButton.config(state='normal')
        self._addElementButton.config(state='normal')
        self._addChildButton.config(state='normal')
        self._addParentButton.config(state='normal')
        self._removeElementButton.config(state='normal')

