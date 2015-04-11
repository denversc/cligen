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
The main entry point for the cligen command-line utility.
"""

from cligen.main_claparser import ArgumentParser
from cligen.targets import TargetRegistry

import sys


def main():
    try:
        exit_code = run()
    except KeyboardInterrupt:
        print("ERROR: application terminated by keyboard interrupt", file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)


def run():
    target_registry = TargetRegistry()
    targets = target_registry.load()

    arg_parser = ArgumentParser(targets=targets)
    try:
        app = arg_parser.parse_args()
    except arg_parser.Error as e:
        if e.exit_code == 2:
            print("ERROR: invalid command-line arguments: {}".format(e), file=sys.stderr)
            print("Run with --help for help", file=sys.stderr)
        elif e.exit_code != 0:
            print("ERROR: {}".format(e), file=sys.stderr)
        return e.exit_code


if __name__ == "__main__":
    main()
