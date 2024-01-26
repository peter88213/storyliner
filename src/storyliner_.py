#!/usr/bin/python3
"""A novel and series plotting application. 

Version @release
Requires Python 3.6+
Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/storyliner
License: GNU GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import os
from pathlib import Path
import sys

from storylinerlib.configuration.sl_configuration import SlConfiguration
from storylinerlib.controller.sl_controller import SlController
from storylinerlib.storyliner_globals import prefs
from novxlib.config.configuration import Configuration

APPNAME = 'storyliner'
SETTINGS = dict(
    last_open='',
    root_geometry='1200x800',
    gui_theme='',
    button_context_menu='<Button-3>',
    middle_frame_width=400,
    right_frame_width=350,
    index_card_height=13,
    gco_height=4,
    prop_win_geometry='299x716+260+260',
    color_arc='maroon',
    color_point='black',
    color_book='green',
    color_character='blue',
    color_modified_bg='goldenrod1',
    color_modified_fg='maroon',
    color_text_bg='white',
    color_text_fg='black',
    color_notes_bg='lemon chiffon',
    color_notes_fg='black',
    coloring_mode='',
    title_width=400,
    bk_width=400,
    column_order='bk'
    )
OPTIONS = dict(
    show_properties=True,
    detach_prop_win=False,
    discard_tmp_docs=True,
    large_icons=False,
    )


def main():
    #--- Set up the directories for configuration and temporary files.
    try:
        homeDir = str(Path.home()).replace('\\', '/')
        installDir = f'{homeDir}/.storyliner'
    except:
        installDir = '.'
    os.makedirs(installDir, exist_ok=True)
    configDir = f'{installDir}/config'
    os.makedirs(configDir, exist_ok=True)
    tempDir = f'{installDir}/temp'
    os.makedirs(tempDir, exist_ok=True)

    #--- Load configuration.
    iniFile = f'{configDir}/{APPNAME}.ini'
    configuration = Configuration(SETTINGS, OPTIONS)
    configuration.read(iniFile)
    prefs.update(configuration.settings)
    prefs.update(configuration.options)

    #--- Instantiate the app object.
    app = SlController('storyliner @release', tempDir)
    ui = app.get_view()

    #--- Launchers for opening linked non-standard filetypes.
    launcherConfig = SlConfiguration()
    launcherConfig.read(f'{configDir}/launchers.ini')
    app.launchers = launcherConfig.settings

    #--- Load a project, if specified.
    try:
        sourcePath = sys.argv[1]
    except:
        sourcePath = ''
    if not sourcePath or not os.path.isfile(sourcePath):
        sourcePath = prefs['last_open']
    if sourcePath and os.path.isfile(sourcePath):
        app.open_project(filePath=sourcePath)

    #--- Run the GUI application.
    ui.start()

    #--- Save project specific configuration
    for keyword in prefs:
        if keyword in configuration.options:
            configuration.options[keyword] = prefs[keyword]
        elif keyword in configuration.settings:
            configuration.settings[keyword] = prefs[keyword]
    configuration.write(iniFile)

    #--- Delete the temporary files.
    # Note: Do not remove the temp directory itself,
    # because other storyliner instances might be running and using it.
    # However, temporary files of other running instances are deleted
    # if not protected e.g. by a read-only flag.
    for file in os.scandir(tempDir):
        try:
            os.remove(file)
        except:
            pass


if __name__ == '__main__':
    main()
