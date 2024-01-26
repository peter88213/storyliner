"""Provide a class for the storyliner project file.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from datetime import datetime
import os

from storylinerlib.stlx.stlx_file import StlxFile
from storylinerlib.storyliner_globals import _


class SlWorkFile(StlxFile):
    """storyliner project file representation.
    
    This is to be an adapter to the .stlx project format.
    
    Public instance variables:
        timestamp: float -- Time of last file modification (number of seconds since the epoch).
    
    Public properties:
        fileDate: str -- ISO-formatted file date/time (YYYY-MM-DD hh:mm:ss).

    Extends the superclass.
    """
    DESCRIPTION = _('storyliner project')
    _LOCKFILE_PREFIX = '.LOCK.'
    _LOCKFILE_SUFFIX = '#'

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath: str -- path to the project file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.timestamp = None

    @property
    def fileDate(self):
        if self.timestamp is not None:
            return datetime.fromtimestamp(self.timestamp).replace(microsecond=0).isoformat(sep=' ')
        else:
            return _('Never')

    def has_changed_on_disk(self):
        """Return True if the yw project file has changed since last opened."""
        try:
            if self.timestamp != os.path.getmtime(self.filePath):
                return True
            else:
                return False

        except:
            # this is for newly created projects
            return False

    def read(self):
        """Read file, get custom data, word count log, and timestamp.
        
        Extends the superclass method.
        """
        super().read()

        #--- Read the file timestamp.
        try:
            self.timestamp = os.path.getmtime(self.filePath)
        except:
            self.timestamp = None

    def write(self):
        """Update the timestamp.
        
        Extends the superclass method.
        """
        super().write()
        self.timestamp = os.path.getmtime(self.filePath)

    def _split_file_path(self):
        head, tail = os.path.split(self.filePath)
        if head:
            head = f'{head}/'
        else:
            head = './'
        return head, tail

