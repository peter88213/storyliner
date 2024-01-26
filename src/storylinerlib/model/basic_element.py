"""Provide a base class for storyliner element representation.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""


class BasicElement:
    """Basic data model element representation.

    Public properties:
        title: str -- Element title (name)
        desc: str -- Element description
        
    Public instance variables:
        on_element_change -- Points to a callback routine for element changes
        
    The on_element_change method is called when the value of any property changes.
    This method can be overridden at runtime for each individual element instance.
    """

    def __init__(self,
            on_element_change=None,
            title=None,
            desc=None):
        """Set the initial values.
        
        Optional arguments:
            on_element_change -- Points to a callback routine for element changes
            title: str -- Element title (name)
            desc: str -- Element description

        If on_element_change is None, the do_nothing method will be assigned to it.
            
        General note:
        When merging files, only new elements that are not None will override 
        existing elements. This allows you to easily update a storyliner project 
        from a document that contains only a subset of the data model.
        Keep this in mind when setting the initial values.
        """
        if on_element_change is None:
            self.on_element_change = self.do_nothing
        else:
            self.on_element_change = on_element_change
        self._title = title
        self._desc = desc

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, newVal):
        if self._title != newVal:
            self._title = newVal
            self.on_element_change()

    @property
    def desc(self):
        return self._desc

    @desc.setter
    def desc(self, newVal):
        if self._desc != newVal:
            self._desc = newVal
            self.on_element_change()

    def do_nothing(self):
        """Standard callback routine for element changes."""
        pass

