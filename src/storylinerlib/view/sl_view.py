"""Provide a tkinter GUI framework for storyliner.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
"""
import sys
from tkinter import messagebox
from tkinter import ttk
import webbrowser

from storylinerlib.storyliner_globals import prefs
from storylinerlib.view.icons import Icons
from storylinerlib.view.properties_window.properties_viewer import PropertiesViewer
from storylinerlib.view.toolbar import Toolbar
from storylinerlib.view.tree_window.tree_viewer import TreeViewer
from storylinerlib.view.view_options_window import ViewOptionsWindow
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import CHARACTER_PREFIX
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import BOOK_PREFIX
from storylinerlib.storyliner_globals import CHARACTERS_SUFFIX
from storylinerlib.storyliner_globals import CHARLIST_SUFFIX
from storylinerlib.storyliner_globals import BOOKS_SUFFIX
from storylinerlib.storyliner_globals import BOOKLIST_SUFFIX
from storylinerlib.storyliner_globals import PLOT_SUFFIX
from storylinerlib.storyliner_globals import PLOTLIST_SUFFIX

from storylinerlib.storyliner_globals import _
from novxlib.ui.set_icon_tk import set_icon
import tkinter as tk


class SlView:
    """Main view of the tkinter GUI framework for storyliner."""
    _HELP_URL = 'https://peter88213.github.io/storyliner/help/help'
    _KEY_ADD_CHILD = ('<Control-Alt-n>', 'Ctrl-Alt-N')
    _KEY_ADD_ELEMENT = ('<Control-n>', 'Ctrl-N')
    _KEY_ADD_PARENT = ('<Control-Alt-Shift-N>', 'Ctrl-Alt-Shift-N')
    _KEY_CHAPTER_LEVEL = ('<Control-Alt-c>', 'Ctrl-Alt-C')
    _KEY_DETACH_PROPERTIES = ('<Control-Alt-d>', 'Ctrl-Alt-D')
    _KEY_FOLDER = ('<Control-p>', 'Ctrl-P')
    _KEY_LOCK_PROJECT = ('<Control-l>', 'Ctrl-L')
    _KEY_OPEN_PROJECT = ('<Control-o>', 'Ctrl-O')
    _KEY_QUIT_PROGRAM = ('<Control-q>', 'Ctrl-Q')
    _KEY_REFRESH_TREE = ('<F5>', 'F5')
    _KEY_RELOAD_PROJECT = ('<Control-r>', 'Ctrl-R')
    _KEY_RESTORE_BACKUP = ('<Control-b>', 'Ctrl-B')
    _KEY_RESTORE_STATUS = ('<Escape>', 'Esc')
    _KEY_SAVE_AS = ('<Control-S>', 'Ctrl-Shift-S')
    _KEY_SAVE_PROJECT = ('<Control-s>', 'Ctrl-S')
    _KEY_TOGGLE_PROPERTIES = ('<Control-Alt-t>', 'Ctrl-Alt-T')
    _KEY_TOGGLE_VIEWER = ('<Control-t>', 'Ctrl-T')
    _KEY_UNLOCK_PROJECT = ('<Control-u>', 'Ctrl-U')

    def __init__(self, model, controller, title):
        """Set up the application's user interface.
    
        Positional arguments:
            title: str -- Application title to be displayed at the window frame.
         
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
        self._mdl = model
        self._ctrl = controller
        self._mdl.register_client(self)
        self.views = []

        #--- Create the tk root window and set the size.
        self.title = title
        self._statusText = ''
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self._ctrl.on_quit)
        self.root.title(title)
        if prefs.get('root_geometry', None):
            self.root.geometry(prefs['root_geometry'])
        set_icon(self.root, icon='sLogo32')

        #---  Add en empty main menu to the root window.
        self.mainMenu = tk.Menu(self.root)
        self.root.config(menu=self.mainMenu)

        #--- Create the main window.
        self.mainWindow = tk.Frame()
        self.mainWindow.pack(expand=True, fill='both')

        #--- Create the status bar.
        self.statusBar = tk.Label(self.root, text='', anchor='w', padx=5, pady=2)
        self.statusBar.pack(expand=False, fill='both')
        self.statusBar.bind('<Button-1>', self.restore_status)
        self.infoWhatText = ''
        self.infoHowText = ''

        #--- Create the path bar.
        self.pathBar = tk.Label(self.root, text='', anchor='w', padx=5, pady=3)
        self.pathBar.pack(expand=False, fill='both')

        #--- Initialize GUI theme.
        self.guiStyle = ttk.Style()

        #--- Initalize icons.
        self.icons = Icons()

        #--- Build the GUI frames.

        # Create an application window with three frames.
        self.appWindow = ttk.Frame(self.mainWindow)
        self.appWindow.pack(expand=True, fill='both')

        #--- left frame (intended for the tree).
        self.leftFrame = ttk.Frame(self.appWindow)
        self.leftFrame.pack(side='left', expand=True, fill='both')

        #--- Create a story tree window in the left frame.
        self.tv = TreeViewer(self.leftFrame, self._mdl, self, self._ctrl, prefs)
        self.views.append(self.tv)
        self.tv.pack(expand=True, fill='both')

        #--- Middle frame (intended for the content viewer).
        self.middleFrame = ttk.Frame(self.appWindow, width=prefs['middle_frame_width'])
        self.middleFrame.pack_propagate(0)

        #--- Right frame for for the element properties view.
        self.rightFrame = ttk.Frame(self.appWindow, width=prefs['right_frame_width'])
        self.rightFrame.pack_propagate(0)
        if prefs['show_properties']:
            self.rightFrame.pack(expand=True, fill='both')

        #--- Create an element properties view in the right frame.
        self.propertiesView = PropertiesViewer(self.rightFrame, self._mdl, self, self._ctrl)
        self.propertiesView.pack(expand=True, fill='both')
        self._propWinDetached = False
        if prefs['detach_prop_win']:
            self.detach_properties_frame()
        self.views.append(self.propertiesView)

        #--- Add commands and submenus to the main menu.
        self._build_menu()

        #--- Add a toolbar.
        self._toolbar = Toolbar(self, self._ctrl)
        self.views.append(self._toolbar)

        #--- tk root event bindings.
        self._bind_events()

    def ask_yes_no(self, text, title=None):
        """Query yes or no with a pop-up box.
        
        Positional arguments:
            text -- question to be asked in the pop-up box. 
            
        Optional arguments:
            title -- title to be displayed on the window frame.            
        """
        if title is None:
            title = self.title
        return messagebox.askyesno(title, text)

    def detach_properties_frame(self, event=None):
        """View the properties in its own window."""
        self.propertiesView.apply_changes()
        if self._propWinDetached:
            return

        if self.rightFrame.winfo_manager():
            self.rightFrame.pack_forget()
        self._propertiesWindow = tk.Toplevel()
        self._propertiesWindow.geometry(prefs['prop_win_geometry'])
        set_icon(self._propertiesWindow, icon='pLogo32', default=False)
        self.propertiesView.pack_forget()
        self.propertiesView = PropertiesViewer(self._propertiesWindow, self._mdl, self, self._ctrl)
        self.propertiesView.pack(expand=True, fill='both')
        self._propertiesWindow.protocol("WM_DELETE_WINDOW", self.dock_properties_frame)
        prefs['detach_prop_win'] = True
        self._propWinDetached = True
        try:
            self.propertiesView.show_properties(self.tv.tree.selection()[0])
        except IndexError:
            pass
        return 'break'

    def disable_menu(self):
        """Disable menu entries when no project is open."""
        self.fileMenu.entryconfig(_('Close'), state='disabled')
        self.mainMenu.entryconfig(_('Characters'), state='disabled')
        self.mainMenu.entryconfig(_('Books'), state='disabled')
        self.mainMenu.entryconfig(_('Arc'), state='disabled')
        self.mainMenu.entryconfig(_('Turning point'), state='disabled')
        self.fileMenu.entryconfig(_('Reload'), state='disabled')
        self.fileMenu.entryconfig(_('Restore backup'), state='disabled')
        self.fileMenu.entryconfig(_('Refresh Tree'), state='disabled')
        self.fileMenu.entryconfig(_('Open Project folder'), state='disabled')
        self.fileMenu.entryconfig(_('Copy style sheet'), state='disabled')
        self.fileMenu.entryconfig(_('Save'), state='disabled')
        self.fileMenu.entryconfig(_('Save as...'), state='disabled')
        self.viewMenu.entryconfig(_('Expand selected'), state='disabled')
        self.viewMenu.entryconfig(_('Collapse selected'), state='disabled')
        self.viewMenu.entryconfig(_('Expand all'), state='disabled')
        self.viewMenu.entryconfig(_('Collapse all'), state='disabled')
        self.viewMenu.entryconfig(_('Show Characters'), state='disabled')
        self.viewMenu.entryconfig(_('Show Books'), state='disabled')
        self.viewMenu.entryconfig(_('Show Arcs'), state='disabled')
        for view in self.views:
            try:
                view.disable_menu()
            except AttributeError:
                pass

    def dock_properties_frame(self, event=None):
        """Dock the properties window at the right pane, if detached."""
        self.propertiesView.apply_changes()
        if not self._propWinDetached:
            return

        if not self.rightFrame.winfo_manager():
            self.rightFrame.pack(side='left', expand=False, fill='both')
        self.propertiesView = PropertiesViewer(self.rightFrame, self._mdl, self, self._ctrl)
        self.propertiesView.pack(expand=True, fill='both')
        prefs['prop_win_geometry'] = self._propertiesWindow.winfo_geometry()
        self._propertiesWindow.destroy()
        prefs['show_properties'] = True
        prefs['detach_prop_win'] = False
        self._propWinDetached = False
        self.root.lift()
        try:
            self.propertiesView.show_properties(self.tv.tree.selection()[0])
        except IndexError:
            pass
        return 'break'

    def enable_menu(self):
        """Enable menu entries when a project is open."""
        self.fileMenu.entryconfig(_('Close'), state='normal')
        self.mainMenu.entryconfig(_('Characters'), state='normal')
        self.mainMenu.entryconfig(_('Books'), state='normal')
        self.mainMenu.entryconfig(_('Arc'), state='normal')
        self.mainMenu.entryconfig(_('Turning point'), state='normal')
        self.fileMenu.entryconfig(_('Reload'), state='normal')
        self.fileMenu.entryconfig(_('Restore backup'), state='normal')
        self.fileMenu.entryconfig(_('Refresh Tree'), state='normal')
        self.fileMenu.entryconfig(_('Open Project folder'), state='normal')
        self.fileMenu.entryconfig(_('Copy style sheet'), state='normal')
        self.fileMenu.entryconfig(_('Save'), state='normal')
        self.fileMenu.entryconfig(_('Save as...'), state='normal')
        self.viewMenu.entryconfig(_('Expand selected'), state='normal')
        self.viewMenu.entryconfig(_('Collapse selected'), state='normal')
        self.viewMenu.entryconfig(_('Expand all'), state='normal')
        self.viewMenu.entryconfig(_('Collapse all'), state='normal')
        self.viewMenu.entryconfig(_('Show Characters'), state='normal')
        self.viewMenu.entryconfig(_('Show Books'), state='normal')
        self.viewMenu.entryconfig(_('Show Arcs'), state='normal')
        for view in self.views:
            try:
                view.enable_menu()
            except AttributeError:
                pass

    def on_change_selection(self, nodeId):
        """Event handler for element selection.
        
        Show the properties of the selected element.
        """
        self.propertiesView.show_properties(nodeId)

    def restore_status(self, event=None):
        """Overwrite error message with the status before."""
        self.show_status(self._statusText)
        self.statusBar.bind('<Button-1>', self.restore_status)

    def set_info(self, message):
        """This is a stub, just for compatibility with several converters."""
        pass

    def set_status(self, message, colors=None):
        """SDisplay a message at the status bar.
        
        Positional arguments:
            message -- message to be displayed. 
            
        Optional arguments:
            colors: tuple -- (background color, foreground color).

        Default status bar color is red if the message starts with "!", otherwise green.
        """
        if message is not None:
            try:
                self.statusBar.config(bg=colors[0])
                self.statusBar.config(fg=colors[1])
                self.infoHowText = message
            except:
                if message.startswith('!'):
                    self.statusBar.config(bg='red')
                    self.statusBar.config(fg='white')
                    self.infoHowText = message.split('!', maxsplit=1)[1].strip()
                else:
                    self.statusBar.config(bg='green')
                    self.statusBar.config(fg='white')
                    self.infoHowText = message
            self.statusBar.config(text=self.infoHowText)

    def set_title(self):
        """Set the main window title. 
        
        'Document title by author - application'
        """
        if self._mdl.story is None:
            return

        if self._mdl.story.title:
            titleView = self._mdl.story.title
        else:
            titleView = _('Untitled project')
        self.root.title(f'{titleView} - {self.title}')

    def show_error(self, message, title=None):
        """Display an error message box.
        
        Optional arguments:
            title -- title to be displayed on the window frame.
        """
        if title is None:
            title = self.title
        messagebox.showerror(title, message)

    def show_info(self, message, title=None):
        """Display an informational message box.
        
        Optional arguments:
            title -- title to be displayed on the window frame.
        """
        if title is None:
            title = self.title
        messagebox.showinfo(title, message)

    def show_warning(self, message, title=None):
        """Display a warning message box.
        
        Optional arguments:
            title -- title to be displayed on the window frame.
        """
        if title is None:
            title = self.title
        messagebox.showwarning(title, message)

    def show_path(self, message):
        """Put text on the path bar."""
        self.pathBar.config(text=message)

    def show_status(self, message=''):
        """Display project statistics at the status bar.
        
        Optional arguments:
            message: str -- Message to be displayed instead of the statistics.
        """
        self._statusText = message
        self.statusBar.config(bg=self.root.cget('background'))
        self.statusBar.config(fg='black')
        self.statusBar.config(text=message)

    def start(self):
        """Start the Tk main loop.
        
        Note: This can not be done in the constructor method.
        """
        self.root.mainloop()

    def toggle_properties_view(self, event=None):
        """Show/hide the element properties frame."""
        if self.rightFrame.winfo_manager():
            self.propertiesView.apply_changes()
            self.rightFrame.pack_forget()
            prefs['show_properties'] = False
        elif not self._propWinDetached:
            self.rightFrame.pack(side='left', expand=False, fill='both')
            prefs['show_properties'] = True
        return 'break'

    def toggle_properties_window(self, event=None):
        """Detach/dock the element properties frame."""
        if self._propWinDetached:
            self.dock_properties_frame()
        else:
            self.detach_properties_frame()
        return 'break'

    def refresh(self):
        """Update children."""
        if self._mdl.isModified:
            self.pathBar.config(bg=prefs['color_modified_bg'])
            self.pathBar.config(fg=prefs['color_modified_fg'])
        else:
            self.pathBar.config(bg=self.root.cget('background'))
            self.pathBar.config(fg='black')
        for view in self.views:
            try:
                view.refresh()
            except AttributeError:
                pass
        self.set_title()

    def _bind_events(self):
        self.root.bind(self._KEY_RESTORE_STATUS[0], self.restore_status)
        self.root.bind(self._KEY_OPEN_PROJECT[0], self._ctrl.open_project)

        self.root.bind(self._KEY_RELOAD_PROJECT[0], self._ctrl.reload_project)
        self.root.bind(self._KEY_RESTORE_BACKUP[0], self._ctrl.restore_backup)
        self.root.bind(self._KEY_FOLDER[0], self._ctrl.open_project_folder)
        self.root.bind(self._KEY_REFRESH_TREE[0], self._ctrl.refresh_views)
        self.root.bind(self._KEY_SAVE_PROJECT[0], self._ctrl.save_project)
        self.root.bind(self._KEY_SAVE_AS[0], self._ctrl.save_as)
        self.root.bind(self._KEY_TOGGLE_PROPERTIES[0], self.toggle_properties_view)
        self.root.bind(self._KEY_DETACH_PROPERTIES[0], self.toggle_properties_window)
        self.root.bind(self._KEY_ADD_ELEMENT[0], self._ctrl.add_element)
        self.root.bind(self._KEY_ADD_CHILD[0], self._ctrl.add_child)
        self.root.bind(self._KEY_ADD_PARENT[0], self._ctrl.add_parent)
        if sys.platform == 'win32':
            self.root.bind('<4>', self.tv.go_back)
            self.root.bind('<5>', self.tv.go_forward)
        else:
            self.root.bind(self._KEY_QUIT_PROGRAM[0], self._ctrl.on_quit)

    def _build_menu(self):
        """Add commands and submenus to the main menu."""

        # Files
        self.fileMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('File'), menu=self.fileMenu)
        self.fileMenu.add_command(label=_('New'), command=self._ctrl.new_project)
        self.fileMenu.add_command(label=_('Open...'), accelerator=self._KEY_OPEN_PROJECT[1], command=self._ctrl.open_project)
        self.fileMenu.add_command(label=_('Reload'), accelerator=self._KEY_RELOAD_PROJECT[1], command=self._ctrl.reload_project)
        self.fileMenu.add_command(label=_('Restore backup'), accelerator=self._KEY_RESTORE_BACKUP[1], command=self._ctrl.restore_backup)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=_('Refresh Tree'), accelerator=self._KEY_REFRESH_TREE[1], command=self._ctrl.refresh_views)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=_('Open Project folder'), accelerator=self._KEY_FOLDER[1], command=self._ctrl.open_project_folder)
        self.fileMenu.add_command(label=_('Copy style sheet'), command=self._ctrl.copy_css)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=_('Save'), accelerator=self._KEY_SAVE_PROJECT[1], command=self._ctrl.save_project)
        self.fileMenu.add_command(label=_('Save as...'), accelerator=self._KEY_SAVE_AS[1], command=self._ctrl.save_as)
        self.fileMenu.add_command(label=_('Close'), command=self._ctrl.close_project)
        if sys.platform == 'win32':
            self.fileMenu.add_command(label=_('Exit'), accelerator='Alt-F4', command=self._ctrl.on_quit)
        else:
            self.fileMenu.add_command(label=_('Quit'), accelerator=self._KEY_QUIT_PROGRAM[1], command=self._ctrl.on_quit)

        # View
        self.viewMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('View'), menu=self.viewMenu)
        self.viewMenu.add_command(label=_('Expand selected'), command=lambda: self.tv.open_children(self.tv.tree.selection()[0]))
        self.viewMenu.add_command(label=_('Collapse selected'), command=lambda: self.tv.close_children(self.tv.tree.selection()[0]))
        self.viewMenu.add_command(label=_('Expand all'), command=lambda: self.tv.open_children(''))
        self.viewMenu.add_command(label=_('Collapse all'), command=lambda: self.tv.close_children(''))
        self.viewMenu.add_separator()
        self.viewMenu.add_command(label=_('Show Books'), command=lambda: self.tv.show_branch(BK_ROOT))
        self.viewMenu.add_command(label=_('Show Characters'), command=lambda: self.tv.show_branch(CR_ROOT))
        self.viewMenu.add_command(label=_('Show Arcs'), command=lambda: self.tv.show_branch(AC_ROOT))
        self.viewMenu.add_separator()
        self.viewMenu.add_command(label=_('Toggle Properties'), accelerator=self._KEY_TOGGLE_PROPERTIES[1], command=self.toggle_properties_view)
        self.viewMenu.add_command(label=_('Detach/Dock Properties'), accelerator=self._KEY_DETACH_PROPERTIES[1], command=self.toggle_properties_window)
        self.viewMenu.add_separator()
        self.viewMenu.add_command(label=_('Options'), command=self._view_options)

        # Character
        self.characterMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Characters'), menu=self.characterMenu)
        self.characterMenu.add_command(label=_('Add'), command=self._ctrl.add_character)
        self.characterMenu.add_separator()
        self.characterMenu.add_command(label=_('Export character descriptions'), command=lambda: self._ctrl.export_document(CHARACTERS_SUFFIX))
        self.characterMenu.add_command(label=_('Export character list (spreadsheet)'), command=lambda: self._ctrl.export_document(CHARLIST_SUFFIX))
        self.characterMenu.add_command(label=_('Show list'), command=lambda: self._ctrl.show_report(CHARLIST_SUFFIX))

        # Book
        self.bookMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Books'), menu=self.bookMenu)
        self.bookMenu.add_command(label=_('Add'), command=self._ctrl.add_book)
        self.bookMenu.add_separator()
        self.bookMenu.add_command(label=_('Export book descriptions'), command=lambda: self._ctrl.export_document(BOOKS_SUFFIX))
        self.bookMenu.add_command(label=_('Export book list (spreadsheet)'), command=lambda: self._ctrl.export_document(BOOKLIST_SUFFIX))
        self.bookMenu.add_command(label=_('Show list'), command=lambda: self._ctrl.show_report(BOOKLIST_SUFFIX))

        # "Arc" menu.
        self.plotMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Arc'), menu=self.plotMenu)
        self.plotMenu.add_command(label=_('Add'), command=self._ctrl.add_arc)
        self.plotMenu.add_separator()
        self.plotMenu.add_command(label=_('Export plot description'), command=lambda: self._ctrl.export_document(PLOT_SUFFIX, lock=False))
        self.plotMenu.add_command(label=_('Export plot list (spreadsheet)'), command=lambda: self._ctrl.export_document(PLOTLIST_SUFFIX, lock=False))
        self.plotMenu.add_command(label=_('Show Plot list'), command=lambda: self._ctrl.show_report(PLOTLIST_SUFFIX))

        # "Turning point" menu.
        self.pointMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Turning point'), menu=self.pointMenu)
        self.pointMenu.add_command(label=_('Add'), command=self._ctrl.add_turning_point)

        # "Tools" menu.
        self.toolsMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Tools'), menu=self.toolsMenu)
        self.toolsMenu.add_command(label=_('Open installation folder'), command=self._ctrl.open_installationFolder)
        self.toolsMenu.add_separator()

        # "Help" menu.
        self.helpMenu = tk.Menu(self.mainMenu, tearoff=0)
        self.mainMenu.add_cascade(label=_('Help'), menu=self.helpMenu)
        self.helpMenu.add_command(label=_('Online help'), command=lambda: webbrowser.open(self._HELP_URL))

    def _view_options(self, event=None):
        """Open a toplevel window to edit the view options."""
        offset = 300
        __, x, y = self.root.geometry().split('+')
        windowGeometry = f'+{int(x)+offset}+{int(y)+offset}'
        ViewOptionsWindow(windowGeometry, self)
        return 'break'

