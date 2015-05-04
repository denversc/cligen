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

import unittest

from cligen.argspec import ArgumentParserSpec


class Test_ArgumentSpecParser(unittest.TestCase):

    DEFAULT_VALUE = object()

    def test___init___PositionalArgs(self):
        arguments = object()
        help_argument = object()
        x = ArgumentParserSpec(arguments, help_argument)
        self.assertIs(arguments, x.arguments)
        self.assertIs(help_argument, x.help_argument)

    def test___init___KeywordArgs(self):
        arguments = object()
        help_argument = object()
        x = ArgumentParserSpec(arguments=arguments, help_argument=help_argument)
        self.assertIs(arguments, x.arguments)
        self.assertIs(help_argument, x.help_argument)

    def test___eq___Equal(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec()
        self.assertTrue(x1 == x2)

    def test___eq___arguments_Missing(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec()
        del x2.arguments
        self.assertFalse(x1 == x2)

    def test___eq___arguments_Unequal(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec(arguments=[])
        self.assertFalse(x1 == x2)

    def test___eq___help_argument_Missing(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec()
        del x2.help_argument
        self.assertFalse(x1 == x2)

    def test___eq___help_argument_Unequal(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec(help_argument=object())
        self.assertFalse(x1 == x2)

    def test___ne___Equal(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec()
        self.assertFalse(x1 != x2)

    def test___ne___arguments_Missing(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec()
        del x2.arguments
        self.assertTrue(x1 != x2)

    def test___ne___arguments_Unequal(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec(arguments=[])
        self.assertTrue(x1 != x2)

    def test___ne___help_argument_Missing(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec()
        del x2.help_argument
        self.assertTrue(x1 != x2)

    def test___ne___help_argument_Unequal(self):
        x1 = self.new_ArgumentParserSpec()
        x2 = self.new_ArgumentParserSpec(help_argument=object())
        self.assertTrue(x1 != x2)

    def new_ArgumentParserSpec(self, arguments=DEFAULT_VALUE, help_argument=DEFAULT_VALUE):
        if arguments is self.DEFAULT_VALUE:
            input_file_argument = ArgumentParserSpec.Argument(
                keys=["-i", "--input-file"],
                type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                help_text="The input file",
            )
            output_file_argument = ArgumentParserSpec.Argument(
                keys=["-o", "--output-file"],
                type=ArgumentParserSpec.Argument.TYPE_STRING_VALUE,
                help_text="The output file",
            )
            arguments = [input_file_argument, output_file_argument]

            if help_argument is self.DEFAULT_VALUE:
                help_argument = ArgumentParserSpec.Argument(
                    keys=["-h", "--help"],
                    type=ArgumentParserSpec.Argument.TYPE_BUILTIN_HELP,
                    help_text="Show the help screen then exit",
                )

            if help_argument is not None:
                arguments.append(help_argument)

        return ArgumentParserSpec(
            arguments=arguments,
            help_argument=help_argument,
        )


class Test_ArgumentParserSpec_Argument(unittest.TestCase):

    def test___init___PositionalArgs(self):
        keys = object()
        type = object()
        help_text = object()
        x = ArgumentParserSpec.Argument(keys, type, help_text)
        self.assertIs(keys, x.keys)
        self.assertIs(type, x.type)
        self.assertIs(help_text, x.help_text)

    def test___init___KeywordArgs(self):
        keys = object()
        type = object()
        help_text = object()
        x = ArgumentParserSpec.Argument(keys=keys, type=type, help_text=help_text)
        self.assertIs(keys, x.keys)
        self.assertIs(type, x.type)
        self.assertIs(help_text, x.help_text)

    def test___eq___Equal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        self.assertTrue(x1 == x2)

    def test___eq___keys_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.keys
        self.assertFalse(x1 == x2)

    def test___eq___keys_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(keys=[])
        self.assertFalse(x1 == x2)

    def test___eq___type_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.type
        self.assertFalse(x1 == x2)

    def test___eq___type_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(type=[])
        self.assertFalse(x1 == x2)

    def test___eq___help_text_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.help_text
        self.assertFalse(x1 == x2)

    def test___eq___help_text_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(help_text="blah blah")
        self.assertFalse(x1 == x2)

    def test___ne___Equal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        self.assertFalse(x1 != x2)

    def test___ne___keys_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.keys
        self.assertTrue(x1 != x2)

    def test___ne___keys_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(keys=[])
        self.assertTrue(x1 != x2)

    def test___ne___type_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.type
        self.assertTrue(x1 != x2)

    def test___ne___type_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(type=[])
        self.assertTrue(x1 != x2)

    def test___ne___help_text_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.help_text
        self.assertTrue(x1 != x2)

    def test___ne___help_text_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(help_text="blah blah")
        self.assertTrue(x1 != x2)

    def test___str___keys_Length0(self):
        x = self.new_Argument(keys=[])
        self.assertEqual("", "{}".format(x))

    def test___str___keys_Length1(self):
        x = self.new_Argument(keys=["-n"])
        self.assertEqual("-n", "{}".format(x))

    def test___str___keys_Length2(self):
        x = self.new_Argument(keys=["-n", "--name"])
        self.assertEqual("-n/--name", "{}".format(x))

    def test___repr___(self):
        keys = ["keys"]
        type = "the type"
        help_text = "help_text"
        x = self.new_Argument(keys=keys, type=type, help_text=help_text)

        expected = "Argument(keys={keys!r}, type={type!r}, help_text={help_text!r})".format(
            keys=keys,
            type=type,
            help_text=help_text,
        )
        self.assertEqual(expected, "{!r}".format(x))

    def new_Argument(self, keys=None, type=None, help_text=None):
        if keys is None:
            keys = ["-o", "--output-file"]
        if type is None:
            type = ArgumentParserSpec.Argument.TYPE_STRING_VALUE

        return ArgumentParserSpec.Argument(
            keys=keys,
            type=type,
            help_text=help_text,
        )
