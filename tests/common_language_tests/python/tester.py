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
Runs the common language tests for Python
"""


class Tester:

    def __init__(self, compiler_path, spec_xml_path, work_dir_path):
        self.compiler_path = compiler_path
        self.spec_xml_path = spec_xml_path
        self.work_dir_path = work_dir_path

    def cligen_language(self):
        return "python"

    def cligen_output_files(self):
        output_path = self.work_dir_path / "test.py"
        output_path_str = "{}".format(output_path)
        return [output_path_str]

    def create_executable(self, output_file_paths):
        args = [
            self.compiler_path,
        ]
        args.extend(output_file_paths)
        return args
