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

    def test_ValidDocument(self):
        (handle, temp_file_path) = tempfile.mkstemp()
        with os.fdopen(handle, "wb") as f:
            f.write("""<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <name>-i</name>
                        <name>--input-file</name>
                    </argument>
                </cligen>
            """.encode("utf8"))
        try:
            x = ArgumentSpecParser()
            retval = x.parse_file(temp_file_path)
        finally:
            os.unlink(temp_file_path)

        self.assertIsInstance(retval, ArgumentParserSpec)


class Test_ArgumentSpecParser_parse_string(unittest.TestCase):

    def test_EmptyFile(self):
        self.assert_xml_parse_error(
            "",
            expected_message="no element found: line 1, column 0"
        )

    def test_InvalidXml1(self):
        self.assert_xml_parse_error(
            "<unclosed",
            expected_message="unclosed token: line 1, column 0"
        )

    def test_InvalidXml2(self):
        self.assert_xml_parse_error(
            "<unmatched>",
            expected_message="no element found: line 1, column 11"
        )

    def assert_xml_parse_error(self, xml_string, expected_message):
        x = ArgumentSpecParser()
        with self.assertRaises(x.XmlParseError) as cm:
            x.parse_string(xml_string)
        self.assertEqual(expected_message, "{}".format(cm.exception))

    def test_InvalidXmlRootElement_WrongName_NoNamespace(self):
        self.assert_cligen_xml_error(
            "<wrongname/>",
            expected_message="incorrect tag name of XML root element: "
            "wrongname (expected {http://schemas.cligen.io/arguments}cligen)"
        )

    def test_InvalidXmlRootElement_WrongName_IncorrectNamespace(self):
        self.assert_cligen_xml_error(
            """<wrongname xmlns="http://www.bad.com" />""",
            expected_message="incorrect tag name of XML root element: "
            "{http://www.bad.com}wrongname (expected {http://schemas.cligen.io/arguments}cligen)"
        )

    def test_InvalidXmlRootElement_WrongName_CorrectNamespace(self):
        self.assert_cligen_xml_error(
            """<wrongname xmlns="http://schemas.cligen.io/arguments" />""",
            expected_message="incorrect tag name of XML root element: "
            "{http://schemas.cligen.io/arguments}wrongname "
            "(expected {http://schemas.cligen.io/arguments}cligen)"
        )

    def test_InvalidXmlRootElement_CorrectName_NoNamespace(self):
        self.assert_cligen_xml_error(
            "<cligen />",
            expected_message="incorrect tag name of XML root element: "
            "cligen (expected {http://schemas.cligen.io/arguments}cligen)"
        )

    def test_InvalidXmlRootElement_CorrectName_IncorrectNamespace(self):
        self.assert_cligen_xml_error(
            """<cligen xmlns="http://www.bad.com" />""",
            expected_message="incorrect tag name of XML root element: "
            "{http://www.bad.com}cligen (expected {http://schemas.cligen.io/arguments}cligen)"
        )

    def assert_cligen_xml_error(self, xml_string, expected_message):
        x = ArgumentSpecParser()
        with self.assertRaises(x.CligenXmlError) as cm:
            x.parse_string(xml_string)
        self.assertEqual(expected_message, "{}".format(cm.exception))

    def test_NoArguments(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments" />
            """,
            arguments=[],
        )

    def test_options_add_builtin_help_argument_True(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <options>
                        <add-builtin-help-argument>true</add-builtin-help-argument>
                    </options>
                    <argument>
                        <key>-n</key>
                        <key>--name</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-n", "--name"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
        )

    def test_options_add_builtin_help_argument_False(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <options>
                        <add-builtin-help-argument>false</add-builtin-help-argument>
                    </options>
                    <argument>
                        <key>-n</key>
                        <key>--name</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-n", "--name"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
            add_builtin_help_argument=False,
        )

    def test_options_add_builtin_help_argument_CaseInsensitive(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <options>
                        <add-builtin-help-argument>  FaLsE   </add-builtin-help-argument>
                    </options>
                    <argument>
                        <key>-n</key>
                        <key>--name</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-n", "--name"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
            add_builtin_help_argument=False,
        )

    def test_options_add_builtin_help_argument_InvalidValue(self):
        self.assert_cligen_xml_error(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <options>
                        <add-builtin-help-argument>cheese</add-builtin-help-argument>
                    </options>
                    <argument>
                        <key>-n</key>
                        <key>--name</key>
                    </argument>
                </cligen>
            """,
            expected_message="invalid text in element {http://schemas.cligen.io/arguments}"
            "add-builtin-help-argument: cheese (expected \"true\" or \"false\")"
        )

    def test_1Argument(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>-n</key>
                        <key>--name</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-n", "--name"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None
                )
            ],
        )

    def test_2Arguments(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>-n</key>
                        <key>--name</key>
                    </argument>
                    <argument>
                        <key>-t</key>
                        <key>--title</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-n", "--name"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                ),
                ArgumentParserSpec.Argument(
                    keys=("-t", "--title"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                ),
            ],
        )

    def test_argument_key_NotSpecified(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=(),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
        )

    def test_argument_key_1Key(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>--write</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("--write",),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
        )

    def test_argument_key_3Keys(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>-w</key>
                        <key>--write</key>
                        <key>--write-file</key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-w", "--write", "--write-file"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
        )

    def test_argument_key_trimming(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>   -h</key>
                        <key>--help    </key>
                        <key>
                            --help-me
                        </key>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-h", "--help", "--help-me"),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text=None,
                )
            ],
        )

    def test_argument_help(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>-q</key>
                        <help>Keep quiet</help>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-q",),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text="Keep quiet",
                )
            ],
        )

    def test_argument_help_trimming(self):
        self.assert_xml_parse_success(
            """<?xml version="1.0" ?>
                <cligen xmlns="http://schemas.cligen.io/arguments">
                    <argument>
                        <key>-q</key>
                        <help>
                            Keep quiet
                        </help>
                    </argument>
                </cligen>
            """,
            arguments=[
                ArgumentParserSpec.Argument(
                    keys=("-q",),
                    type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                    help_text="Keep quiet",
                )
            ],
        )

    def assert_xml_parse_success(
            self, xml_string, arguments=None, help_argument=None, add_builtin_help_argument=None):
        x = ArgumentSpecParser()
        actual = x.parse_string(xml_string)

        if arguments is None:
            arguments = []
        arguments = tuple(arguments)

        if add_builtin_help_argument is None or add_builtin_help_argument:
            help_argument = ArgumentParserSpec.Argument(
                keys=("-h", "--help"),
                type=ArgumentParserSpec.Argument.TYPE_BUILTIN_HELP,
                help_text="Print the help information then exit",
            )
            arguments += (help_argument,)

        expected = ArgumentParserSpec(
            arguments=arguments,
            help_argument=help_argument,
        )

        self.assertEqual(actual, expected)
