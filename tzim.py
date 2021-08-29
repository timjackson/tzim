#!/usr/bin/python3

# tzim.py - Simple conversion module to convert a Tomboy/Gnote notes to zim notes.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2007,2008 Bengt J. Olsson 
# Copyright 2020      Osamu Aoki
# Copyright 2021      Tim Jackson

import os
import os.path
import sys
import glob
import re
import argparse

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Convert Gnote/Tomboy notes to Zim')
    parser.add_argument('--source-dir', help='Gnote/Tomboy source directory', required=True)
    parser.add_argument('--dest-dir', help='Zim destination directory', required=True)
    args = parser.parse_args()

    # Fix up source/dest paths
    home = os.path.expanduser("~")
    tomboynotes = os.path.realpath(os.path.expanduser(args.source_dir))
    if not tomboynotes[-1] == "/":
        tomboynotes += "/"
    print("Reading Gnote/Tomboy notes from: ", tomboynotes)
    files = glob.glob(tomboynotes + "*.note")  # Read tomboy notes file names
    if len(files) == 0:
        print("No note files.")  # Exit if no note files in directory
        sys.exit()
    zimnotes = args.dest_dir
    zimnotes = zimnotes.rstrip()
    if zimnotes == "":
        # current
        zimnotes = "."
    zimnotes = os.path.realpath(os.path.expanduser(zimnotes))
    if not zimnotes[-1] == "/":
        zimnotes += "/"
    if zimnotes == tomboynotes:
        # avoid overlapping directory
        zimnotes += "zim/"
    print("Writing Zim notes to: ", zimnotes)
    if not os.path.exists(zimnotes):
        os.mkdir(zimnotes)
    elif os.listdir(zimnotes):
        print("  INFO: Some files exist in ", zimnotes)
    
    curdir = os.getcwd()
    os.chdir(zimnotes)
    
    # Do the conversion
    errors = 0
    for file in files:
        print("Converting: ", os.path.basename(file))
    
        infile = open(file, "r")
        longline = infile.read()
        infile.close()

        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(longline)
        except:
            print("  ERROR: Could not parse note (invalid file?)")
            errors += 1
        
        if root.attrib['version'] not in ["0.2", "0.3"]:
            print("  WARNING: only tested with Tomboy note version 0.2 and 0.3 (found " + root.attrib['version'] +")")
        
        text = ''
        title = 'Untitled'
        last_change_date = 'Not found'
        create_date = 'Not found'
        folder = ''
        
        for element in root:
            if element.tag == '{http://beatniksoftware.com/tomboy}text':
                text = parse_content(element)
            elif element.tag == '{http://beatniksoftware.com/tomboy}title':
                title = element.text
            elif element.tag == '{http://beatniksoftware.com/tomboy}last-change-date':
                last_change_date = element.text
                match = re.search(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', last_change_date)
                if match:
                    last_change_date = match.group(1) + " " + match.group(2)
            elif element.tag == '{http://beatniksoftware.com/tomboy}create-date':
                create_date = element.text
                match = re.search(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', create_date)
                if match:
                    create_date = match.group(1) + " " + match.group(2)
            elif element.tag == '{http://beatniksoftware.com/tomboy}tags':
                tag = element.find('.//{http://beatniksoftware.com/tomboy}tag')
                if tag is not None:
                    match = re.search("system:notebook:(.+)$", str(tag.text), re.S)
                    if match:
                        folder = match.group(1)      
                        print(" Filing in folder: " + folder)
                    else:
                        # might be system:template
                        pass

        if title == "Untitled":
            print ("  ERROR: Could not find note title")
            sys.exit()

        # Put together Zim note
        outname = title
        outname = re.sub("[/&<>:; ]", "_", outname)  # removing "dangerous" chars
        outname += ".txt"  # Zim file name for note
        if folder != "":
            if not os.path.exists(folder):
                os.mkdir(folder)
            outname = folder + "/" + outname
        outfile = open(outname, "w")
        line = "====== " + title + " ======" + "\n"
        line += text + "\n"
        line += "\n" + "Last changed (in Tomboy/Gnote): " + last_change_date + "\n"
        line += "Note created (in Tomboy/Gnote): " + create_date + "\n"
        outfile.write(line)
        outfile.close()
    print("\nConversion complete (with " + str(errors) + " error(s))")
    
    os.chdir(curdir)

# ------------------------------------------------------------------------------

def parse_content(textelement):
    note_content = textelement.find('.//{http://beatniksoftware.com/tomboy}note-content')
    output = ""
    
    if note_content is None:
        print("Could not find note content")
        sys.exit()
    
    # Strip first line, which is a repeat of the note title
    if note_content.text is not None:
        leading_text = re.sub(r'^.+\n', '', str(note_content.text))
        output = str(leading_text)

    output += iterate_elements(note_content)

    if note_content.tail is not None:
        output += str(note_content.tail)

    return output
    
    
def iterate_elements(e, output="", depth=0):
    for element in e:
        if element.tag == '{http://beatniksoftware.com/tomboy}list':
            output = iterate_elements(element, output, depth+1)
            if element.tail is not None:
                output += str(element.tail)
        elif element.tag == '{http://beatniksoftware.com/tomboy}list-item':
            output += "\t" * depth + "* "
            if element.text is not None:
                output += str(element.text)
            if element.tail is not None:
                output += str(element.tail)
            output = iterate_elements(element, output, depth)
        elif element.tag == '{http://beatniksoftware.com/tomboy}italic':
            output += format_text(element, '//')
        elif element.tag == '{http://beatniksoftware.com/tomboy}bold':
            output += format_text(element, '**')
        elif element.tag == '{http://beatniksoftware.com/tomboy}strikethrough':
            output += format_text(element, '~~')
        elif element.tag == '{http://beatniksoftware.com/tomboy}highlight':
            output += format_text(element, '__')
        elif element.tag == '{http://beatniksoftware.com/tomboy}monospace':
            output += format_text(element, "''")
        elif element.tag == '{http://beatniksoftware.com/tomboy}underline':
            # no underline
            output += format_text(element)
        elif element.tag == '{http://beatniksoftware.com/tomboy/link}internal':
            if element.text is not None:
                output += "[[" + str(element.text) + "]]"
            if element.tail is not None:
                output += str(element.tail)
        elif element.tag == '{http://beatniksoftware.com/tomboy/link}broken':
            if element.text is not None:
                output += "[[" + str(element.text) + "]]"
            if element.tail is not None:
                output += str(element.tail)
        elif element.tag == '{http://beatniksoftware.com/tomboy/link}url':
            output += format_text(element)
        elif '{http://beatniksoftware.com/tomboy/size}' in element.tag:
            # we don't do anything with size
            output += format_text(element)
        else:
            print("  WARNING: Unknown/unsupported tag in source note: '" + element.tag + "'\n")
            output += format_text(element)

    return output


def format_text(element,formatter=""):
    output = ""
    
    if element.text is not None and element.text != "":
        output = formatter + str(element.text) + formatter
        
    if element.tail is not None and element.text != "":
        output += str(element.tail)
    
    return output

main()
