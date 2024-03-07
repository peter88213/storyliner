"""Provide a tkinter based storyliner tree view.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from tkinter import ttk

from storylinerlib.model.sl_treeview import SlTreeview
from storylinerlib.storyliner_globals import prefs
from storylinerlib.view.tree_window.history_list import HistoryList
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import ARC_POINT_PREFIX
from storylinerlib.storyliner_globals import ARC_PREFIX
from storylinerlib.storyliner_globals import CHARACTER_PREFIX
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import ROOT_PREFIX
from storylinerlib.storyliner_globals import _
from storylinerlib.storyliner_globals import list_to_string
from storylinerlib.storyliner_globals import string_to_list
import tkinter as tk
import tkinter.font as tkFont


class TreeViewer(ttk.Frame):
    """Widget for storyliner tree view."""
    COLORING_MODES = [_('None'), _('Status'), _('Work phase')]
    # List[str] -- Section row coloring modes.

    _COLUMNS = dict(
        bk=(_('Books'), 'bk_width'),
        )
    # Key: column ID
    # Value: (column title, column width)

    _ROOT_TITLES = {
        CR_ROOT: _('Characters'),
        BK_ROOT: _('Books'),
        AC_ROOT: _('Plot lines'),
        }

    def __init__(self, parent, model, view, controller, kwargs, **kw):
        """Put a tkinter tree in the specified parent widget.
        
        Positional arguments:
            parent -- parent widget for displaying the tree view.
            view -- GUI class reference.        
        """
        super().__init__(parent, **kw)
        self._mdl = model
        self._ui = view
        self._ctrl = controller
        self._wordsTotal = None
        self.skipUpdate = False

        # Create a story tree.
        self.tree = SlTreeview(self)
        scrollX = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        scrollY = ttk.Scrollbar(self.tree, orient='vertical', command=self.tree.yview)
        self.tree.configure(xscrollcommand=scrollX.set)
        self.tree.configure(yscrollcommand=scrollY.set)
        scrollX.pack(side='bottom', fill='x')
        scrollY.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)

        #--- Add columns to the tree.
        self.configure_columns()

        #--- configure tree row display.
        fontSize = tkFont.nametofont('TkDefaultFont').actual()['size']
        self.tree.tag_configure('root', font=('', fontSize, 'bold'))
        self.tree.tag_configure('arc', font=('', fontSize, 'bold'), foreground=kwargs['color_arc'])
        self.tree.tag_configure('turning_point', foreground=kwargs['color_point'])
        self.tree.tag_configure('book', foreground=kwargs['color_book'])
        self.tree.tag_configure('character', foreground=kwargs['color_character'])

        #--- Browsing history.
        self._history = HistoryList()

        #--- Create public submenus and local context menus.
        self._build_menus()

        #--- Bind events.
        self._bind_events(**kwargs)

    def close_children(self, parent):
        """Recursively close children nodes.
        
        Positional arguments:
            parent: str -- Root node of the branch to close.
        """
        self.tree.item(parent, open=False)
        for child in self.tree.get_children(parent):
            self.close_children(child)

    def configure_columns(self):
        """Determine the order of the columnns.
        
        Read from the ui keyword arguments:
            column_order: str -- ordered column IDs, semicolon-separated.
        
        Write instance variables:
            _colPos: dict -- key=ID, value=index.
            columns -- list of tuples (ID, title, width).
        """
        # Column position by column ID.
        self._colPos = {}
        self.columns = []
        titles = []
        srtColumns = string_to_list(prefs['column_order'])

        # Check data integrity.
        for coId in self._COLUMNS:
            if not coId in srtColumns:
                srtColumns.append(coId)
        i = 0
        for coId in srtColumns:
            try:
                title, width = self._COLUMNS[coId]
            except:
                continue
            self._colPos[coId] = i
            i += 1
            self.columns.append((coId, title, width))
            titles.append(title)
        self.tree.configure(columns=tuple(titles))
        for column in self.columns:
            self.tree.heading(column[1], text=column[1], anchor='w')
            self.tree.column(column[1], width=int(prefs[column[2]]), minwidth=3, stretch=False)
        self.tree.column('#0', width=int(prefs['title_width']), stretch=False)

    def go_back(self, event=None):
        """Select a node back in the tree browsing history."""
        self._browse_tree(self._history.go_back())

    def go_forward(self, event=None):
        """Select a node forward in the tree browsing history."""
        self._browse_tree(self._history.go_forward())

    def go_to_node(self, node):
        """Select and view a node.
        
        Positional arguments:
            node: str -- Tree element to select and show.
        """
        try:
            self.tree.focus_set()
            self.tree.selection_set(node)
            self.tree.see(node)
            self.tree.focus(node)
        except:
            pass

    def next_node(self, thisNode):
        """Return the next node ID  of the same element type as thisNode.
        
        Positional arguments: 
            thisNode: str -- node ID
            root: str -- root ID of the branch to search 
        """

        def search_tree(parent, result, flag):
            """Search the tree for the node ID after thisNode."""
            for child in self.tree.get_children(parent):
                if result:
                    break
                if child.startswith(prefix):
                    if flag:
                        result = child
                        break

                    elif child == thisNode:
                        flag = True
                else:
                    result, flag = search_tree(child, result, flag)
            return result, flag

        prefix = thisNode[:2]
        root = self.tree.parent(thisNode)
        while not root.startswith(ROOT_PREFIX):
            root = self.tree.parent(root)
        nextNode, __ = search_tree(root, None, False)
        return nextNode

    def on_quit(self):
        """Write the applicaton's keyword arguments."""
        prefs['title_width'] = self.tree.column('#0', 'width')
        for i, column in enumerate(self.columns):
            prefs[column[2]] = self.tree.column(i, 'width')

    def open_children(self, parent):
        """Recursively show children nodes.
        
        Positional arguments:
            parent: str -- Root node of the branch to open.
        """
        self.tree.item(parent, open=True)
        for child in self.tree.get_children(parent):
            self.open_children(child)

    def prev_node(self, thisNode):
        """Return the previous node ID of the same element type as thisNode.

        Positional arguments: 
            thisNode: str -- node ID
            root: str -- root ID of the branch to search 
        """

        def search_tree(parent, result, prevNode):
            """Search the tree for the node ID before thisNode."""
            for child in self.tree.get_children(parent):
                if result:
                    break

                if child.startswith(prefix):
                    if child == thisNode:
                        result = prevNode
                        break
                    else:
                        prevNode = child
                else:
                    result, prevNode = search_tree(child, result, prevNode)
            return result, prevNode

        prefix = thisNode[:2]
        root = self.tree.parent(thisNode)
        while not root.startswith(ROOT_PREFIX):
            root = self.tree.parent(root)
        prevNode, __ = search_tree(root, None, None)
        return prevNode

    def reset_view(self):
        """Clear the displayed tree, and reset the browsing history."""
        self._history.reset()
        for rootElement in self.tree.get_children(''):
            self.tree.item(rootElement, text='')
            # Make the root element "invisible".
        self.tree.configure({'selectmode': 'none'})
        self._ctrl.reset_tree()

    def show_branch(self, node):
        """Go to node and open children.
        
        Positional arguments:
            node: str -- Root element of the branch to open.
        """
        self.go_to_node(node)
        self.open_children(node)
        return 'break'
        # this stops event propagation and allows for re-mapping e.g. the F10 key
        # (see: https://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter)

    def refresh(self, event=None):
        """Update the tree display to view changes.
        
        Iterate the tree and re-configure the columns.
        """

        def update_branch(node):
            """Recursive tree walker.
            
            Positional arguments: 
                node: str -- Node ID to start from.
            
            Return the incremented word count.
            """
            for elemId in self.tree.get_children(node):
                if elemId.startswith(CHARACTER_PREFIX):
                    title, columns, nodeTags = self._configure_character_display(elemId)
                elif elemId.startswith(BOOK_PREFIX):
                    title, columns, nodeTags = self._configure_book_display(elemId)
                elif elemId.startswith(ARC_PREFIX):
                    update_branch(elemId)
                    title, columns, nodeTags = self._configure_arc_display(elemId)
                elif elemId.startswith(ARC_POINT_PREFIX):
                    title, columns, nodeTags = self._configure_turning_point_display(elemId)
                else:
                    title = self._ROOT_TITLES[elemId]
                    columns = []
                    nodeTags = 'root'
                    update_branch(elemId)
                self.tree.item(elemId, text=title, values=columns, tags=nodeTags)

        if self.skipUpdate:
            self.skipUpdate = False
        elif self._mdl.prjFile is not None:
            update_branch('')
            self.tree.configure(selectmode='extended')

    def _bind_events(self, **kwargs):
        self.tree.bind('<<TreeviewSelect>>', self._on_select_node)
        self.tree.bind('<Delete>', self._ctrl.delete_elements)
        self.tree.bind(kwargs['button_context_menu'], self._on_open_context_menu)
        self.tree.bind('<Alt-B1-Motion>', self._on_move_node)

    def _browse_tree(self, node):
        """Select and show node. 
        
        Positional arguments:
            node: str -- History list element pointed to.
        
        - Do not add the move to the history list.
        - If node doesn't exist, reset the history.
        """
        if node and self.tree.exists(node):
            if self.tree.selection()[0] != node:
                self._history.lock()
                # make sure not to extend the history list
                self.go_to_node(node)
        else:
            self._history.reset()
            self._history.append_node(self.tree.selection()[0])

    def _build_menus(self):
        """Create public submenus and local context menus."""

        #--- Create local context menus.

        #--- Create a world element context menu.
        self._crCtxtMenu = tk.Menu(self.tree, tearoff=0)
        self._crCtxtMenu.add_command(label=_('Add'), command=self._ctrl.add_element)
        self._crCtxtMenu.add_separator()
        self._crCtxtMenu.add_command(label=_('Delete'), command=self._ctrl.delete_elements)

        #--- Create an arc context menu.
        self._acCtxtMenu = tk.Menu(self.tree, tearoff=0)
        self._acCtxtMenu.add_command(label=_('Add Arc'), command=self._ctrl.add_arc)
        self._acCtxtMenu.add_command(label=_('Add Turning point'), command=self._ctrl.add_turning_point)
        self._acCtxtMenu.add_separator()
        self._acCtxtMenu.add_command(label=_('Delete'), command=self._ctrl.delete_elements)

        #--- Create a book context menu.
        self._bkCtxtMenu = tk.Menu(self.tree, tearoff=0)
        self._bkCtxtMenu.add_command(label=_('Add Book'), command=self._ctrl.add_book)
        self._bkCtxtMenu.add_separator()
        self._bkCtxtMenu.add_command(label=_('Delete'), command=self._ctrl.delete_elements)

    def _configure_arc_display(self, acId):
        """Configure project note formatting and columns."""
        title = self._mdl.story.plotLines[acId].title
        if not title:
            title = _('Unnamed')
        title = f'({self._mdl.story.plotLines[acId].shortName}) {title}'
        columns = []
        for __ in self.columns:
            columns.append('')
        nodeTags = ['arc']
        return title, columns, tuple(nodeTags)

    def _configure_character_display(self, crId):
        """Configure character formatting and columns."""
        title = self._mdl.story.characters[crId].title
        if not title:
            title = _('Unnamed')
        columns = []
        for __ in self.columns:
            columns.append('')

        return title, columns, ('character')

    def _configure_book_display(self, bkId):
        """Configure book formatting and columns."""
        title = self._mdl.story.books[bkId].title
        if not title:
            title = _('Unnamed')
        columns = []
        for __ in self.columns:
            columns.append('')

        return title, columns, ('book')

    def _configure_turning_point_display(self, tpId):
        """Configure turning point formatting and columns."""
        title = self._mdl.story.plotPoints[tpId].title
        if not title:
            title = _('Unnamed')
        columns = []
        for __ in self.columns:
            columns.append('')
        tpBookTitles = []
        try:
            for bkId in self._mdl.story.plotPoints[tpId].books:
                tpBookTitles.append(self._mdl.story.books[bkId].title)
        except:
            pass
        columns[self._colPos['bk']] = list_to_string(tpBookTitles)

        return title, columns, ('turning_point')

    def _on_move_node(self, event):
        self._ctrl.move_node(
            self.tree.selection()[0],
            self.tree.identify_row(event.y)
            )

    def _on_open_context_menu(self, event):
        """Event handler for the tree's context menu.
        
        - Configure the context menu depending on the selected branch and the program state.
        - Open it.
        """
        if self._mdl is None:
            return

        row = self.tree.identify_row(event.y)
        if row:
            self.go_to_node(row)
            if row.startswith(ROOT_PREFIX):
                prefix = row
            else:
                prefix = row[:2]
            if prefix in (CR_ROOT, CHARACTER_PREFIX, BK_ROOT, BOOK_PREFIX):
                # Context is character/book.
                if self._ctrl.isLocked:
                    # No changes allowed.
                    self._crCtxtMenu.entryconfig(_('Add'), state='disabled')
                    self._crCtxtMenu.entryconfig(_('Delete'), state='disabled')
                else:
                    self._crCtxtMenu.entryconfig(_('Add'), state='normal')
                    if prefix.startswith('wr'):
                        # Context is the root of a world element type branch.
                        self._crCtxtMenu.entryconfig(_('Delete'), state='disabled')
                    else:
                        # Context is a world element.
                        self._crCtxtMenu.entryconfig(_('Delete'), state='normal')
                try:
                    self._crCtxtMenu.tk_popup(event.x_root, event.y_root, 0)
                finally:
                    self._crCtxtMenu.grab_release()
            elif prefix in (AC_ROOT, ARC_PREFIX, ARC_POINT_PREFIX):
                # Context is Arc/Turning point.
                if self._ctrl.isLocked:
                    # No changes allowed.
                    self._acCtxtMenu.entryconfig(_('Add Arc'), state='disabled')
                    self._acCtxtMenu.entryconfig(_('Add Turning point'), state='disabled')
                    self._acCtxtMenu.entryconfig(_('Delete'), state='disabled')
                elif prefix.startswith(AC_ROOT):
                    self._acCtxtMenu.entryconfig(_('Add Arc'), state='normal')
                    self._acCtxtMenu.entryconfig(_('Add Turning point'), state='disabled')
                    self._acCtxtMenu.entryconfig(_('Delete'), state='disabled')
                else:
                    self._acCtxtMenu.entryconfig(_('Add Arc'), state='normal')
                    self._acCtxtMenu.entryconfig(_('Add Turning point'), state='normal')
                    self._acCtxtMenu.entryconfig(_('Delete'), state='normal')
                try:
                    self._acCtxtMenu.tk_popup(event.x_root, event.y_root, 0)
                finally:
                    self._acCtxtMenu.grab_release()

    def _on_select_node(self, event=None):
        """Event handler for node selection.
        
        - Show the node's properties.
        - Add the node ID to the browsing history.
        """
        try:
            nodeId = self.tree.selection()[0]
        except IndexError:
            return

        self._history.append_node(nodeId)
        self._ui.on_change_selection(nodeId)

