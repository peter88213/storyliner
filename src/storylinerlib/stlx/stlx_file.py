"""Provide a class for novx file import and export.

Copyright (c) 2024 Peter Triesberger
For further information see https://github.com/peter88213/novxlib
License: GNU LGPLv3 (https://www.gnu.org/licenses/lgpl-3.0.en.html)
"""
import os

from novxlib.file.file import File
from novxlib.xml.etree_tools import *
from novxlib.xml.xml_indent import indent
from storylinerlib.model.arc import Arc
from storylinerlib.model.book import Book
from storylinerlib.model.character import Character
from storylinerlib.model.turning_point import TurningPoint
from storylinerlib.storyliner_globals import AC_ROOT
from storylinerlib.storyliner_globals import BK_ROOT
from storylinerlib.storyliner_globals import CR_ROOT
from storylinerlib.storyliner_globals import Error
from storylinerlib.storyliner_globals import _
from storylinerlib.storyliner_globals import list_to_string
from storylinerlib.storyliner_globals import norm_path
from storylinerlib.storyliner_globals import string_to_list
import xml.etree.ElementTree as ET


class StlxFile(File):
    """stlx file representation.

    Public instance variables:
        tree -- xml element tree of the storyliner project
    
    Public properties:
        fileDate: str -- ISO-formatted file date/time (YYYY-MM-DD hh:mm:ss).
    """
    DESCRIPTION = _('storyliner project')
    EXTENSION = '.stlx'

    MAJOR_VERSION = 1
    MINOR_VERSION = 0
    # DTD version.

    XML_HEADER = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE novx SYSTEM "stlx_1_0.dtd">
