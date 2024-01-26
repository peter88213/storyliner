"""Provide a class for a storyliner project tree substitute.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import ARC_PREFIX
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import BK_ROOT


class SlTree:
    """storyliner project structure, emulating the ttk.Treeview interface.
    
    This allows independence from the tkinter library.
    """

    def __init__(self):
        self.roots = {
            AC_ROOT:[],
            BK_ROOT:[],
            CR_ROOT:[],
            }
        # values : listed children's IDs
        self.srtTurningPoints = {}
        # key: arc ID
        # value : turning point ID

    def append(self, parent, iid):
        """Creates a new item with identifier iid."""
        if parent in self.roots:
            self.roots[parent].append(iid)
            if parent == AC_ROOT:
                self.srtTurningPoints[iid] = []
        elif parent.startswith(ARC_PREFIX):
            try:
                self.srtTurningPoints[parent].append(iid)
            except:
                self.srtTurningPoints[parent] = [iid]

    def delete(self, *items):
        """Delete all specified items and all their descendants. The root
        item may not be deleted."""
        raise NotImplementedError

    def delete_children(self, parent):
        """Delete all parent's descendants."""
        if parent in self.roots:
            self.roots[parent] = []
            if parent == AC_ROOT:
                self.srtTurningPoints = {}
        elif parent.startswith(ARC_PREFIX):
            self.srtTurningPoints[parent] = []

    def get_children(self, item):
        """Returns the list of children belonging to item."""
        if item in self.roots:
            return self.roots[item]

        elif item.startswith(ARC_PREFIX):
            return self.srtTurningPoints.get(item, [])

    def index(self, item):
        """Return the integer index of item within its parent's list
        of children."""
        raise NotImplementedError

    def insert(self, parent, index, iid):
        """Create a new item with identifier iid."""
        if parent in self.roots:
            self.roots[parent].insert(index, iid)
            if parent == AC_ROOT:
                self.srtTurningPoints[iid] = []
        elif parent.startswith(ARC_PREFIX):
            try:
                self.srtTurningPoints.insert(index, iid)
            except:
                self.srtTurningPoints[parent] = [iid]

    def move(self, item, parent, index):
        """Move item to position index in parent's list of children.

        It is illegal to move an item under one of its descendants. If
        index is less than or equal to zero, item is moved to the
        beginning, if greater than or equal to the number of children,
        it is moved to the end. If item was detached it is reattached.
        """
        raise NotImplementedError

    def next(self, item):
        """Return the identifier of item's next sibling, or '' if item
        is the last child of its parent."""
        raise NotImplementedError

    def parent(self, item):
        """Return the ID of the parent of item, or '' if item is at the
        top level of the hierarchy."""
        raise NotImplementedError

    def prev(self, item):
        """Return the identifier of item's previous sibling, or '' if
        item is the first child of its parent."""
        raise NotImplementedError

    def reset(self):
        """Clear the tree."""
        for item in self.roots:
            self.roots[item] = []
        self.srtSections = {}
        self.srtTurningPoints = {}

    def set_children(self, item, newchildren):
        """Replaces item’s child with newchildren."""
        if item in self.roots:
            self.roots[item] = newchildren[:]
            if item == AC_ROOT:
                self.srtTurningPoints = {}
        elif item.startswith(ARC_PREFIX):
            self.srtTurningPoints[item] = newchildren[:]


if __name__ == '__main__':
    thisTree = SlTree()
