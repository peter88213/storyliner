"""Provide a converter class for document export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
from datetime import datetime
import os
from tkinter import messagebox

from novxlib.converter.export_target_factory import ExportTargetFactory
from novxlib.file.doc_open import open_document
from novxlib.novx.data_writer import DataWriter
from storylinerlib.storyliner_globals import Error
from storylinerlib.storyliner_globals import _
from storylinerlib.storyliner_globals import norm_path


class SlDocExporter:
    """Converter class for document export."""
    EXPORT_TARGET_CLASSES = [
        ]

    def __init__(self):
        """Create strategy class instances."""
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self._source = None
        self._target = None

    def run(self, source, suffix, **kwargs):
        """Create a target object and run conversion.

        Positional arguments: 
            source -- NovxFile instance.
            suffix: str -- Target file name suffix.
            
        On success, return a message. Otherwise raise the Error exception.
        """
        self._source = source
        self._isNewer = False
        __, self._target = self.exportTargetFactory.make_file_objects(self._source.filePath, suffix=suffix)
        if os.path.isfile(self._target.filePath):
            targetTimestamp = os.path.getmtime(self._target.filePath)
            try:
                if  targetTimestamp > self._source.timestamp:
                    timeStatus = _('Newer than the project file')
                    self._isNewer = True
                    defaultButton = 'yes'
                else:
                    timeStatus = _('Older than the project file')
                    defaultButton = 'no'
            except:
                timeStatus = ''
            self._targetFileDate = datetime.fromtimestamp(targetTimestamp).replace(microsecond=0).isoformat(sep=' ')
            title = _('Export document')
            message = _('{0} already exists.\n(last saved on {2})\n{1}.\n\nOpen this document instead of overwriting it?').format(
                        norm_path(self._target.DESCRIPTION), timeStatus, self._targetFileDate)
            openExisting = messagebox.askyesnocancel(title, message, default=defaultButton)
            if openExisting is None:
                raise Error(f'{_("Action canceled by user")}.')

            elif openExisting:
                open_document(self._target.filePath)
                if self._isNewer:
                    prefix = ''
                else:
                    prefix = '!'
                    # warn the user, if a document is open that might be outdated
                return f'{prefix}{_("Opened existing {0} (last saved on {1})").format(self._target.DESCRIPTION, self._targetFileDate)}.'

        # Generate a new document. Overwrite the existing document, if any.
        self._target.story = self._source.story
        self._target.write()
        self._targetFileDate = datetime.now().replace(microsecond=0).isoformat(sep=' ')
        if kwargs.get('show', True):
            if messagebox.askyesno(title=self._target.story.title, message=_('{} created.\n\nOpen now?').format(norm_path(self._target.DESCRIPTION))):
                open_document(self._target.filePath)
        return _('Created {0} on {1}.').format(self._target.DESCRIPTION, self._targetFileDate)

