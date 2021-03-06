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
Python target language support for cligen.
"""

from cligen.targets import Jinja2TargetLanguageBase


class PythonTargetLanguage(Jinja2TargetLanguageBase):

    def __init__(self):
        output_file = self.OutputFileInfo(
            name="source file",
            default_value="cligen.py",
            template_name="python.py",
        )

        super().__init__(
            key="python",
            name="python",
            output_files=(output_file,),
        )
