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

    def test_EncodingUTF8_NewlineUnix_OutputFileDoesNotExist(self):
        x = self.sample_Jinja2TargetLanguageBase()
        argspec = self.sample_argspec()
        dir_path = self.create_temp_dir()
        output_file_path = os.path.join(dir_path, "test.txt")
        x.generate(
            argspec=argspec,
            output_file_paths=[output_file_path],
            encoding="utf8",
            newline="\n",
        )

        with open(output_file_path, "rt", encoding="utf8") as f:
            generated_code = f.read()

        self.assertEqual(
            generated_code,
            "The arguments are:\n"
            "Argument 1: -i/--input-file\n"
            "Argument 2: -o/--output-file\n"
        )

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
