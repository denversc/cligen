#!/usr/bin/env python

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
Runs the common language tests against one or more languages.
"""

import argparse
import configparser
import importlib
import io
import pathlib
import subprocess
import sys
import tempfile


def main():
    args = parse_arguments()
    compilers = load_compilers_config(args.compilers_config_file)
    for language in args.language:
        run_tests(language, compilers, args.tests_directory)


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "language",
        nargs="+",
        default=[],
        help="""The target language to test; must be specified at least one and may be specified
        multiple times; all compilers configured for the given target language will be tested,
        unless a specific compiler is specified by having the language be followed by a colon
        character then the name of the compiler (e.g. python:python2)"""
    )

    parser.add_argument(
        "-c", "--compilers-config-file",
        default="compilers.cfg",
        help="""The file that specifies the compilers to test (default: %(default)s)"""
    )

    parser.add_argument(
        "--tests-directory",
        default="tests",
        help="""The directory containing the tests to execute (default: %(default)s)"""
    )

    return parser.parse_args()


def run_tests(language, compilers, tests_dir_path):
    if ":" in language:
        colon_index = language.index(":")
        compiler_name = language[colon_index+1:]
        language_name = language[:colon_index]
    else:
        language_name = language
        compiler_name = None

    try:
        language_compilers = compilers[language_name]
    except KeyError:
        raise Exception("no compilers configured for language: {}".format(language_name))

    if compiler_name is None:
        compiler_names = list(language_compilers)
    else:
        compiler_names = [compiler_name]

    language_module_name = "{}.tester".format(language_name)
    language_module = importlib.import_module(language_module_name)
    tester_class = language_module.Tester
    tests_dir = pathlib.Path(tests_dir_path)
    test_loader = TestLoader()

    for compiler_name in compiler_names:
        print("Testing language={} compiler={}".format(language_name, compiler_name))
        try:
            compiler_path = language_compilers[compiler_name]
        except KeyError:
            raise Exception("compiler for language \"{}\" not found: {}".format(
                language_name, compiler_name))

        for test_file in tests_dir.iterdir():
            if not test_file.is_file():
                continue
            print("   {}".format(test_file.name))

            (spec_xml, arguments, expected_stdout, expected_stderr, expected_exit_code) = \
                test_loader.load(test_file)
            with tempfile.TemporaryDirectory() as temp_dir_path_string:
                temp_dir_path = pathlib.Path(temp_dir_path_string)
                spec_xml_path = temp_dir_path / "cligen.xml"
                with spec_xml_path.open("wt", encoding="utf8") as f:
                    f.write(spec_xml)

                tester = tester_class(
                    compiler_path=compiler_path,
                    spec_xml_path=spec_xml_path,
                    work_dir_path=temp_dir_path,
                )

                cligen_language = tester.cligen_language()
                cligen_output_file_paths = tester.cligen_output_files()
                run_cligen(cligen_language, cligen_output_file_paths, spec_xml_path)

                test_executable_args = tester.create_executable(cligen_output_file_paths)
                test_executable_args = list(test_executable_args)
                test_executable_args.extend(arguments)

                stdout_path = temp_dir_path / "stdout.txt"
                stderr_path = temp_dir_path / "stderr.txt"
                with stdout_path.open("wb") as stdout_file:
                    with stderr_path.open("wb") as stderr_file:
                        try:
                            process = subprocess.Popen(
                                test_executable_args, stdout=stdout_file, stderr=stderr_file)
                        except OSError as e:
                            raise Exception(
                                "unable to run test {}: unable to start process {}: {}".format(
                                    test_file.name, test_executable_args[0], e.strerror))
                        else:
                            exit_code = process.wait()

                with stdout_path.open("rt", encoding="utf8") as f:
                    actual_stdout = f.read().strip()
                with stderr_path.open("rt", encoding="utf8") as f:
                    actual_stderr = f.read().strip()

                if actual_stderr != expected_stderr:
                    print("====== BEGIN ACTUAL STDOUT ======")
                    print(actual_stderr)
                    print("====== END ACTUAL STDOUT ======")
                    print("====== BEGIN EXPECTED STDOUT ======")
                    print(expected_stderr)
                    print("====== END EXPECTED STDOUT ======")
                    raise Exception("incorrect stderr output")

                if actual_stdout != expected_stdout:
                    print("====== BEGIN ACTUAL STDOUT ======")
                    print(actual_stdout)
                    print("====== END ACTUAL STDOUT ======")
                    print("====== BEGIN EXPECTED STDOUT ======")
                    print(expected_stdout)
                    print("====== END EXPECTED STDOUT ======")
                    raise Exception("incorrect stdout output")

                if exit_code != expected_exit_code:
                    raise Exception("incorrect exit code: {} (expected {})".format(
                        exit_code, expected_exit_code))


def load_compilers_config(path):
    parser = configparser.ConfigParser()
    parser.read(path)

    compilers = {}
    for language_name in parser.sections():
        language_compilers = {}
        compilers[language_name] = language_compilers
        for compiler_name in parser[language_name]:
            compiler_path = parser[language_name][compiler_name]
            language_compilers[compiler_name] = compiler_path

    return compilers


class TestLoader:

    def load(self, path):
        spec_xml = None
        arguments = None
        expected_exit_code = None
        expected_stdout = ""
        expected_stderr = ""

        with path.open("rt", encoding="utf8") as f:
            lines = iter(f)
            line = None
            while True:
                if line is None:
                    try:
                        line = next(lines)
                    except StopIteration:
                        break

                line = line.strip()
                if line == "[spec]":
                    (spec_xml, line) = self.parse_text_blob(f)
                elif line == "[arguments]":
                    (arguments, line) = self.parse_arguments(f)
                elif line == "[stdout]":
                    (expected_stdout, line) = self.parse_text_blob(f)
                elif line == "[stderr]":
                    (expected_stderr, line) = self.parse_text_blob(f)
                elif line == "[exit code]":
                    (expected_exit_code, line) = self.parse_exit_code(f)
                else:
                    raise Exception("syntax error: {}".format(line))

        if spec_xml is None:
            raise Exception("[spec] section missing")
        elif arguments is None:
            raise Exception("[arguments] section missing")
        elif expected_exit_code is None:
            raise Exception("[exit code] section missing")

        return (spec_xml, arguments, expected_stdout.strip(), expected_stderr.strip(), expected_exit_code)

    def parse_text_blob(self, f):
        out = io.StringIO()
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith("["):
                return (out.getvalue(), line)
            out.write(line)

        return (out.getvalue(), None)

    def parse_arguments(self, f):
        arguments = []
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith("["):
                return (arguments, line)
            elif len(line_stripped) > 0:
                arguments.append(line_stripped)

        return (arguments, None)

    def parse_exit_code(self, f):
        exit_code = None
        for line in f:
            line_stripped = line.strip()
            if line_stripped.startswith("["):
                if exit_code is None:
                    raise Exception("no exit code specified in [exit code] section")
                return (exit_code, line)
            elif len(line_stripped) > 0:
                if exit_code is not None:
                    raise Exception("exit code specified more than once in [exit code] section")
                exit_code = int(line_stripped)

        if exit_code is None:
            raise Exception("no exit code specified in [exit code] section")
        return (exit_code, None)


def run_cligen(language, output_file_paths, cligen_xml_path):
    args = [
        sys.executable,
        "-m",
        "cligen",
        "--language",
        language,
    ]

    for output_file_path in output_file_paths:
        args.append("--output-file")
        args.append(output_file_path)

    args.append("{}".format(cligen_xml_path))

    try:
        process = subprocess.Popen(args)
    except OSError as e:
        raise Exception("unable to start process: {} ({})".format(args[0], e.strerror))
    else:
        exit_code = process.wait()

    if exit_code != 0:
        raise Exception("command completed with non-zero exit code {}: {}".format(
            exit_code, subprocess.list2cmdline(args)))


if __name__ == "__main__":
    main()
