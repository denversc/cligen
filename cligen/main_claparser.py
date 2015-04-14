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
The command-line arguments parser for the cligen command-line utility.
"""

import argparse
import codecs
import collections

from cligen.main_app import CligenApplication


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, targets):
        super().__init__(usage="%(prog)s [options] <input_file>")
        self.targets = targets
        self._add_arguments()

    def _add_arguments(self):
        self.arg_source_file = self.add_argument(
            "source_file",
            default="cligen.xml",
            nargs="?",
            help="""The cligen specification file to compile (default: %(default)s)"""
        )

        self.arg_output_files = self.add_argument(
            "-o", "--output-file",
            action="append",
            dest="output_files",
            help="""The file to which to write the command-line arguments parser;
            some target languages require more than one output file, in which case this argument
            must be specified multiple times;
            if not specified, default values specific to the target language will be used"""
        )

        self.arg_language = self.add_argument(
            "-l", "--language",
            help="""The target language whose command-line arguments parser to generate;
            valid values are: {}""".format(", ".join(sorted(self.targets)))
        )

        self.arg_inline = self.add_argument(
            "--inline",
            action="store_true",
            default=False,
            help="""Insert the generated code into an existing file instead of creating a new
            file or new files;
            a target-language-specific begin and end comment pair must exist in the output file
            to indicate where the parsing code should be placed;
            any code between the begin and end comments will be replaced by the generated code"""
        )

        self.arg_no_inline = self.add_argument(
            "--no-inline",
            dest="inline",
            action="store_false",
            help="""Reverse the effects of {} if previously specified"""
                .format("/".join(self.arg_inline.option_strings))
        )

        self.example_valid_encodings = ("utf8", "utf16", "ascii", "big5", "cp1252", "iso-8859-1")
        self.arg_encoding = self.add_argument(
            "-e", "--encoding",
            help="""The character encoding to use when reading from and writing to files;
            valid values are: {}, and any other character encoding
            recognized by the Python interpreter (default: utf8)"""
            .format(", ".join(self.example_valid_encodings))
        )

        self.arg_default_encoding = self.add_argument(
            "--default-encoding",
            action="store_const",
            const=None,
            dest="encoding",
            help="""Reverse the effects of {} if previously specified"""
                .format("/".join(self.arg_encoding.option_strings))
        )

        self.newline_names = collections.OrderedDict((
            ("\\n", "\n"),
            ("\\r", "\r"),
            ("\\r\\n", "\r\n"),
        ))
        self.arg_newline = self.add_argument(
            "--newline",
            help="""The character sequence to use in generated code to insert a line break;
            if not specified then the newline character will be detected from the output file if
            it already exists or \\n will be used; valid values are: {}"""
            .format(", ".join(self.newline_names))
        )

        self.arg_detect_newline = self.add_argument(
            "--detect-newline",
            action="store_const",
            const=None,
            dest="newline",
            help="""Reverse the effects of {} if previously specified"""
                .format("/".join(self.arg_encoding.option_strings))
        )

    def parse_args(self, args=None):
        namespace = self.Namespace(self)
        super().parse_args(args=args, namespace=namespace)
        app = namespace.create_application()
        return app

    def exit(self, status=0, message=None):
        raise self.Error(message=message, exit_code=status)

    def error(self, message):
        self.exit(status=2, message=message)

    class Namespace(argparse.Namespace):

        def __init__(self, parser):
            self.parser = parser

        def create_application(self):
            source_file_path = self.source_file
            target_language = self.get_target_language()
            inline = self.inline
            output_file_paths = self.get_output_files(target_language, inline)
            encoding = self.get_encoding()
            newline = self.get_newline()

            return CligenApplication(
                source_file_path=source_file_path,
                output_file_paths=output_file_paths,
                target_language=target_language,
                inline=inline,
                encoding=encoding,
                newline=newline,
            )

        def get_output_files(self, target_language, inline):
            output_files = self.output_files
            if output_files is None or len(output_files) == 0:
                return None

            output_files = tuple(output_files)
            if inline:
                if len(output_files) > 1:
                    self.parser.error(
                        "{} was specified {} times, but must be specified 0 or 1 time when "
                        "{} is specified".format(
                            "/".join(self.parser.arg_output_files.option_strings),
                            len(output_files),
                            "/".join(self.parser.arg_inline.option_strings)))
            elif len(output_files) < len(target_language.output_files):
                self.parser.error(
                    "missing {} argument for language {} to specify the generated {}".format(
                        "/".join(self.parser.arg_output_files.option_strings),
                        target_language.name, target_language.output_files[len(output_files)].name))
            elif len(output_files) > len(target_language.output_files):
                self.parser.error(
                    "too many {} arguments specified for language {}: {} (expected {})".format(
                        "/".join(self.parser.arg_output_files.option_strings),
                        target_language.name, len(output_files), len(target_language.output_files)))

            return output_files

        def get_target_language(self):
            target_language_key = self.language
            if target_language_key is None:
                self.parser.error("{} not specified".format(
                    "/".join(self.parser.arg_language.option_strings)))

            try:
                return self.parser.targets[target_language_key]
            except KeyError:
                    self.parser.error("invalid value specified for {}: {} (valid values are: {})"
                        .format(
                            "/".join(self.parser.arg_language.option_strings), target_language_key,
                        ", ".join(sorted(self.parser.targets))))

        def get_encoding(self):
            encoding = self.encoding
            if encoding is not None:
                try:
                    codecs.lookup(encoding)
                except LookupError:
                    self.parser.error("invalid value specified for {}: {} "
                        "(example valid values are: {})".format(
                            "/".join(self.parser.arg_encoding.option_strings), encoding,
                            ", ".join(self.parser.example_valid_encodings)))
            return encoding

        def get_newline(self):
            newline_name = self.newline
            if newline_name is None:
                return None
            elif newline_name in self.parser.newline_names:
                return self.parser.newline_names[newline_name]
            else:
                self.parser.error("invalid value specified for {}: {} (valid values are: {})"
                    .format(
                        "/".join(self.parser.arg_newline.option_strings),
                        newline_name,
                        ", ".join(self.parser.newline_names)))

    class Error(Exception):

        def __init__(self, message, exit_code):
            super().__init__(message)
            self.exit_code = exit_code
