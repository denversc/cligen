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
import jinja2


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

    def generate(self, argspec, output_file_paths, encoding, newline):
        """
        Generates the output files based on the given input.
        *argspec* must be a cligen.argspec.ArgumentParserSpec object that specifies the command-
        line arguments that the generated code is to parse.
        *output_file_paths* the paths of the output files to write, corresponding to the
        output_files list that was given to __init__(); if the length of this list is zero then
        the default filenames will be used for all output files.
        *encoding* must be a string whose value is the character encoding to use in the generated
        files (e.g. "utf8", "ascii").
        *newline* must be a string whose value is the character sequence to use to create a new
        line in the output file; may be None, in which case the newline sequence will be detected
        from the output file, if it already exists; if it does not exist then \n will be used.
        Raises self.Error if an error occurs.
        """
        raise NotImplementedError()

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

    class Error(Exception):
        pass


class Jinja2TargetLanguageBase(TargetLanguageBase):
    """
    An implementation of TargetLanguageBase that generates output files from Jinja2 templates.
    The output_files specified to __init__() must be Jinja2TargetLanguageBase.OutputFileInfo
    objects.
    """

    def generate(self, argspec, output_file_paths, encoding, newline):
        if newline is None:
            # TODO: try and determine the newline used in the output file
            newline = "\n"

        env = jinja2.Environment(
            newline_sequence=newline,
            keep_trailing_newline=True,
            autoescape=False,
            lstrip_blocks=True,
            trim_blocks=True,
            undefined=jinja2.StrictUndefined,
            loader=jinja2.PackageLoader("cligen"),
        )

        output_files = tuple(self.output_files)
        output_file_paths = tuple(output_file_paths)
        if len(output_file_paths) == 0:
            output_file_paths = tuple(x.default_value for x in output_files)
        elif len(output_file_paths) != len(output_files):
            raise RuntimeError("invalid output_file_paths length: {} (expected {})".format(
                len(output_file_paths), len(output_files)))

        for (output_file_path, output_file) in zip(output_file_paths, output_files):
            template_name = output_file.template_name
            self._generate(env, template_name, argspec, output_file_path, encoding)

    def _generate(self, env, template_name, argspec, output_file_path, output_file_encoding):
        template = env.get_template(template_name)
        generated_code = template.render(argspec=argspec)
        generated_code_bytes = generated_code.encode(output_file_encoding)

        try:
            with open(output_file_path, "wb") as f:
                f.write(generated_code_bytes)
        except IOError as e:
            raise self.Error("error writing generated code to file: {} ({})".format(
                output_file_path, e.strerror))

    class OutputFileInfo(TargetLanguageBase.OutputFileInfo):

        def __init__(self, name, default_value, template_name):
            super().__init__(name=name, default_value=default_value)
            self.template_name = template_name
