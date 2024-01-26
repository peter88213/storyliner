"""Provide a class for the storyliner model.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from storylinerlib.model.sl_work_file import SlWorkFile
from storylinerlib.model.arc import Arc
from storylinerlib.model.basic_element import BasicElement
from storylinerlib.model.character import Character
from novxlib.model.id_generator import create_id
from storylinerlib.model.story import Story
from storylinerlib.model.book import Book
from storylinerlib.model.turning_point import TurningPoint
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import ARC_POINT_PREFIX
from storylinerlib.storyliner_globals import ARC_PREFIX
from storylinerlib.storyliner_globals import CHARACTER_PREFIX
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import Error
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import _


class SlModel:
    """storyliner model representation."""

    def __init__(self):
        """Initialize instance variables.
        
        Positional arguments:
            tree: SlTreeview -- The tree view shared by model and view.
        """
        self.tree = None
        # strategy class
        self.prjFile = None
        self.story = None
        self._clients = []
        # objects to be updated on model change

        self._internalModificationFlag = False

    @property
    def isModified(self):
        # Boolean -- True if there are unsaved changes.
        return self._internalModificationFlag

    @isModified.setter
    def isModified(self, setFlag):
        self._internalModificationFlag = setFlag
        for client in self._clients:
            client.refresh()

    def add_arc(self, **kwargs):
        """Add an arc to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title. 
            
        - If the target node is of the same type as the new node, 
          place the new node after the selected node and select it.
        - Otherwise, place the new node at the last position.   

        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', '')
        index = 'end'
        if targetNode.startswith(ARC_PREFIX):
            index = self.tree.index(targetNode) + 1
        acId = create_id(self.story.arcs, prefix=ARC_PREFIX)
        self.story.arcs[acId] = Arc(
            title=kwargs.get('title', f'{_("New Arc")} ({acId})'),
            desc='',
            shortName=acId,
            notes='',
            on_element_change=self.on_element_change,
            )
        self.tree.insert(AC_ROOT, index, acId)
        return acId

    def add_character(self, **kwargs):
        """Add a character to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title.
            
        - If the target node is of the same type as the new node, 
          place the new node after the selected node and select it.
        - Otherwise, place the new node at the last position.   

        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', '')
        index = 'end'
        if targetNode.startswith(CHARACTER_PREFIX):
            index = self.tree.index(targetNode) + 1
        crId = create_id(self.story.characters, prefix=CHARACTER_PREFIX)
        self.story.characters[crId] = Character(
            title=kwargs.get('title', f'{_("New Character")} ({crId})'),
            fullName='',
            desc='',
            role='',
            notes='',
            on_element_change=self.on_element_change,
            )
        self.tree.insert(CR_ROOT, index, crId)
        return crId

    def add_book(self, **kwargs):
        """Add a book to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title. 
            
        - If the target node is of the same type as the new node, 
          place the new node after the selected node and select it.
        - Otherwise, place the new node at the last position.   

        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', '')
        index = 'end'
        if targetNode.startswith(BOOK_PREFIX):
            index = self.tree.index(targetNode) + 1
        lcId = create_id(self.story.books, prefix=BOOK_PREFIX)
        self.story.books[lcId] = Book(
            title=kwargs.get('title', f'{_("New Book")} ({lcId})'),
            desc='',
            nvPath='',
            notes='',
            on_element_change=self.on_element_change,
            )
        self.tree.insert(BK_ROOT, index, lcId)
        return lcId

    def add_turning_point(self, **kwargs):
        """Add a turning point to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Section title. Default: Auto-generated title.
            position: int -- Section title. Default: Auto-generated title.
            
        - Place the new node at the next free position after the target node, if possible.
        - Otherwise, do nothing. 
        
        Return the turning point ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            return

        index = 'end'
        if targetNode.startswith(ARC_POINT_PREFIX):
            parent = self.tree.parent(targetNode)
            index = self.tree.index(targetNode) + 1
        elif targetNode.startswith(ARC_PREFIX):
            parent = targetNode
        else:
            return

        tpId = create_id(self.story.turningPoints, prefix=ARC_POINT_PREFIX)
        self.story.turningPoints[tpId] = TurningPoint(
            title=kwargs.get('title', f'{_("New Turning point")} ({tpId})'),
            desc='',
            notes='',
            position=kwargs.get('position', None),
            on_element_change=self.on_element_change,
            )
        self.tree.insert(parent, index, tpId)
        return tpId

    def close_project(self):
        self.isModified = False
        self.tree.on_element_change = self.tree.do_nothing
        self.story = None
        self.prjFile = None

    def delete_element(self, elemId):
        """Delete an element and its children.
        
        Positional arguments:
            elemId: str -- ID of the element to delete.
        
        """

        if elemId.startswith(CHARACTER_PREFIX):
            # Delete a character and remove references.
            self.tree.delete(elemId)
            del self.story.characters[elemId]
        elif elemId.startswith(BOOK_PREFIX):
            # Delete a book and remove references.
            for tpId in self.story.turningPoints:
                try:
                    tpBooks = self.story.turningPoints[tpId].books
                    tpBooks.remove(elemId)
                    self.story.turningPoints[tpId].books = tpBooks
                except:
                    pass
            self.tree.delete(elemId)
            del self.story.books[elemId]
        elif elemId.startswith(ARC_PREFIX):
            # Delete an arc and remove children.
            del self.story.arcs[elemId]
            for tpId in self.tree.get_children(elemId):
                del self.story.turningPoints[tpId]
                self.tree.delete(tpId)
            self.tree.delete(elemId)
        elif elemId.startswith(ARC_POINT_PREFIX):
            # Delete an turning point and remove references.
            del self.story.turningPoints[elemId]
            self.tree.delete(elemId)

    def move_node(self, node, targetNode):
        """Move a node to another position.
        
        Positional elements:
            node: str - ID of the node to move.
            targetNode: str -- ID of the new parent/predecessor of the node.
        """
        if node[:2] == targetNode[:2]:
            self.tree.move(node, self.tree.parent(targetNode), self.tree.index(targetNode))
        elif (node.startswith(ARC_POINT_PREFIX) and targetNode.startswith(ARC_PREFIX)):
            if not self.tree.get_children(targetNode):
                self.tree.move(node, targetNode, 0)
            elif self.tree.prev(targetNode):
                self.tree.move(node, self.tree.prev(targetNode), 'end')

    def new_project(self, tree):
        """Create a storyliner project instance."""
        self.story = Story(
            title='',
            desc='',
            tree=tree,
            on_element_change=self.on_element_change,
            )
        self.prjFile = SlWorkFile('')
        self.prjFile.story = self.story
        self._initialize_tree(self.on_element_change)

    def on_element_change(self):
        """Callback function to report model element modifications."""
        self.isModified = True

    def open_project(self, filePath):
        """Initialize instance variables.
        
        Positional arguments:
            filePath: str -- path to the prjFile file.
        """
        self.story = Story(tree=self.tree)
        self.prjFile = SlWorkFile(filePath)
        self.prjFile.story = self.story
        self.prjFile.read()
        self.isModified = False
        self._initialize_tree(self.on_element_change)

    def register_client(self, client):
        if not client in self._clients:
            self._clients.append(client)

    def reset_tree(self):
        """Clear the tree."""
        self.tree.reset()

    def save_project(self, filePath=None):
        """Write the storyliner project file, and set "unchanged" status."""
        if filePath is not None:
            self.prjFile.filePath = filePath
        self.prjFile.write()
        self.isModified = False

    def unregister_client(self, client):
        try:
            self._clients.remove(client)
        except:
            pass

    def _initialize_tree(self, on_element_change):
        """Iterate the tree and configure the elements."""

        def initialize_branch(node):
            """Recursive tree walker.
            
            Positional arguments: 
                node: str -- Node ID to start from.
            """
            for elemId in self.tree.get_children(node):
                if elemId.startswith(CHARACTER_PREFIX):
                    self.story.characters[elemId].on_element_change = on_element_change
                elif elemId.startswith(BOOK_PREFIX):
                    self.story.books[elemId].on_element_change = on_element_change
                elif elemId.startswith(ARC_PREFIX):
                    initialize_branch(elemId)
                    self.story.arcs[elemId].on_element_change = on_element_change
                elif elemId.startswith(ARC_POINT_PREFIX):
                    self.story.turningPoints[elemId].on_element_change = on_element_change
                else:
                    initialize_branch(elemId)

        initialize_branch('')
        self.story.on_element_change = on_element_change
        self.tree.on_element_change = on_element_change

