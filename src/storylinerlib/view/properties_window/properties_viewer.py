""" Provide a class for the properties view window.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk

from storylinerlib.view.properties_window.arc_view import ArcView
from storylinerlib.view.properties_window.character_view import CharacterView
from storylinerlib.view.properties_window.book_view import BookView
from storylinerlib.view.properties_window.no_view import NoView
from storylinerlib.view.properties_window.project_view import ProjectView
from storylinerlib.view.properties_window.turning_point_view import TurningPointView
from storylinerlib.storyliner_globals import ARC_POINT_PREFIX
from storylinerlib.storyliner_globals import ARC_PREFIX
from storylinerlib.storyliner_globals import CHARACTER_PREFIX
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import AC_ROOT


class PropertiesViewer(ttk.Frame):
    """A window viewing the selected element's properties."""

    def __init__(self, parent, model, view, controller, **kw):
        super().__init__(parent, **kw)
        self._mdl = model
        self._ui = view
        self._ctrl = controller
        self._noView = NoView(self, self._mdl, self._ui, self._ctrl)
        self._projectView = ProjectView(self, self._mdl, self._ui, self._ctrl)
        self._bookView = BookView(self, self._mdl, self._ui, self._ctrl)
        self._characterView = CharacterView(self, self._mdl, self._ui, self._ctrl)
        self._arcView = ArcView(self, self._mdl, self._ui, self._ctrl)
        self._turningPointView = TurningPointView(self, self._mdl, self._ui, self._ctrl)
        self._elementView = self._noView
        self._elementView.set_data(None)
        self._elementView.doNotUpdate = False
        self._allViews = [
            self._projectView,
            self._characterView,
            self._bookView,
            self._arcView,
            self._turningPointView,
            ]

    def apply_changes(self, event=None):
        # This is called by the controller to make sure changes take effect
        # e.g. when starting an export while a property entry still has the focus.
        if not self._ctrl.isLocked:
            self._elementView.doNotUpdate = True
            self._elementView.apply_changes()
            self._elementView.doNotUpdate = False

    def focus_title(self):
        """Prepare the current element's title entry for manual input."""
        self._elementView.focus_title()

    def show_properties(self, nodeId):
        """Show the properties of the selected element."""
        if self._mdl is None:
            self._view_nothing()
        elif nodeId.startswith(CHARACTER_PREFIX):
            self._view_character(nodeId)
        elif nodeId.startswith(BOOK_PREFIX):
            self._view_book(nodeId)
        elif nodeId.startswith(ARC_PREFIX):
            self._view_arc(nodeId)
        elif nodeId.startswith(ARC_POINT_PREFIX):
            self._view_turning_point(nodeId)
        else:
            self._view_nothing()
        self._elementView.doNotUpdate = False

    def refresh(self):
        """Refresh the view after changes have been made "outsides"."""
        if not self._elementView.doNotUpdate:
            try:
                self.show_properties(self._elementView._elementId)
            except:
                pass

    def _set_data(self, elemId):
        """Fill the widgets with the data of the element to view and change."""
        self._elementView.set_data(elemId)

    def _view_arc(self, acId):
        """Show the selected arc.
        
        Positional arguments:
            acId: str -- Arc ID
        """
        if not self._elementView is self._arcView:
            self._elementView.hide()
            self._elementView = self._arcView
            self._elementView.show()
        self._set_data(acId)

    def _view_character(self, crId):
        """Show the selected character's properties.
                
        Positional arguments:
            crId: str -- character ID
        """
        if not self._elementView is self._characterView:
            self._elementView.hide()
            self._elementView = self._characterView
            self._elementView.show()
        self._set_data(crId)

    def _view_book(self, lcId):
        """Show the selected book's properties.
                
        Positional arguments:
            lcId: str -- book ID
        """
        if not self._elementView is self._bookView:
            self._elementView.hide()
            self._elementView = self._bookView
            self._elementView.show()
        self._set_data(lcId)

    def _view_nothing(self):
        """Reset properties if nothing valid is selected."""
        if not self._elementView is self._noView:
            self._elementView.hide()
            self._elementView = self._noView
            self._elementView.show()

    def _view_project(self):
        """Show the project's properties."""
        if not self._elementView is self._projectView:
            self._elementView.hide()
            self._elementView = self._projectView
            self._elementView.show()
        self._set_data(AC_ROOT)

    def _view_turning_point(self, tpId):
        """Show the selected turning point
        Positional arguments:
            tpId: str -- Turning point ID
        """
        if not self._elementView is self._turningPointView:
            self._elementView.hide()
            self._elementView = self._turningPointView
            self._elementView.show()
        self._set_data(tpId)

