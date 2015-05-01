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

import os
import re

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
        output_files list that was given to __init__(); if None then the default filenames will be
        used for all output files and will be written to the current directory.
        *encoding* must be a string whose value is the character encoding to use in the generated
        files (e.g. "utf8", "ascii"); may be None to use the default "utf8".
        *newline* must be a string whose value is the character sequence to use to create a new
        line in the output file; may be None, in which case the newline sequence will be detected
        from the output file, if it already exists; if it does not exist then the system default
        newline character sequence retrieved from os.linesep will be used.
        Raises self.Error if an error occurs.
        """
        if encoding is None:
            encoding = "utf8"
        output_files = self._resolved_output_files(output_file_paths, encoding, newline)
        output_files = tuple(output_files)
        self._generate(argspec=argspec, encoding=encoding, output_files=output_files)

    def _generate(self, argspec, encoding, output_files):
        """
        To be implemented by subclasses to generate the code.
        This method is called by generate() after validating and resolving its arguments.
        No arguments specified to this method will be None.

        *argspec* is the value for the argument of the same name that was specified to generate().
        *encoding* is a string whose value is the name of the character encoding to use in the
        generated files.
        *output_files* is an iterable of self._OutputFile objects representing the output files.
        Raises self.Error if an error occurs.
        """
        raise NotImplementedError()

    def _resolved_output_files(self, output_file_paths, encoding, newline):
        output_file_infos = tuple(self.output_files)

        if output_file_paths is None:
            output_file_paths = [x.default_value for x in output_file_infos]
        else:
            output_file_paths = tuple(output_file_paths)
            if len(output_file_paths) != len(output_file_infos):
                raise RuntimeError("len(output_file_paths)=={} (expected {})".format(
                    len(output_file_paths), len(output_file_infos)))

        for i in range(len(output_file_infos)):
            path = output_file_paths[i]
            info = output_file_infos[i]
            if newline is not None:
                cur_newline = newline
            else:
                cur_newline = self._detect_newline(path, encoding)

            yield self._OutputFile(
                path=path,
                newline=cur_newline,
                info=info,
            )

    @classmethod
    def _detect_newline(cls, path, encoding):
        """
        Helper method for use by subclasses to determine the newline character sequence in use in
        a given file.  If the file does not exist or contains no newline character sequences then
        os.linesep is returned.  If the file cannot be read then Error is raised.
        """
        try:
            with open(path, "rt", encoding=encoding, newline="") as f:
                for line in f:
                    match = re.search(r"([\r\n]+$)", line)
                    if match is not None:
                        newline = match.group(1)
                        return newline
        except FileNotFoundError:
            return os.linesep
        except IOError as e:
            raise cls.Error(
                "unable to determine newline character sequence in file: {} ({})".format(
                    path, e.strerror))
        except UnicodeDecodeError as e:
            raise cls.Error(
                "unable to decode characters from file using encoding {}: {} ({})".format(
                    encoding, path, e))

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

    class _OutputFile:
        """
        Stores information about an output file.
        Instances of this class will be specified to _generate() by generate().
        """

        def __init__(self, path, newline, info):
            """
            Initializes a new instance of this class.

            *path* must be a string whose value is the path of the output file to generate;
            must not be None.
            *newline* must be a string whose value is the newline character sequence to generate
            in the output file; must not be None.
            *info* must be a OutputFileInfo object that is the output file to which this object
            corresponds; must not be None.
            """
            self.path = path
            self.newline = newline
            self.info = info

    class Error(Exception):
        pass


class Jinja2TargetLanguageBase(TargetLanguageBase):
    """
    An implementation of TargetLanguageBase that generates output files from Jinja2 templates.
    The output_files specified to __init__() must be Jinja2TargetLanguageBase.OutputFileInfo
    objects.
    """

    def argument_variable_name(self, arg):
        """
        Convert an ArgumentParserSpec.Argument to a string that is to be used as the variable name
        in generated code to store the argument's value.
        """
        variable_names = ("".join(s for s in x if s.isalnum()) for x in arg.keys)
        return self._largest_len_in(variable_names)

    def most_descriptive_key(self, arg):
        """
        Select and return the key of an ArgumentParserSpec.Argument object that is the most
        descriptive.  This is the key that should be displayed if only one key can be displayed
        for some reason.  This method simply returns the longest key
        """
        return self._largest_len_in(arg.keys)

    def joined_keys(self, arg):
        """
        Returns a string whose value is all keys of the given argument with "/" between them.
        For example: -i/--input-file
        """
        return "/".join(arg.keys)

    @staticmethod
    def _largest_len_in(seq):
        largest = None
        for s in seq:
            if largest is None or len(s) > len(largest):
                largest = s
        return largest


    def _generate(self, argspec, encoding, output_files):
        env = jinja2.Environment(
            keep_trailing_newline=True,
            autoescape=False,
            lstrip_blocks=True,
            trim_blocks=True,
            undefined=jinja2.StrictUndefined,
            loader=jinja2.PackageLoader("cligen"),
        )

        env.filters["varname"] = self.argument_variable_name
        env.filters["most_descriptive_key"] = self.most_descriptive_key
        env.filters["joined_keys"] = self.joined_keys

        for output_file in output_files:
            self._generate_output_file(
                argspec=argspec,
                env=env,
                template_name=output_file.info.template_name,
                output_file_path=output_file.path,
                output_file_newline=output_file.newline,
                output_file_encoding=encoding,
            )

    def _generate_output_file(
            self, argspec, env, template_name, output_file_path, output_file_encoding,
            output_file_newline):
        template = env.get_template(template_name)
        output = template.render(argspec=argspec)
        output_fixed_newlines = output.replace("\n", output_file_newline)
        try:
            output_fixed_newlines_bytes = output_fixed_newlines.encode(output_file_encoding)
        except UnicodeEncodeError as e:
            raise self.Error(
                "unable to encode generated code using encoding {}: {} ({})".format(
                    output_file_encoding, output_file_path, e
                ))

        try:
            with open(output_file_path, "wb") as f:
                f.write(output_fixed_newlines_bytes)
        except IOError as e:
            raise self.Error("error writing generated code to file: {} ({})".format(
                output_file_path, e.strerror))

    class OutputFileInfo(TargetLanguageBase.OutputFileInfo):

        def __init__(self, name, default_value, template_name):
            super().__init__(name=name, default_value=default_value)
            self.template_name = template_name
