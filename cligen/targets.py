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
Registry for supported target languages for cligen.
"""

import fakeable


class TargetRegistry(metaclass=fakeable.Fakeable):

    def __init__(self):
        self.targets = {}

    def load(self):
        return {x.key: x for x in self._load_targets()}

    def _load_targets(self):
        import cligen.target_c
        yield cligen.target_c.CTargetLanguage()
        import cligen.target_java
        yield cligen.target_java.JavaTargetLanguage()
        import cligen.target_python
        yield cligen.target_python.PythonTargetLanguage()


class TargetLanguageBase:

    def __init__(self, key, name, output_files):
        """
        Iniitalizes a new instance of TargetLanguageBase.
        *key* must be a string whose value is a short, unique string to identify this language;
        the primary use for this value is specifying a target in the command-line arguments.
        *name* must be a string whose value is a human friendly name for the target language
        produced by this object; this value will be displayed to the user in help messages and
        should use "title case" (e.g. "Java", "Python", "C++").
        *output_files* must be a tuple of OutputFileInfo objects, each of which describes an output
        file produced by this object's generate() method; the length of this tuple must be equal to
        the number of elements of the output_file_paths argument to generate().
        """
        self.key = key
        self.name = name
        self.output_files = output_files

    class OutputFileInfo:

        def __init__(self, name, default_value):
            """
            Stores information about an output file produced by a target language.
            *name* must be a string whose value is a short description of this output file for
            display to users (e.g. "source file", "header file").
            *default_value* must be a string whose value is the default value to use for this output
            file if not explicitly specified.
            """
            self.name = name
            self.default_value = default_value
