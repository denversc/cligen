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

import io
import sys
import unittest

import fakeable

from cligen.main_claparser import ArgumentParser
from cligen.targets import TargetLanguageBase
from cligen.targets import TargetRegistry


class TestArgumentParser(unittest.TestCase):

    def test___init___PositionalArgs(self):
        stdout = object()
        x = ArgumentParser(stdout)
        self.assertIs(x.stdout, stdout)

    def test___init___KeywordArgs(self):
        stdout = object()
        x = ArgumentParser(stdout=stdout)
        self.assertIs(x.stdout, stdout)

    def test___init___DefaultArgs(self):
        x = ArgumentParser()
        self.assertIs(x.stdout, sys.stdout)

    def test_exit_PositionalArgs(self):
        x = ArgumentParser()
        with self.assertRaises(x.Error) as cm:
            x.exit(5, "whatever")
        self.assertEqual("{}".format(cm.exception), "whatever")
        self.assertEqual(cm.exception.exit_code, 5)

    def test_exit_KeywordArgs(self):
        x = ArgumentParser()
        with self.assertRaises(x.Error) as cm:
            x.exit(status=6, message="whatever")
        self.assertEqual("{}".format(cm.exception), "whatever")
        self.assertEqual(cm.exception.exit_code, 6)

    def test_exit_DefaultArgs(self):
        x = ArgumentParser()
        with self.assertRaises(x.Error) as cm:
            x.exit()
        self.assertEqual("{}".format(cm.exception), "None")
        self.assertEqual(cm.exception.exit_code, 0)

    def test_error_PositionalArgs(self):
        x = ArgumentParser()
        with self.assertRaises(x.Error) as cm:
            x.error("blah blah")
        self.assertEqual("{}".format(cm.exception), "blah blah")
        self.assertEqual(cm.exception.exit_code, 2)

    def test_error_KeywordArgs(self):
        x = ArgumentParser()
        with self.assertRaises(x.Error) as cm:
            x.error(message="blah blah")
        self.assertEqual("{}".format(cm.exception), "blah blah")
        self.assertEqual(cm.exception.exit_code, 2)


