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
import shutil
import tempfile
import unittest

from cligen.targets import Jinja2TargetLanguageBase
from cligen.argspec import ArgumentParserSpec


class Test_Jinja2TargetLanguageBase_generate(unittest.TestCase):

    # a sentinel object used as a method argument to indicate that the default value should be used
    DEFAULT_VALUE = object()

    def test_NewlineUnix(self):
        self.assert_generate_ok(newline="\n")

    def test_NewlineMac(self):
        self.assert_generate_ok(newline="\r")

    def test_NewlineWindows(self):
        self.assert_generate_ok(newline="\r\n")

    def test_NewlineNone_FileNotFound(self):
        self.assert_generate_ok(newline=None, expected_newline=os.linesep)

    def test_NewlineNone_FileCannotBeRead(self):
        self.assert_generate_fail(
            newline=None,
            output_file_is_directory=True,
            expected_exception_message="unable to determine newline character sequence in file: "
            "{output_file_path} (Is a directory)"
        )

    def test_NewlineNone_FileDecodingFails(self):
        self.assert_generate_fail(
            newline=None,
            output_file_initial_bytes=b"\xc3\x28",
            expected_exception_message="unable to decode characters from file using encoding utf8: "
            "{output_file_path} ('utf-8' codec can't decode byte 0xc3 in position 0: "
            "invalid continuation byte)"
        )

    def test_NewlineNone_Unix(self):
        self.assert_generate_ok(
            newline=None,
            expected_newline="\n",
            output_file_initial_contents="ab\ncd\n",
        )

    def test_NewlineNone_Mac(self):
        self.assert_generate_ok(
            newline=None,
            expected_newline="\r",
            output_file_initial_contents="ab\rcd\r",
        )

    def test_NewlineNone_Windows(self):
        self.assert_generate_ok(
            newline=None,
            expected_newline="\r\n",
            output_file_initial_contents="ab\r\ncd\r\n",
        )

    def test_NewlineNone_ConfoundingSpaces(self):
        self.assert_generate_ok(
            newline=None,
            expected_newline="\r\n",
            output_file_initial_contents="This line has trailing spaces   \r\nLine 2   \r\n",
        )

    def test_NewlineNone_InconsistentNewlines(self):
        self.assert_generate_ok(
            newline=None,
            expected_newline="\r\n",
            output_file_initial_contents="Windows\r\nMac\rLinux\n",
        )

    def test_Encoding_None(self):
        self.assert_generate_ok(encoding=None, effective_encoding="utf8")

    def test_Encoding_UTF8(self):
        self.assert_generate_ok(encoding="utf8")

    def test_Encoding_UTF16(self):
        self.assert_generate_ok(encoding="utf16")

    def test_Encoding_ASCII(self):
        self.assert_generate_ok(encoding="ascii")

    def test_Encoding_UTF8_SpecialChars(self):
        x = self.sample_Jinja2TargetLanguageBase_nonascii()
        expected_generated_code = self.generated_test_nonascii_txt()
        self.assert_generate_ok(x=x, expected_generated_code=expected_generated_code)

    def test_Encoding_ASCII_SpecialChars(self):
        x = self.sample_Jinja2TargetLanguageBase_nonascii()
        self.assert_generate_fail(
            x=x,
            encoding="ascii",
            expected_exception_message="unable to encode generated code using encoding ascii: "
            r"{output_file_path} ('ascii' codec can't encode character '\xe9' in position 1: "
            "ordinal not in range(128))"
        )

    def test_OutputFiles_None(self):
        dir_path = self.create_temp_dir()
        old_cwd = os.getcwd()
        self.addCleanup(os.chdir, old_cwd)
        os.chdir(dir_path)

        x = self.sample_Jinja2TargetLanguageBase()
        x.generate(
            argspec=self.sample_argspec(),
            output_file_paths=None,
            encoding="utf8",
            newline="\n",
        )

        with open("test.generated.txt", "rb") as f:
            output_file_bytes = f.read()
        actual_output_file_contents = output_file_bytes.decode("utf8")
        expected_output_file_contents = self.generated_test_txt()
        self.assertEqual(actual_output_file_contents, expected_output_file_contents)

    def test_OutputFiles_NoOutputFilesSpecified(self):
        self.assert_generate_raises_RuntimeError(
            output_file_paths=[],
            expected_message="len(output_file_paths)==0 (expected 1)",
        )

    def test_OutputFiles_TooManyOutputFilesSpecified(self):
        self.assert_generate_raises_RuntimeError(
            output_file_paths=[1, 2],
            expected_message="len(output_file_paths)==2 (expected 1)",
        )

    def assert_generate_raises_RuntimeError(self, output_file_paths, expected_message):
        x = self.sample_Jinja2TargetLanguageBase()
        with self.assertRaises(RuntimeError) as cm:
            x.generate(
                argspec=None,
                encoding=None,
                newline=None,
                output_file_paths=output_file_paths,
            )

        actual_message = "{}".format(cm.exception)
        self.assertEqual(actual_message, expected_message)

    def test_OutputFiles_MultipleOutputFiles(self):
        x = self.sample_Jinja2TargetLanguageBase_MultipleOutputFiles()
        argspec = self.sample_argspec()

        dir_path = self.create_temp_dir()
        output_file_path_1 = os.path.join(dir_path, "test1.txt")
        output_file_path_2 = os.path.join(dir_path, "test2.txt")
        output_file_paths = [output_file_path_1, output_file_path_2]

        x.generate(
            argspec=argspec,
            output_file_paths=output_file_paths,
            encoding="utf8",
            newline="\n",
        )

        with open(output_file_path_1, "rb") as f:
            output_file_1_bytes = f.read()
        actual_output_file_1_contents = output_file_1_bytes.decode("utf8")
        expected_output_file_1_contents = self.generated_test_txt()
        self.assertEqual(actual_output_file_1_contents, expected_output_file_1_contents)

        with open(output_file_path_2, "rb") as f:
            output_file_2_bytes = f.read()
        actual_output_file_2_contents = output_file_2_bytes.decode("utf8")
        expected_output_file_2_contents = self.generated_test2_txt()
        self.assertEqual(actual_output_file_2_contents, expected_output_file_2_contents)

    def test_OutputFiles_MultipleOutputFilesWithDifferentNewlines_NewlineNone(self):
        x = self.sample_Jinja2TargetLanguageBase_MultipleOutputFiles()
        argspec = self.sample_argspec()

        dir_path = self.create_temp_dir()
        output_file_path_1 = os.path.join(dir_path, "test1.txt")
        output_file_path_2 = os.path.join(dir_path, "test2.txt")
        output_file_paths = [output_file_path_1, output_file_path_2]

        with open(output_file_path_1, "wb") as f:
            f.write("line 1\n line 2\n".encode("utf8"))
        with open(output_file_path_2, "wb") as f:
            f.write("line 1\r\n line 2\r\n".encode("utf8"))

        x.generate(
            argspec=argspec,
            output_file_paths=output_file_paths,
            encoding="utf8",
            newline=None,
        )

        with open(output_file_path_1, "rb") as f:
            output_file_1_bytes = f.read()
        actual_output_file_1_contents = output_file_1_bytes.decode("utf8")
        expected_output_file_1_contents = self.generated_test_txt(newline="\n")
        self.assertEqual(actual_output_file_1_contents, expected_output_file_1_contents)

        with open(output_file_path_2, "rb") as f:
            output_file_2_bytes = f.read()
        actual_output_file_2_contents = output_file_2_bytes.decode("utf8")
        expected_output_file_2_contents = self.generated_test2_txt(newline="\r\n")
        self.assertEqual(actual_output_file_2_contents, expected_output_file_2_contents)

    def assert_generate_ok(
            self,
            x=DEFAULT_VALUE,
            encoding=DEFAULT_VALUE,
            newline=DEFAULT_VALUE,
            expected_newline=DEFAULT_VALUE,
            output_file_initial_contents=DEFAULT_VALUE,
            expected_generated_code=DEFAULT_VALUE,
            effective_encoding=DEFAULT_VALUE,
    ):
        if x is self.DEFAULT_VALUE:
            x = self.sample_Jinja2TargetLanguageBase()
        if encoding is self.DEFAULT_VALUE:
            encoding = "utf8"
        if newline is self.DEFAULT_VALUE:
            newline = "\n"
        if expected_newline is self.DEFAULT_VALUE:
            expected_newline = newline
        if output_file_initial_contents is self.DEFAULT_VALUE:
            output_file_initial_contents = None
        if effective_encoding is self.DEFAULT_VALUE:
            effective_encoding = encoding

        dir_path = self.create_temp_dir()
        output_file_path = os.path.join(dir_path, "test.txt")
        if output_file_initial_contents is not None:
            with open(output_file_path, "wb") as f:
                f.write(output_file_initial_contents.encode(encoding))

        argspec = self.sample_argspec()
        x.generate(
            argspec=argspec,
            output_file_paths=[output_file_path],
            encoding=encoding,
            newline=newline,
        )

        with open(output_file_path, "rb") as f:
            actual_generated_code_bytes = f.read()

        if expected_generated_code is self.DEFAULT_VALUE:
            expected_generated_code = self.generated_test_txt(newline=expected_newline)
        actual_generated_code = actual_generated_code_bytes.decode(effective_encoding)
        self.assertEqual(actual_generated_code, expected_generated_code)

    def assert_generate_fail(
            self,
            x=DEFAULT_VALUE,
            encoding=DEFAULT_VALUE,
            newline=DEFAULT_VALUE,
            expected_exception_message=None,
            output_file_is_directory=DEFAULT_VALUE,
            output_file_initial_bytes=DEFAULT_VALUE,
    ):
        if x is self.DEFAULT_VALUE:
            x = self.sample_Jinja2TargetLanguageBase()
        if encoding is self.DEFAULT_VALUE:
            encoding = "utf8"
        if newline is self.DEFAULT_VALUE:
            newline = "\n"
        if output_file_is_directory is self.DEFAULT_VALUE:
            output_file_is_directory = False
        if output_file_initial_bytes is self.DEFAULT_VALUE:
            output_file_initial_bytes = None

        argspec = self.sample_argspec()

        dir_path = self.create_temp_dir()
        if output_file_is_directory:
            output_file_path = dir_path
        else:
            output_file_path = os.path.join(dir_path, "test.txt")
            if output_file_initial_bytes is not None:
                with open(output_file_path, "wb") as f:
                    f.write(output_file_initial_bytes)

        with self.assertRaises(x.Error) as cm:
            x.generate(
                argspec=argspec,
                output_file_paths=[output_file_path],
                encoding=encoding,
                newline=newline,
            )

        if expected_exception_message is not None:
            actual_exception_message = "{}".format(cm.exception)
            expected_exception_message_formatted = expected_exception_message.format(
                output_file_path=output_file_path,
            )
            self.assertEqual(actual_exception_message, expected_exception_message_formatted)

    def create_temp_dir(self):
        path = tempfile.mkdtemp("Test_Jinja2TargetLanguageBase_generate")
        self.addCleanup(shutil.rmtree, path)
        return path

    @staticmethod
    def sample_argspec():
        arg1 = ArgumentParserSpec.Argument(keys=("-i", "--input-file"))
        arg2 = ArgumentParserSpec.Argument(keys=("-o", "--output-file"))
        return ArgumentParserSpec(arguments=(arg1, arg2))

    @staticmethod
    def sample_Jinja2TargetLanguageBase():
        output_file = Jinja2TargetLanguageBase.OutputFileInfo(
            name="test",
            default_value="test.generated.txt",
            template_name="test.txt",
        )
        return Jinja2TargetLanguageBase(
            key="test",
            name="test",
            output_files=[output_file],
        )

    @staticmethod
    def sample_Jinja2TargetLanguageBase_nonascii():
        output_file = Jinja2TargetLanguageBase.OutputFileInfo(
            name="test_nonascii",
            default_value="test.nonascii.generated.txt",
            template_name="test.nonascii.txt",
        )
        return Jinja2TargetLanguageBase(
            key="test_nonascii",
            name="test_nonascii",
            output_files=[output_file],
        )

    @staticmethod
    def sample_Jinja2TargetLanguageBase_MultipleOutputFiles():
        output_file_1 = Jinja2TargetLanguageBase.OutputFileInfo(
            name="test1",
            default_value="test1.generated.txt",
            template_name="test.txt",
        )
        output_file_2 = Jinja2TargetLanguageBase.OutputFileInfo(
            name="test2",
            default_value="test2.generated.txt",
            template_name="test2.txt",
        )
        return Jinja2TargetLanguageBase(
            key="test",
            name="test",
            output_files=[output_file_1, output_file_2],
        )

    @staticmethod
    def generated_test_txt(newline=None):
        s = (
            "The arguments are:\n"
            "Argument 1: -i/--input-file\n"
            "varname: inputfile\n"
            "most_descriptive_key: --input-file\n"
            "Argument 2: -o/--output-file\n"
            "varname: outputfile\n"
            "most_descriptive_key: --output-file\n"
        )
        if newline is not None:
            s = s.replace("\n", newline)
        return s

    @staticmethod
    def generated_test2_txt(newline=None):
        s = (
            "test2.txt begin\n"
            "The arguments are:\n"
            "Argument 1: -i/--input-file\n"
            "Argument 2: -o/--output-file\n"
            "test2.txt end\n"
        )
        if newline is not None:
            s = s.replace("\n", newline)
        return s

    @staticmethod
    def generated_test_nonascii_txt(newline=None):
        s = "Héllô\n"
        if newline is not None:
            s = s.replace("\n", newline)
        return s