<?xml-stylesheet href="stlx.css" type="text/css"?>
'''

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath: str -- path to the novx file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.on_element_change = None
        self.xmlTree = None

    def read(self):
        """Parse the storyliner xml file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        self.xmlTree = ET.parse(self.filePath)
        xmlRoot = self.xmlTree.getroot()
        try:
            majorVersionStr, minorVersionStr = xmlRoot.attrib['version'].split('.')
            majorVersion = int(majorVersionStr)
            minorVersion = int(minorVersionStr)
        except:
            raise Error(f'{_("No valid version found in file")}: "{norm_path(self.filePath)}".')

        if majorVersion > self.MAJOR_VERSION:
            raise Error(_('The project "{}" was created with a newer storyliner version.').format(norm_path(self.filePath)))

        elif majorVersion < self.MAJOR_VERSION:
            raise Error(_('The project "{}" was created with an outdated storyliner version.').format(norm_path(self.filePath)))

        elif minorVersion > self.MINOR_VERSION:
            raise Error(_('The project "{}" was created with a newer storyliner version.').format(norm_path(self.filePath)))

        try:
            locale = xmlRoot.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            self.story.languageCode, self.story.countryCode = locale.split('-')
        except:
            pass
        self.story.tree.reset()
        self._read_books(xmlRoot)
        self._read_arcs(xmlRoot)
        self._read_characters(xmlRoot)

    def write(self):
        """Write instance variables to the novx xml file.
        
        Update the word count log, write the file, and update the timestamp.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        attrib = {'version':f'{self.MAJOR_VERSION}.{self.MINOR_VERSION}'}
        xmlRoot = ET.Element('novx', attrib=attrib)
        self._build_element_tree(xmlRoot)
        indent(xmlRoot)
        self.xmlTree = ET.ElementTree(xmlRoot)
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_arc_branch(self, xmlArcs, prjArc, acId):
        xmlArc = ET.SubElement(xmlArcs, 'ARC', attrib={'id':acId})
        if prjArc.title:
            ET.SubElement(xmlArc, 'Title').text = prjArc.title
        if prjArc.shortName:
            ET.SubElement(xmlArc, 'ShortName').text = prjArc.shortName
        if prjArc.desc:
            xmlArc.append(text_to_xml_element('Desc', prjArc.desc))

        #--- Turning points.
        for tpId in self.story.tree.get_children(acId):
            xmlPoint = ET.SubElement(xmlArc, 'POINT', attrib={'id':tpId})
            self._build_turningPoint_branch(xmlPoint, self.story.turningPoints[tpId])

        return xmlArc

    def _build_turningPoint_branch(self, xmlPoint, prjTurningPoint):
        if prjTurningPoint.title:
            ET.SubElement(xmlPoint, 'Title').text = prjTurningPoint.title
        if prjTurningPoint.desc:
            xmlPoint.append(text_to_xml_element('Desc', prjTurningPoint.desc))
        if prjTurningPoint.notes:
            xmlPoint.append(text_to_xml_element('Notes', prjTurningPoint.notes))
        try:
            position = str(prjTurningPoint.position)
        except:
            position = '0'
        xmlPoint.set('position', position)

        #--- References.
        if prjTurningPoint.books:
            bookIds = list_to_string(prjTurningPoint.books, divider=' ')
            ET.SubElement(xmlPoint, 'Books', attrib={'ids': bookIds})

    def _build_character_branch(self, xmlCrt, prjCrt):
        if prjCrt.title:
            ET.SubElement(xmlCrt, 'Title').text = prjCrt.title
        if prjCrt.fullName:
            ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName
        if prjCrt.desc:
            xmlCrt.append(text_to_xml_element('Desc', prjCrt.desc))
        if prjCrt.role:
            xmlCrt.append(text_to_xml_element('Role', prjCrt.bio))
        if prjCrt.notes:
            xmlCrt.append(text_to_xml_element('Notes', prjCrt.notes))

    def _build_element_tree(self, root):
        #--- Process project attributes.

        xmlProject = ET.SubElement(root, 'PROJECT')
        self._build_project_branch(xmlProject)

        #--- Process arcs and turning points.
        xmlArcs = ET.SubElement(root, 'ARCS')
        for acId in self.story.tree.get_children(AC_ROOT):
            self._build_arc_branch(xmlArcs, self.story.arcs[acId], acId)

        #--- Process characters.
        xmlCharacters = ET.SubElement(root, 'CHARACTERS')
        for crId in self.story.tree.get_children(CR_ROOT):
            xmlCrt = ET.SubElement(xmlCharacters, 'CHARACTER', attrib={'id':crId})
            self._build_character_branch(xmlCrt, self.story.characters[crId])

        #--- Process books.
        xmlBooks = ET.SubElement(root, 'BOOKS')
        for bkId in self.story.tree.get_children(BK_ROOT):
            xmlBook = ET.SubElement(xmlBooks, 'BOOK', attrib={'id':bkId})
            self._build_book_branch(xmlBook, self.story.books[bkId])

    def _build_book_branch(self, xmlBook, prjBook):
        if prjBook.title:
            ET.SubElement(xmlBook, 'Title').text = prjBook.title
        if self.story.desc:
            xmlBook.append(text_to_xml_element('Desc', prjBook.desc))

    def _build_project_branch(self, xmlProject):
        if self.story.title:
            ET.SubElement(xmlProject, 'Title').text = self.story.title
        if self.story.desc:
            xmlProject.append(text_to_xml_element('Desc', self.story.desc))

    def _postprocess_xml_file(self, filePath):
        """Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath: str -- path to xml file.
        
        Read the xml file and put a header on top. 
        Overwrite the .stlx xml file.
        Raise the "Error" exception in case of error. 
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for storyliner-generated xml files other than .stlx as well. 
        """
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(f'{self.XML_HEADER}{text}')
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _read_books(self, root):
        """Read book data from the xml element tree."""
        for xmlBook in root.find('BOOKS'):
            bkId = xmlBook.attrib['id']
            self.story.books[bkId] = Book(on_element_change=self.on_element_change)
            self.story.books[bkId].title = get_element_text(xmlBook, 'Title')
            self.story.books[bkId].desc = xml_element_to_text(xmlBook.find('Desc'))
            self.story.books[bkId].notes = xml_element_to_text(xmlBook.find('Notes'))
            self.story.books[bkId].nvPath = xmlBook.attrib.get('path', None)
            self.story.tree.append(BK_ROOT, bkId)

    def _read_arcs(self, root):
        """Read arc data from the xml element tree."""
        for xmlArc in root.find('ARCS'):
            acId = xmlArc.attrib['id']
            self.story.arcs[acId] = Arc(on_element_change=self.on_element_change)
            self.story.arcs[acId].title = get_element_text(xmlArc, 'Title')
            self.story.arcs[acId].desc = xml_element_to_text(xmlArc.find('Desc'))
            self.story.arcs[acId].notes = xml_element_to_text(xmlArc.find('Notes'))
            self.story.arcs[acId].shortName = get_element_text(xmlArc, 'ShortName')
            self.story.tree.append(AC_ROOT, acId)
            for xmlPoint in xmlArc.iterfind('POINT'):
                tpId = xmlPoint.attrib['id']
                self.story.turningPoints[tpId] = TurningPoint(on_element_change=self.on_element_change)
                self.story.turningPoints[tpId].title = get_element_text(xmlPoint, 'Title')
                self.story.turningPoints[tpId].desc = xml_element_to_text(xmlPoint.find('Desc'))
                self.story.turningPoints[tpId].notes = xml_element_to_text(xmlPoint.find('Notes'))
                try:
                    position = int(xmlPoint.attrib['position'])
                except:
                    position = 0
                self.story.turningPoints[tpId].position = position
                tpBooks = []
                xmlBooks = xmlPoint.find('Books')
                if xmlBooks is not None:
                    bkIds = xmlBooks.get('ids', None)
                    for bkId in string_to_list(bkIds, divider=' '):
                        if bkId and bkId in self.story.books:
                            tpBooks.append(bkId)
                self.story.turningPoints[tpId].books = tpBooks

                self.story.tree.append(acId, tpId)

    def _read_characters(self, root):
        """Read characters from the xml element tree."""
        for xmlCharacter in root.find('CHARACTERS'):
            crId = xmlCharacter.attrib['id']
            self.story.characters[crId] = Character(on_element_change=self.on_element_change)
            self.story.characters[crId].isMajor = xmlCharacter.get('major', None) == '1'
            self.story.characters[crId].title = get_element_text(xmlCharacter, 'Title')
            self.story.characters[crId].desc = xml_element_to_text(xmlCharacter.find('Desc'))
            self.story.characters[crId].notes = xml_element_to_text(xmlCharacter.find('Notes'))
            self.story.characters[crId].goals = xml_element_to_text(xmlCharacter.find('Role'))
            self.story.characters[crId].fullName = get_element_text(xmlCharacter, 'FullName')
            self.story.tree.append(CR_ROOT, crId)

    def _read_project(self, root):
        """Read data at project level from the xml element tree."""
        xmlProject = root.find('PROJECT')
        self.story.title = get_element_text(xmlProject, 'Title')
        self.story.desc = xml_element_to_text(xmlProject.find('Desc'))

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def _write_element_tree(self, xmlProject):
        """Write back the xml element tree to a .stlx xml file located at filePath.
        
        Raise the "Error" exception in case of error. 
        """
        backedUp = False
        if os.path.isfile(xmlProject.filePath):
            try:
                os.replace(xmlProject.filePath, f'{xmlProject.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(xmlProject.filePath)}".')
            else:
                backedUp = True
        try:
            xmlProject.xmlTree.write(xmlProject.filePath, xml_declaration=False, encoding='utf-8')
        except Error:
            if backedUp:
                os.replace(f'{xmlProject.filePath}.bak', xmlProject.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(xmlProject.filePath)}".')

