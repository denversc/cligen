# Copyright 2015 Denver Coneybeare <denver@sleepydragon.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The "main application" class for the cligen command-line utility.
"""

from cligen.argspec_xml_parser import ArgumentSpecParser


class CligenApplication:

    def __init__(
            self, source_file_path, output_file_paths, target_language, inline, encoding, newline):
        self.source_file_path = source_file_path
        self.output_file_paths = output_file_paths
        self.target_language = target_language
        self.inline = inline
        self.encoding = encoding
        self.newline = newline

    def run(self):
        argspec = self.read_source_file()
        self.generate_output_files(argspec)

    def read_source_file(self):
        parser = ArgumentSpecParser()
        try:
            return parser.parse_file(self.source_file_path)
        except IOError as e:
            raise self.Error("reading file failed: {} ({})".format(
                self.source_file_path, e.strerror))
        except parser.Error as e:
            raise self.Error("parsing file failed: {} ({})".format(self.source_file_path, e))

    def generate_output_files(self, argspec):
        try:
            self.target_language.generate(
                argspec=argspec,
                output_file_paths=self.output_file_paths,
                encoding=self.encoding,
                newline=self.newline,
            )
        except self.target_language.Error as e:
            raise self.Error("{}".format(e))

    class Error(Exception):
        pass
