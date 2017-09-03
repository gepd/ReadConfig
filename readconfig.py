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
from __future__ import unicode_literals

import re
from os import path

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
    _VALUE_PATT = r'((\w+\s\=\s*)? (.+)|)'

    # Compiled regular expression for matching sections
    SECTCRE = re.compile(_SECTION_PATT, re.VERBOSE)

    # Compiled regular expression for matching options
    OPTRE = re.compile(_OPTION_PATT, re.VERBOSE)

    # Compiled regular expression for matching options
    VALRE = re.compile(_VALUE_PATT)

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
    _bad_format = False

    def read(self, filepath):

        if(not path.exists(filepath)):
            return False

        with open(filepath, 'rb') as file:
            for line in file:

                line = line.decode(ENCODING)

                # store file in the current state
                self._old_data.append(line.rstrip())

                if(line and not line.startswith('#')):
                    # store sections
                    self._raw_sections(line)
                    # store options
                    self._raw_options(line)
                    # stop if file has a bad format
                    if(self._bad_format):
                        break
                    # store values
                    self._raw_values(line)
    
    def _raw_sections(self, line):
        is_section = self.SECTCRE.match(line)
        if(is_section):
            section = self._KEYCRE.sub('', line).rstrip()
            self._data[section] = {}
            self._cur_sect = section
            self._sections.append(section)
            self._in_option = False
    
    def _raw_options(self, line):
        is_option = self.OPTRE.match(line)
        if(is_option):
            option = is_option.group(0).strip()
            if(option):
                section = self._cur_sect
                if(not section):
                    self._bad_format = True
                    return
                self._data[section][option] = []
                self._cur_opt = option
                self._in_option = True

    def _raw_values(self, line):
        if(self._in_option):
            is_value = self.VALRE.match(line)
            if(is_value):
                if(is_value.group(3)):
                    section = self._cur_sect
                    option = self._cur_opt
                    value = is_value.group(3).rstrip()
                    self._data[section][option].append(value)
    
    def bad_format(self):
        return self._bad_format

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
        if(section in self._new_sect):
            if(section not in self._new_opts):
                self._new_opts[section] = {}
            self._new_opts[section][option] = [str(value) + '\n']
        elif(section in self._data):
            self._data[section][option] = [str(value) + '\n']                
            return True
        return False

    def get(self, section, option):
        """
        Get an option value for the named section.
        """
        if(section in self._sections):
            if(option in self._data[section].keys()):
                values = self._data[section][option]
                if(len(values) > 1):
                    return values
                else:
                    return values[0]
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
        the section does not exist, it will return None. Otherwise
        will return false if the option do not exist and True if
        it's removed.
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
        new_line = 0     # avoid to have two consecutive \n
        new_data = ""    # where new file will be stored
        section = None   # current covered section
        num_options = 0  # num of options in a section
        indx_option = 0  # index of the current option

        for line in self._old_data:
            line = line + '\n'

            # section(s) to remove
            is_section = self.SECTCRE.match(line)
            if(is_section):
                section = self._KEYCRE.sub('', line).strip()

                if(section not in self._del_sect):
                    new_data = new_data + line
                    new_line = 0
                
                num_options = len(self._data[section])
                indx_option = 0

            # remove and update options
            is_option = self.OPTRE.match(line)
            if(is_option):
                option = is_option.group(0).strip()
                if(section not in self._del_sect and \
                    option not in self._del_opts and option):

                        quant = len(self._data[section][option])
                        value = self._data[section][option]
                        
                        if(quant == 1):
                            line = '{0} = {1}\n'.format(option, value[0])
                        else:
                            value = "\n".join(value)
                            line = '{0} = \n{1}\n'.format(option, value)

                        new_data = new_data + line
                        indx_option = indx_option + 1

            # new options in section
            if(indx_option == num_options and
                section in self._new_opts):
                options = self._new_opts[section]
                for option in options:
                    value = options[option]
                    option = '{0} = {1}'.format(option, value[0])
                    new_data = new_data + option
                del self._new_opts[section]

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

            for key, value in self._new_opts[section].items():
                option = "{0} = {1}".format(key, value[0])
                new_data = new_data + option

        # write the file
        fileobject.write(new_data.encode(ENCODING))