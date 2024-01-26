"""Provide a class for a characters/books/items importer.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from storylinerlib.widgets.pick_list import PickList
from novxlib.model.id_generator import create_id
from novxlib.model.novel import Novel
from novxlib.model.nv_tree import NvTree
from novxlib.novx.character_data_reader import CharacterDataReader
from novxlib.novx.item_data_reader import ItemDataReader
from novxlib.novx.book_data_reader import BookDataReader
from storylinerlib.storyliner_globals import CHARACTER_PREFIX
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import ITEM_PREFIX
from storylinerlib.storyliner_globals import IT_ROOT
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import _
from storylinerlib.storyliner_globals import norm_path


class SlDataImporter:
    """Characters/books/items importer with a pick list."""

    def __init__(self, model, view, controller, filePath, elemPrefix):
        """Open a pick list with the elements of the XML data file specified by filePath.
        
        Positional arguments:
            view -- the caller.
            filePath: str -- Path of the XML data file.
            elemPrefix: str -- Prefix of the new element IDs.
        """
        self._mdl = model
        self._ui = view
        self._ctrl = controller
        sources = {
            CHARACTER_PREFIX:CharacterDataReader,
            BOOK_PREFIX:BookDataReader,
            ITEM_PREFIX:ItemDataReader,
            }
        source = sources[elemPrefix](filePath)
        source.story = Novel(tree=NvTree())
        errorMessages = {
            CHARACTER_PREFIX:_('No character data found'),
            BOOK_PREFIX:_('No book data found'),
            ITEM_PREFIX:_('No item data found'),
            }
        try:
            source.read()
        except:
            self._ui.set_status(f"!{errorMessages[elemPrefix]}: {norm_path(filePath)}")
            return

        sourceElements = {
            CHARACTER_PREFIX:source.story.characters,
            BOOK_PREFIX:source.story.books,
            ITEM_PREFIX:source.story.items,
            }
        targetElements = {
            CHARACTER_PREFIX:self._mdl.story.characters,
            BOOK_PREFIX:self._mdl.story.books,
            ITEM_PREFIX:self._mdl.story.items,
            }
        elemParents = {
            CHARACTER_PREFIX:CR_ROOT,
            BOOK_PREFIX:BK_ROOT,
            ITEM_PREFIX:IT_ROOT,
            }
        windowTitles = {
            CHARACTER_PREFIX:_('Select characters'),
            BOOK_PREFIX:_('Select books'),
            ITEM_PREFIX:_('Select items'),
            }
        self._elemPrefix = elemPrefix
        self._sourceElements = sourceElements[elemPrefix]
        self._targetElements = targetElements[elemPrefix]
        self._elemParent = elemParents[elemPrefix]
        pickButtonLabel = _('Import selected elements')
        offset = 50
        size = '300x400'
        __, x, y = self._ui.root.geometry().split('+')
        windowGeometry = f'{size}+{int(x)+offset}+{int(y)+offset}'
        PickList(
            windowTitles[elemPrefix],
            windowGeometry,
            self._sourceElements,
            pickButtonLabel,
            self._pick_element
            )

    def _pick_element(self, elements):
        """Add the selected elements to the story."""
        i = 0
        for  elemId in elements:
            newId = create_id(self._targetElements, prefix=self._elemPrefix)
            self._targetElements[newId] = self._sourceElements[elemId]
            self._mdl.story.tree.append(self._elemParent, newId)
            i += 1
        if i > 0:
            self._ui.tv.go_to_node(newId)
            self._ui.set_status(f'{i} {_("elements imported")}')