class TestArgumentParser_parse_args(fakeable.FakeableCleanupMixin, unittest.TestCase):

    DEFAULT_VALUE = object()

    def setUp(self):
        super().setUp()
        fakeable.set_fake_class(TargetRegistry, FakeTargetRegistry)

    def test_NoArgs(self):
        self.assert_parse_args_fails([], "-l/--language not specified")

    def test_ExtraPositionalArg(self):
        self.assert_parse_args_fails(["-l", "c", "a", "extra"], "unrecognized arguments: extra")

    def test_Help_Short(self):
        self.assert_help_text_printed(["-h"])

    def test_Help_Long(self):
        self.assert_help_text_printed(["--help"])

    def assert_help_text_printed(self, args):
        stdout = io.StringIO()
        self.assert_parse_args_fails(args, message=None, exit_code=0, stdout=stdout)
        stdout.seek(0)
        help_text = stdout.read()
        self.assertIn("--language", help_text)
        self.assertIn("--output-file", help_text)

    def test_InputFile(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "a.xml"], source_file_path="a.xml")

    def test_Language_Short_C(self):
        self.assert_parse_args_succeeds(["-l", "c"], target_language="c")

    def test_Language_Long_C(self):
        self.assert_parse_args_succeeds(["--language", "c"], target_language="c")

    def test_Language_Short_Java(self):
        self.assert_parse_args_succeeds(["-l", "java"], target_language="java")

    def test_Language_Long_Java(self):
        self.assert_parse_args_succeeds(["--language", "java"], target_language="java")

    def test_Language_Invalid(self):
        self.assert_parse_args_fails(
            ["-l", "invalid"],
            message="invalid value specified for -l/--language: "
            "invalid (valid values are: c, java)")

    def test_OutputFiles_Short(self):
        self.assert_parse_args_succeeds(
            ["-l", "java", "-o", "out.java"],
            target_language="java", output_file_paths=["out.java"])

    def test_OutputFiles_Long(self):
        self.assert_parse_args_succeeds(
            ["-l", "java", "--output-file", "out.java"],
            target_language="java", output_file_paths=["out.java"])

    def test_OutputFiles_1RequiredOutputFile_1GivenOutputFile(self):
        self.assert_parse_args_succeeds(
            ["-l", "java", "-o", "out.java"],
            target_language="java", output_file_paths=["out.java"])

    def test_OutputFiles_1RequiredOutputFile_2GivenOutputFiles(self):
        self.assert_parse_args_fails(
            ["-l", "java", "-o", "out1.java", "-o", "out2.java"],
            message="too many -o/--output-file arguments specified for language Java: 2 (expected 1)")

    def test_OutputFiles_2RequiredOutputFiles_1GivenOutputFile(self):
        self.assert_parse_args_fails(
            ["-l", "c", "-o", "out1.c"],
            message="missing -o/--output-file argument for language C to specify the generated source file")

    def test_OutputFiles_2RequiredOutputFiles_2GivenOutputFiles(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "-o", "out1.h", "-o", "out1.c"],
            target_language="c", output_file_paths=("out1.h", "out1.c"))

    def test_OutputFiles_2RequiredOutputFiles_3GivenOutputFiles(self):
        self.assert_parse_args_fails(
            ["-l", "c", "-o", "out1.c", "-o", "out2.c", "-o", "out3.c"],
            message="too many -o/--output-file arguments specified for language C: 3 (expected 2)")

    def test_Inline(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--inline"],
            inline=True)

    def test_NoInline(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--no-inline"],
            inline=False)

    def test_Inline_NoInline(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--inline", "--no-inline"],
            inline=False)

    def test_Inline_NoInline_Inline(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--inline", "--no-inline", "--inline"],
            inline=True)

    def test_Inline_MultipleOutputFiles(self):
        self.assert_parse_args_fails(
            ["-l", "c", "--inline", "-o", "out.h", "-o", "out.c"],
            message="-o/--output-file was specified 2 times, "
                    "but must be specified 0 or 1 time when --inline is specified")

    def test_Encoding_Short(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "-e", "utf16"],
            encoding="utf16")

    def test_Encoding_Long(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--encoding", "utf16"],
            encoding="utf16")

    def test_Encoding_Invalid(self):
        self.assert_parse_args_fails(
            ["-l", "c", "--encoding", "abcd"],
            message="invalid value specified for -e/--encoding: abcd "
                    "(example valid values are: utf8, utf16, ascii, big5, cp1252, iso-8859-1)")

    def test_DefaultEncoding_NoEncodingSpecified(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--default-encoding"])

    def test_DefaultEncoding_WithEncodingSpecified(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--encoding", "utf16", "--default-encoding"])

    def test_Newline_LF(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--newline", "\\n"],
            newline="\n")

    def test_Newline_CR(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--newline", "\\r"],
            newline="\r")

    def test_Newline_CRLF(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--newline", "\\r\\n"],
            newline="\r\n")

    def test_Newline_Invalid(self):
        self.assert_parse_args_fails(
            ["-l", "c", "--newline", "abc"],
            message="invalid value specified for --newline: abc "
                    "(valid values are: \\n, \\r, \\r\\n)")

    def test_DetectNewline(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--detect-newline"])

    def test_DetectNewline_AfterNewline(self):
        self.assert_parse_args_succeeds(
            ["-l", "c", "--newline", "\\r\\n", "--detect-newline"])

    def assert_parse_args_fails(self, args, message, exit_code=None, stdout=None):
        if exit_code is None:
            exit_code = 2
        if stdout is None:
            stdout = io.StringIO()
        x = ArgumentParser(stdout=stdout)
        with self.assertRaises(x.Error) as cm:
            x.parse_args(args)

        self.assertEqual("{}".format(cm.exception), "{}".format(message))
        self.assertEqual(cm.exception.exit_code, exit_code)

    def assert_parse_args_succeeds(
            self, args,
            target_language=DEFAULT_VALUE,
            source_file_path=DEFAULT_VALUE,
            output_file_paths=DEFAULT_VALUE,
            inline=DEFAULT_VALUE,
            encoding=DEFAULT_VALUE,
            newline=DEFAULT_VALUE,
    ):
        stdout = io.StringIO()
        x = ArgumentParser(stdout=stdout)

        app = x.parse_args(args)

        if target_language is self.DEFAULT_VALUE:
            target_language = x.targets["c"]
        else:
            target_language = x.targets[target_language]

        if source_file_path is self.DEFAULT_VALUE:
            source_file_path = "cligen.xml"

        if output_file_paths is self.DEFAULT_VALUE:
            output_file_paths = None
        else:
            output_file_paths = tuple(output_file_paths)

        if inline is self.DEFAULT_VALUE:
            inline = False

        if encoding is self.DEFAULT_VALUE:
            encoding = None

        if newline is self.DEFAULT_VALUE:
            newline = None

        self.assertIs(app.target_language, target_language)
        self.assertEqual(app.source_file_path, source_file_path)
        self.assertEqual(app.output_file_paths, output_file_paths)
        self.assertIs(app.inline, inline)
        self.assertIs(app.encoding, encoding)
        self.assertEqual(app.newline, newline)


class TestArgumentParser_Error(unittest.TestCase):

    def test___init___PositionalArgs(self):
        with self.assertRaises(ArgumentParser.Error) as cm:
            raise ArgumentParser.Error("message", 0)
        self.assertEqual("{}".format(cm.exception), "message")
        self.assertEqual(cm.exception.exit_code, 0)

    def test___init___KeywordArgs(self):
        with self.assertRaises(ArgumentParser.Error) as cm:
            raise ArgumentParser.Error(message="message", exit_code=0)
        self.assertEqual("{}".format(cm.exception), "message")
        self.assertEqual(cm.exception.exit_code, 0)

    def test_exit_code_0(self):
        with self.assertRaises(ArgumentParser.Error) as cm:
            raise ArgumentParser.Error(message="message", exit_code=0)
        self.assertEqual(cm.exception.exit_code, 0)

    def test_exit_code_1(self):
        with self.assertRaises(ArgumentParser.Error) as cm:
            raise ArgumentParser.Error(message="message", exit_code=1)
        self.assertEqual(cm.exception.exit_code, 1)

    def test_exit_code_2(self):
        with self.assertRaises(ArgumentParser.Error) as cm:
            raise ArgumentParser.Error(message="message", exit_code=2)
        self.assertEqual(cm.exception.exit_code, 2)


class FakeTargets(dict):
    """
    A dict suitable for specifying to the ArgumentsParser constructor for the "targets" argument.
    """

    def __init__(self):
        for fake_language in self.fake_languages():
            self[fake_language.key] = fake_language

    def fake_languages(self):
        yield TargetLanguageBase(key="c", name="C", output_files=(
            TargetLanguageBase.OutputFileInfo(name="header file", default_value="cligen.h"),
            TargetLanguageBase.OutputFileInfo(name="source file", default_value="cligen.c"),
        ))
        yield TargetLanguageBase(key="java", name="Java", output_files=(
            TargetLanguageBase.OutputFileInfo(name="source file", default_value="Cligen.java"),
        ))


class FakeTargetRegistry:

    def load(self):
        return FakeTargets()
