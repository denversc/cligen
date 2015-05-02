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

import os
import unittest
import xml.etree.ElementTree

from cligen.argspec_xml_parser import ArgumentSpecParser
from cligen.argspec import ArgumentParserSpec


class TestSampleCligenXml(unittest.TestCase):

    def test_ValidUTF8(self):
        path = self.sample_cligen_xml_path()
        with open(path, "rt", encoding="utf8", errors="strict") as f:
            f.read()

    def test_ValidXML(self):
        path = self.sample_cligen_xml_path()
        xml.etree.ElementTree.parse(path)

    def test_ValidCligenArgumentSpec(self):
        path = self.sample_cligen_xml_path()
        parser = ArgumentSpecParser()
        parser.parse_file(path)

    def test_ParsedXML(self):
        path = self.sample_cligen_xml_path()
        parser = ArgumentSpecParser()
        actual = parser.parse_file(path)

        help_argument = ArgumentParserSpec.Argument(
            keys=("-h", "--help"),
            help_text="Print the help information then exit",
        )

        expected_arguments = (
            ArgumentParserSpec.Argument(
                keys=("-i", "--input-file"),
                help_text="The file from which to read",
            ),
            ArgumentParserSpec.Argument(
                keys=("-o", "--output-file"),
                help_text="The file to which to write",
            ),
            help_argument,
        )
        expected = ArgumentParserSpec(
            arguments=expected_arguments,
            help_argument=help_argument,
        )

        self.assertEqual(actual, expected)

    def sample_cligen_xml_path(self):
        import cligen.main
        dir_path = os.path.dirname(cligen.main.__file__)
        return os.path.join(dir_path, "sample_cligen.xml")
