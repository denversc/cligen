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

    def test___init___PositionalArgs(self):
        arguments = object()
        x = ArgumentParserSpec(arguments)
        self.assertIs(arguments, x.arguments)

    def test___init___KeywordArgs(self):
        arguments = object()
        x = ArgumentParserSpec(arguments=arguments)
        self.assertIs(arguments, x.arguments)

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

    def new_ArgumentParserSpec(self, arguments=None):
        if arguments is None:
            arguments = [
                ArgumentParserSpec.Argument(names=["-o", "--output-file"]),
                ArgumentParserSpec.Argument(names=["-i", "--input-file"]),
            ]

        return ArgumentParserSpec(
            arguments=arguments,
        )


class Test_ArgumentSpecParser_Argument(unittest.TestCase):

    def test___init___PositionalArgs(self):
        names = object()
        x = ArgumentParserSpec.Argument(names)
        self.assertIs(names, x.names)

    def test___init___KeywordArgs(self):
        names = object()
        x = ArgumentParserSpec.Argument(names=names)
        self.assertIs(names, x.names)

    def test___eq___Equal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        self.assertTrue(x1 == x2)

    def test___eq___names_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.names
        self.assertFalse(x1 == x2)

    def test___eq___names_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(names=[])
        self.assertFalse(x1 == x2)

    def test___ne___Equal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        self.assertFalse(x1 != x2)

    def test___ne___names_Missing(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument()
        del x2.names
        self.assertTrue(x1 != x2)

    def test___ne___names_Unequal(self):
        x1 = self.new_Argument()
        x2 = self.new_Argument(names=[])
        self.assertTrue(x1 != x2)

    def new_Argument(self, names=None):
        if names is None:
            names = ["-o", "--output-file"]

        return ArgumentParserSpec.Argument(
            names=names,
        )
