"""Provide a tkinter GUI framework for storyliner.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import os
import sys
from shutil import copy2
from tkinter import filedialog

from storylinerlib.exporter.sl_doc_exporter import SlDocExporter
from storylinerlib.exporter.sl_html_reporter import SlHtmlReporter
from storylinerlib.model.sl_model import SlModel
from storylinerlib.model.sl_work_file import SlWorkFile
from storylinerlib.storyliner_globals import prefs
from storylinerlib.view.sl_view import SlView
from storylinerlib.storyliner_globals import ARC_POINT_PREFIX
from storylinerlib.storyliner_globals import ARC_PREFIX
from storylinerlib.storyliner_globals import CHARACTER_PREFIX
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import Error
from storylinerlib.storyliner_globals import _
from storylinerlib.storyliner_globals import norm_path


class SlController:
    """Controller for the storyliner application."""

    def __init__(self, title, tempDir):
        """Initialize the model and set up the application's user interface.
    
        Positional arguments:
            title: str -- Application title to be displayed at the window frame.
            tempDir: str -- Path of the temporary directory, used for e.g. packing zipfiles. 
         
        Processed keyword arguments:
            root_geometry: str -- geometry of the root window.
            coloring_mode: str -- tree coloring mode.
        
        Operation:
        - Create a main menu to be extended by subclasses.
        - Create a title bar for the project title.
        - Open a main window frame to be used by subclasses.
        - Create a status bar to be used by subclasses.
        - Create a path bar for the project file path.
        """
        self.tempDir = tempDir

        #--- Create the model
        self._mdl = SlModel()
        self._mdl.register_client(self)

        self.launchers = {}
        # launchers for opening linked non-standard filetypes.

        self._fileTypes = [(SlWorkFile.DESCRIPTION, SlWorkFile.EXTENSION)]
        self.importFiletypes = [(_('ODF Text document'), '.odt'), (_('ODF Spreadsheet document'), '.ods')]

        #--- Build the GUI.
        self._ui = SlView(self._mdl, self, title)

        # Link the model to the view.
        # Strictly speaking, this breaks the MVC pattern, since the
        # model depends on a data structure defined by the GUI framework.
        self._mdl.tree = self._ui.tv.tree

        self.disable_menu()
        self._internalLockFlag = False
        self._ui.tv.reset_view()

    @property
    def isLocked(self):
        # Boolean -- True if a lock file exists for the current project.
        return self._internalLockFlag

    @isLocked.setter
    def isLocked(self, setFlag):
        raise NotImplementedError

    def add_arc(self, **kwargs):
        """Add an arc to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title. 
            
        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_arc(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_chapter(self, **kwargs):
        """Add a chapter to the story.
             
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Section title. Default: Auto-generated title. 
            chType: int -- Chapter type. Default: 0.
            NoNumber: str -- Do not auto-number this chapter. Default: None.
            
        Return the chapter ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_chapter(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_character(self, **kwargs):
        """Add a character to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title.
            isMajor: bool -- If True, make the new character a major character. Default: False.
            
        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_character(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_child(self, event=None):
        """Add a child element to an element.
        
        What kind of element is added, depends on the selection's prefix.
        """
        if self._mdl.prjFile is None:
            return

        if not self.check_lock():
            try:
                selection = self._ui.tv.tree.selection()[0]
            except:
                return

        if selection.startswith(ARC_PREFIX):
            self.add_turning_point(targetNode=selection)
        elif selection == CR_ROOT:
            self.add_character(targetNode=selection)
        elif selection == BK_ROOT:
            self.add_book(targetNode=selection)
        elif selection == AC_ROOT:
            self.add_arc(targetNode=selection)

    def add_element(self, event=None):
        """Add an element to the story.
        
        What kind of element is added, depends on the selection's prefix.
        """
        if self._mdl.prjFile is None:
            return

        try:
            selection = self._ui.tv.tree.selection()[0]
        except:
            return

        if CHARACTER_PREFIX in selection:
            self.add_character(targetNode=selection)
        elif BOOK_PREFIX in selection:
            self.add_book(targetNode=selection)
        elif ARC_PREFIX in selection:
            self.add_arc(targetNode=selection)
        elif selection.startswith(ARC_POINT_PREFIX):
            self.add_turning_point(targetNode=selection)

    def add_item(self, **kwargs):
        """Add an item to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title. 
            
        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_item(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_book(self, **kwargs):
        """Add a book to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title. 
            
        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_book(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_parent(self, event=None):
        """Add a parent element to an element.
        
        What kind of element is added, depends on the selection's prefix.
        """
        if self._mdl.prjFile is None:
            return

        if not self.check_lock():
            try:
                selection = self._ui.tv.tree.selection()[0]
            except:
                return

        if selection.startswith(ARC_POINT_PREFIX):
            self.add_arc(targetNode=selection)

    def add_part(self, **kwargs):
        """Add a part to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str: Part title. Default -- Auto-generated title. 
            chType: int: Part type. Default -- 0.  
            NoNumber: str: Do not auto-number this part. Default -- None.
           
        Return the chapter ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_part(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_project_note(self, **kwargs):
        """Add a Project note to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Element title. Default: Auto-generated title. 
            
        Return the element's ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_project_note(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_section(self, **kwargs):
        """Add a section to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Section title. Default: Auto-generated title. 
            desc: str -- Description.
            scType: int -- Section type. Default: 0.
            status: int -- Section status. Default: 1.
            scPacing: int -- Action/Reaction/Custom. Default = 0.
            appendToPrev: bool -- Append to previous section. Default: False.
            
        - Place the new node at the next free position after the selection, if possible.
        - Otherwise, do nothing. 
        
        Return the section ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_section(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_stage(self, **kwargs):
        """Add a stage to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Stage title. Default: Auto-generated title. 
            desc: str -- Description.
            scType: int -- Scene type. Default: 3.
            
        Return the section ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_stage(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def add_turning_point(self, **kwargs):
        """Add a turning point to the story.
        
        Keyword arguments:
            targetNode: str -- Tree position where to place a new node.
            title: str -- Section title. Default: Auto-generated title. 
            
        Return the turning point ID, if successful.
        """
        targetNode = kwargs.get('targetNode', None)
        if targetNode is None:
            try:
                kwargs['targetNode'] = self._ui.tv.tree.selection()[0]
            except:
                pass
        newNode = self._mdl.add_turning_point(**kwargs)
        self._view_new_element(newNode)
        return newNode

    def check_lock(self):
        """
        TODO: Remove this
        """
        return False

    def close_project(self, event=None, doNotSave=False):
        """Close the current project.
        
        - Save changes
        - clear all views
        - reset flags
        """
        self._ui.propertiesView.apply_changes()
        if self._mdl.isModified and not doNotSave:
            if self._ui.ask_yes_no(_('Save changes?')):
                self.save_project()
        self._ui.propertiesView._view_nothing()
        self._mdl.close_project()
        self._ui.tv.reset_view()
        self._ui.root.title(self._ui.title)
        self.show_status('')
        self._ui.show_path('')
        self.disable_menu()
        return 'break'

    def copy_css(self, event=None):
        """Copy the provided css style sheet into the project directory."""
        try:
            projectDir, __ = os.path.split(self._mdl.prjFile.filePath)
            copy2(f'{os.path.dirname(sys.argv[0])}/css/novx.css', projectDir)
            message = _('Style sheet copied into the project folder.')
        except Exception as ex:
            message = f'!{str(ex)}'
        self._ui.set_status(message)

    def delete_elements(self, event=None, elements=None):
        """Delete elements and their children.
        
        Optional arguments:
            elements: list of IDs of the elements to delete.        
        """
        if elements is None:
            try:
                elements = self._ui.tv.tree.selection()
            except:
                return

        for  elemId in elements:
            if elemId.startswith(CHARACTER_PREFIX):
                candidate = f'{_("Character")} "{self._mdl.story.characters[elemId].title}"'
            elif elemId.startswith(BOOK_PREFIX):
                candidate = f'{_("Book")} "{self._mdl.story.books[elemId].title}"'
            elif elemId.startswith(ARC_PREFIX):
                candidate = f'{_("Arc")} "{self._mdl.story.arcs[elemId].title}"'
            elif elemId.startswith(ARC_POINT_PREFIX):
                candidate = f'{_("Turning point")} "{self._mdl.story.turningPoints[elemId].title}"'
            else:
                return

            if not self._ui.ask_yes_no(_('Delete {}?').format(candidate)):
                return

            if self._ui.tv.tree.prev(elemId):
                self._view_new_element(self._ui.tv.tree.prev(elemId))
            else:
                self._view_new_element(self._ui.tv.tree.parent(elemId))
            self._mdl.delete_element(elemId)

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self._ui.disable_menu()

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self._ui.enable_menu()

    def export_document(self, suffix, **kwargs):
        """Export a document.
        
        Required arguments:
            suffix -- str: Document type suffix (https://peter88213.github.io/storyliner/help/export_menu).
        """
        self._ui.restore_status()
        self._ui.propertiesView.apply_changes()
        if self._mdl.prjFile.filePath is not None or self.save_project():
            exporter = SlDocExporter()
            try:
                self._ui.set_status(exporter.run(self._mdl.prjFile, suffix, **kwargs))
            except Error as ex:
                self._ui.set_status(f'!{str(ex)}')

    def get_view(self):
        """Return a reference to the application's main view object."""
        return self._ui

    def move_node(self, node, targetNode):
        """Move a node to another position.
        
        Positional arguments:
            node: str - ID of the node to move.
            targetNode: str -- ID of the new parent/predecessor of the node.
        """
        if (node.startswith(ARC_POINT_PREFIX) and targetNode.startswith(ARC_PREFIX)):
            self._ui.tv.open_children(targetNode)
        self._ui.tv.skipUpdate = True
        self._mdl.move_node(node, targetNode)

    def new_project(self, event=None):
        """Create a storyliner project instance."""
        if self._mdl.prjFile is not None:
            self.close_project()
        self._mdl.new_project(self._ui.tv.tree)
        self._ui.show_path(_('Unnamed'))
        # setting the path bar
        self.enable_menu()
        self.show_status()
        # setting the status bar
        self._ui.tv.go_to_node(AC_ROOT)
        self.refresh_views()
        self.save_project()
        return 'break'

    def on_quit(self, event=None):
        """Save changes and keyword arguments before exiting the program."""
        try:
            if self._mdl.prjFile is not None:
                self.close_project()

            # Save windows size and position.
            if self._ui._propWinDetached:
                prefs['prop_win_geometry'] = self._propertiesWindow.winfo_geometry()
            self._ui.tv.on_quit()
            prefs['root_geometry'] = self._ui.root.winfo_geometry()
            self._ui.root.quit()
        except Error as ex:
            self._ui.show_error(str(ex), title='ERROR: Unhandled exception on exit')
            self._ui.root.quit()
        return 'break'

    def open_installationFolder(self, event=None):
        """Open the installation folder with the OS file manager."""
        installDir = os.path.dirname(sys.argv[0])
        try:
            os.startfile(norm_path(installDir))
            # Windows
        except:
            try:
                os.system('xdg-open "%s"' % norm_path(installDir))
                # Linux
            except:
                try:
                    os.system('open "%s"' % norm_path(installDir))
                    # Mac
                except:
                    pass
        return 'break'

    def open_project(self, event=None, filePath='', doNotSave=False):
        """Create a storyliner project instance and read the file.
        
        Optional arguments:
            filePath: str -- The new project's file name.
        
        If no file name is given, a file picker is opened.
        Display project title, description and status.
        Return True on success, otherwise return False.
        """
        self._ui.restore_status()
        filePath = self.select_project(filePath)
        if not filePath:
            return False

        prefs['last_open'] = filePath

        if self._mdl.prjFile is not None:
            self.close_project(doNotSave=doNotSave)
        try:
            self._mdl.open_project(filePath)
        except Error as ex:
            self.close_project(doNotSave=doNotSave)
            self._ui.set_status(f'!{str(ex)}')
            return False

        self._ui.show_path(f'{norm_path(self._mdl.prjFile.filePath)}')
        self.enable_menu()

        self.refresh_views()
        self._ui.show_path(_('{0} (last saved on {1})').format(norm_path(self._mdl.prjFile.filePath), self._mdl.prjFile.fileDate))
        self.show_status()
        self._ui.tv.show_branch(AC_ROOT)
        return True

    def open_project_folder(self, event=None):
        """Open the project folder with the OS file manager."""
        if (self._mdl and self._mdl.prjFile.filePath is not None) or self.save_project():
            projectDir, __ = os.path.split(self._mdl.prjFile.filePath)
            try:
                os.startfile(norm_path(projectDir))
                # Windows
            except:
                try:
                    os.system('xdg-open "%s"' % norm_path(projectDir))
                    # Linux
                except:
                    try:
                        os.system('open "%s"' % norm_path(projectDir))
                        # Mac
                    except:
                        pass
        return 'break'

    def refresh(self):
        """Callback function to report model element modifications."""
        self.show_status()

    def refresh_views(self, event=None):
        """Update all registered views."""
        self._ui.propertiesView.apply_changes()
        self._ui.refresh()
        return 'break'

    def reload_project(self, event=None):
        """Discard changes and reload the project."""
        if self._mdl.prjFile is None:
            return 'break'

        if self._mdl.isModified and not self._ui.ask_yes_no(_('Discard changes and reload the project?')):
            return 'break'

        if self._mdl.prjFile.has_changed_on_disk() and not self._ui.ask_yes_no(_('File has changed on disk. Reload anyway?')):
            return 'break'

        # this is to avoid saving when closing the project
        if self.open_project(filePath=self._mdl.prjFile.filePath, doNotSave=True):
            # includes closing
            self._ui.set_status(_('Project successfully restored from disk.'))
        return 'break'

    def reset_tree(self, event=None):
        """Clear the displayed tree, and reset the browsing history."""
        self._mdl.reset_tree()

    def restore_backup(self, event=None):
        """Discard changes and restore the latest backup file."""
        if self._mdl.prjFile is None:
            return 'break'

        latestBackup = f'{self._mdl.prjFile.filePath}.bak'
        if not os.path.isfile(latestBackup):
            self._ui.set_status(f'!{_("No backup available")}')
            return 'break'

        if self._mdl.isModified:
            if not self._ui.ask_yes_no(_('Discard changes and restore the latest backup?')):
                return 'break'

        elif not self._ui.ask_yes_no(_('Restore the latest backup?')):
            return 'break'

        try:
            os.replace(latestBackup, self._mdl.prjFile.filePath)
        except Exception as ex:
            self._ui.set_status(str(ex))
        else:
            if self.open_project(filePath=self._mdl.prjFile.filePath, doNotSave=True):
                # Includes closing
                self._ui.set_status(_('Latest backup successfully restored.'))
        return 'break'

    def save_as(self, event=None):
        """Rename the project file and save it to disk.
        
        Return True on success, otherwise return False.
        """
        if self._mdl.prjFile is None:
            return False

        if prefs['last_open']:
            startDir, __ = os.path.split(prefs['last_open'])
        else:
            startDir = '.'
        fileName = filedialog.asksaveasfilename(
            filetypes=self._fileTypes,
            defaultextension=self._fileTypes[0][1],
            initialdir=startDir,
            )
        if fileName:
            if self._mdl.prjFile is not None:
                self._ui.propertiesView.apply_changes()
                try:
                    self._mdl.save_project(fileName)
                except Error as ex:
                    self._ui.set_status(f'!{str(ex)}')
                else:
                    self._ui.show_path(f'{norm_path(self._mdl.prjFile.filePath)} ({_("last saved on")} {self._mdl.prjFile.fileDate})')
                    self._ui.restore_status()
                    prefs['last_open'] = self._mdl.prjFile.filePath
                    return True

        return False

    def save_project(self, event=None):
        """Save the storyliner project to disk.
        
        Return True on success, otherwise return False.
        """
        if self._mdl.prjFile is None:
            return False

        if self._mdl.prjFile.filePath is None:
            return self.save_as()

        if self._mdl.prjFile.has_changed_on_disk() and not self._ui.ask_yes_no(_('File has changed on disk. Save anyway?')):
            return False

        self._ui.propertiesView.apply_changes()
        try:
            self._mdl.save_project()
        except Error as ex:
            self._ui.set_status(f'!{str(ex)}')
            return False

        self._ui.show_path(f'{norm_path(self._mdl.prjFile.filePath)} ({_("last saved on")} {self._mdl.prjFile.fileDate})')
        self._ui.restore_status()
        prefs['last_open'] = self._mdl.prjFile.filePath
        return True

    def select_project(self, fileName):
        """Return a project file path.

        Positional arguments:
            fileName: str -- project file path.
            
        Optional arguments:
            fileTypes -- list of tuples for file selection (display text, extension).

        Priority:
        1. use file name argument
        2. open file select dialog

        On error, return an empty string.
        """
        initDir = os.path.dirname(prefs.get('last_open', ''))
        if not initDir:
            initDir = './'
        if not fileName or not os.path.isfile(fileName):
            fileName = filedialog.askopenfilename(
                filetypes=self._fileTypes,
                defaultextension=SlWorkFile.EXTENSION,
                initialdir=initDir
                )
        if not fileName:
            return ''

        return fileName

    def show_report(self, suffix):
        """Create HTML report for the web browser.
        
        Positional arguments:
            suffix: str -- the HTML file name suffix, indicating the report type.        
        """
        if self._mdl.prjFile.filePath is None:
            return False

        self._ui.restore_status()
        self._ui.propertiesView.apply_changes()
        reporter = SlHtmlReporter()
        try:
            reporter.run(self._mdl.prjFile, suffix, tempdir=self.tempDir)
        except Error as ex:
            self._ui.set_status(f'!{str(ex)}')

    def show_status(self, message=None):
        """Display project statistics at the status bar.
        
        Optional arguments:
            message: str -- Message to be displayed instead of the statistics.
        """
        self._ui.show_status(message)

    def _view_new_element(self, newNode):
        """View the element with ID newNode.
        
        - Open the properties window for the new element.
        - Show and select it in the tree view.
        - Prepare the current element's title entry for manual input.
        The order is mandatory for smooth operation.
        """
        if newNode:
            self._ui.tv.go_to_node(newNode)
            self._ui.propertiesView.show_properties(newNode)
            self._ui.propertiesView.focus_title()
