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
A class that contains a specification for a command-line arguments parser produced by cligen.
"""


class ArgumentParserSpec:

    def __init__(self, arguments, help_argument):
        """
        Initializes a new instance of ArgumentParserSpec.
        *arguments* must be a list or tuple containing ArgumentParserSpec.Argument objects, and
        lists the arguments in this parser specification.
        *help_argument* must be one of the arguments from the given *arguments* that,
        when specified, will print the help screen; may be None if no help argument exists.
        """
        self.arguments = arguments
        self.help_argument = help_argument

    def __eq__(self, other):
        try:
            other_arguments = other.arguments
            other_help_argument = other.help_argument
        except AttributeError:
            return False
        else:
            return (
                self.arguments == other_arguments
                and self.help_argument == other_help_argument
            )

    def __ne__(self, other):
        return not self.__eq__(other)

    class Argument:

        def __init__(self, keys):
            """
            Initializes a new instance of this class.
            *keys* must be a list or tuple of strings, each of which defines the keys that map to
            this argument when specified on the command line (e.g. ["-o", "--output-file"]).
            """
            self.keys = keys

        def __eq__(self, other):
            try:
                other_keys = other.keys
            except AttributeError:
                return False
            else:
                return self.keys == other_keys

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            return "/".join(self.keys)

        def __repr__(self):
            return "Argument(keys={0.keys!r})".format(self)
