#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright 2017 gepd@outlook.com

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

author: gepd
website: https://github.com/gepd/ReadConfig
library version: 0.0.1
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import re

ENCODING = 'utf8'

class ReadConfig(object):
    """Configuration file parser.

    A configuration file consists of sections, lead by a "[section]" header,
    and followed by "name = value" entries

    class:

    ReadConfig -- responsible for parsing a list of
                  configuration files, and managing
                  the parsed database.
    """

    # Parsing regular expressions

    # Section regex
    _SECTION_PATT = r"""
    \[
    [a-zA-Z0-9:*_-]+        # letters, numbers and :-_ simbols
    \]"""

    # option regex
    _OPTION_PATT = r"""
    [a-zA-Z0-9_]*
    """

    # value regex
    _VALUE_PATT = r"""
    ((\w+\s\=+\s*)? (.+)|)
    """

    # Compiled regular expression for matching sections
    SECTCRE = re.compile(_SECTION_PATT, re.VERBOSE)

    # Compiled regular expression for matching options
    OPTRE = re.compile(_OPTION_PATT, re.VERBOSE)

    # Compiled regular expression for matching options
    VALRE = re.compile(_VALUE_PATT, re.VERBOSE)

    # Compiled regular expression for remove square brakets
    _KEYCRE = re.compile(r"\[|\]")

    # data stored
    _old_data = []
    _data = {}
    _sections = []
    _cur_sect = None
    _cur_opt = None
    _in_option = False
    _new_sect = []
    _new_opts = {}
    _del_sect = []
    _del_opts = {}

    def read(self, filepath):
        with open(filepath, 'rb') as file:
            for line in file:

                line = line.decode(ENCODING)

                # store file in the current state
                self._old_data.append(line)

                if(line and not line.startswith('#')):
                    # store sections
                    self._raw_sections(line)
                    # store options
                    self._raw_options(line)
                    # store values
                    self._raw_values(line)
    
    def _raw_sections(self, line):
        sec = self.SECTCRE.match(line)
        if(sec):
            sec = self._KEYCRE.sub('', line)
            self._data[sec] = {}
            self._cur_sect = sec
            self._sections.append(sec)
            self._in_option = False
    
    def _raw_options(self, line):
        opt = self.OPTRE.match(line)
        if(opt):
            opt = opt.group(0).strip()
            if(opt):
                self._data[self._cur_sect][opt] = []
                self._cur_opt = opt
                self._in_option = True

    def _raw_values(self, line):

        if(self._in_option):
            val = self.VALRE.match(line)
            if(val):
                val = val.group(3).rstrip()
                if(val):
                    self._data[self._cur_sect][self._cur_opt].append(val)

    def add_section(self, section):
        """
        Add a section named section to the instance. If a section by the
        given name already exists, will return false
        """
        if(section not in self._sections):
            self._new_sect.append(section)
            self._sections.append(section)
            return True
        return False

    def set(self, section, option, value):
        """
        If the given section exists, set the given option to the specified
        value; otherwise will return false. each argument expects a string
        """
        if(section in self._sections):
            self._new_opts[section] = {}
            self._new_opts[section][option] = value
            return True
        return False

    def get(self, section, option):
        """
        Get an option value for the named section.
        """
        if(section in self._sections):
            if(option in self._data[section].keys()):
                return self._data[section][option][0]
        return False

    def has_section(self, section):
        """
        Checks if the named section is present  or not.
        """
        return section in self._sections

    def has_option(self, section, option):
        """
        Checks if the named option is present  or not.
        """
        if(section not in self._sections):
            return False
        return option in self._data[section].keys()

    def sections(self):
        """
        Return a list of the sections available
        """
        return self._sections

    def options(self, section):
        """
        Returns a list of options available in the specified section
        """
        if(self.has_section(section)):
            return self._data[section].keys()
        return False

    def remove_section(self, section):
        """
        Remove the specified section from the configuration. If the
        section in fact existed, return True. Otherwise return False.
        """
        if(section in self._sections):
            self._del_sect.append(section)
            return True
        return False

    def remove_option(self, section, option):
        """
        Remove the specified option from the specified section. If
        the section does not exist will return None. If the option
        existed to be removed, return True; otherwise return False.
        """
        if(section in self._sections):
            if(option in self._options):
                if(section not in self._del_opts):
                    self._del_opts[section] = []
                self._del_opts[section].append(option)
                return True
            return False
        return None

    def write(self, fileobject):
        """
        Write a representation of the configuration to the specified
        file object.
        """
        new_line = 0    # avoid to have two consecutive \n
        new_data = ""   # where new file will be stored
        section = None  # current covered section

        # print(self._old_data)
        print(self._data)

        for line in self._old_data:
            line = line + '\r\n'

            # section(s) to remove
            sec = self.SECTCRE.match(line)
            if(sec):
                sec = self._KEYCRE.sub('', line).strip()
                if(sec not in self._del_sect):
                    new_data = new_data + line
                    new_line = 0
                section = sec

            # option(s) to remove
            opt = self.OPTRE.match(line)
            if(opt):
                opt = opt.group(0).strip()
                try:
                    # remove option(s) with remove_option
                    if(opt and opt not in self._del_opts[section]):
                        new_data = new_data + line
                        new_line = 0
                except:
                    # remove option(s) from removed section(s)
                    if(section not in self._del_sect):
                        new_data = new_data + line
                        new_line = 0

            # count \n
            if(line == '\n'):
                new_line = new_line + 1

            # write comments and new line char
            # new_line will avoid more than two \n consecutive
            if(line.startswith('#') or line == '\n' and new_line < 2):
                new_data = new_data + line
                if(line.startswith('#')):
                    new_line = 0

        # add new sections and options
        for section in self._new_sect:
            new_sect = "\n[{0}]\n".format(section)
            new_data = new_data + new_sect

            option = self._new_opts[section].items()
            option = "{0} = {1}\n".format(option[0][0], option[0][1])
            new_data = new_data + option

        # write the file
        fileobject.write(new_data.encode(ENCODING))