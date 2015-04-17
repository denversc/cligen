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
import tempfile
import unittest

from cligen.argspec import ArgumentParserSpec
from cligen.argspec_xml_parser import ArgumentSpecParser


class Test_ArgumentSpecParser_parse_file(unittest.TestCase):

    def test_PathDoesNotExist(self):
        (handle, temp_file_path) = tempfile.mkstemp()
        os.close(handle)
        os.unlink(temp_file_path)
        x = ArgumentSpecParser()
        with self.assertRaises(FileNotFoundError):
            x.parse_file(temp_file_path)

    def test_PathIsAFile(self):
        temp_dir_path = tempfile.mkdtemp()
        try:
            x = ArgumentSpecParser()
            with self.assertRaises(IsADirectoryError):
                x.parse_file(temp_dir_path)
        finally:
            os.rmdir(temp_dir_path)

    def test_InvalidXml(self):
        (handle, temp_file_path) = tempfile.mkstemp()
        os.close(handle)
        try:
            x = ArgumentSpecParser()
            with self.assertRaises(x.XmlParseError):
                x.parse_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)

    def test_ValidDocoument(self):
        (handle, temp_file_path) = tempfile.mkstemp()
        with os.fdopen(handle, "wt", encoding="utf8") as f:
            print("""<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <name>-i</name>
                        <name>--input-file</name>
                    </argument>
                </cligen>
            """, file=f)
        try:
            x = ArgumentSpecParser()
            retval = x.parse_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)

        self.assertIsInstance(retval, ArgumentParserSpec)


class Test_ArgumentSpecParser_parse_string(unittest.TestCase):

    def test_EmptyFile(self):
        self.assert_xml_parse_error(
            xml_string="",
            expected_message="no element found: line 1, column 0"
        )

    def test_InvalidXml1(self):
        self.assert_xml_parse_error(
            xml_string="<unclosed",
            expected_message="unclosed token: line 1, column 0"
        )

    def test_InvalidXml2(self):
        self.assert_xml_parse_error(
            xml_string="<unmatched>",
            expected_message="no element found: line 1, column 11"
        )

    def assert_xml_parse_error(self, xml_string, expected_message):
        x = ArgumentSpecParser()
        with self.assertRaises(x.XmlParseError) as cm:
            x.parse_string(xml_string)
        self.assertEqual(expected_message, "{}".format(cm.exception))
