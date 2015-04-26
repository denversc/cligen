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
                ArgumentParserSpec.Argument(keys=["-o", "--output-file"]),
                ArgumentParserSpec.Argument(keys=["-i", "--input-file"]),
            ]

        return ArgumentParserSpec(
            arguments=arguments,
        )


class Test_ArgumentSpecParser_Argument(unittest.TestCase):

    def test___init___PositionalArgs(self):
        keys = object()
        x = ArgumentParserSpec.Argument(keys)
        self.assertIs(keys, x.keys)

    def test___init___KeywordArgs(self):
        keys = object()
        x = ArgumentParserSpec.Argument(keys=keys)
        self.assertIs(keys, x.keys)

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

    def new_Argument(self, keys=None):
        if keys is None:
            keys = ["-o", "--output-file"]

        return ArgumentParserSpec.Argument(
            keys=keys,
        )
