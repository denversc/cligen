#!/usr/bin/env python

# These "future" imports increase compatibility between Python 2 and Python 3
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys


class ArgumentParser(object):
    """
    Parses command-line arguments.
    Simply invoke the parse() method of this class to parse the arguments and return the result
    """

    def __init__(self, stdout=None, stderr=None):
        """
        Initializes a new instance of this class.

        *stdout* must be a file opened in write-text mode to which any "standard output" output
        generated by this object will be written; may be None (the default) to use sys.stdout.
        *stderr* must be a file opened in write-text mode to which any "standard output" output
        generated by this object will be written; may be None (the default) to use sys.stderr.
        """
        self.stdout = stdout if stdout is not None else sys.stdout
        self.stderr = stderr if stderr is not None else sys.stderr

    def parse(self, args=None, fail_with_exception=None):
        """
        Parses the command-line arguments.

        *args* must be an iterable of strings which are the arguments to parse;
        may be None (the default) to use sys.stdout[1:].
        *fail_with_exception* will be evaluated as a boolean and is only consulted if an error
        occurs while parsing the given command-line arguments;
        if it evaluates to False then errors will be reported by raising self.Error;
        otherwise, if it evaluates to True, then errors will be printed to self.stderr followed by
        a call to sys.exit(); specifying None (the default) is equivalent to specifying False.

        Returns an instance of self.ParsedArguments containing the parsed arguments or None if the
        application should terminate immediately as if successful, such as if the help
        documentation was printed in response to --help being specified.
        """

    class ParsedArguments(object):
        """
        Stores the parsed command-line arguments.
        An instance of this class is returned from ArgumentParser.parse().
        """

        def __init__(self):
            """
            Initializes a new instance of this class, setting each attribute to its default value.
            """

        def print(self, f=None):
            """
            Prints the parsed command-line arguments stored in this object, one per line.
            This method is primarily intended for debugging purposes
            """

    class Error(Exception):
        """
        The exception raised if an error occurs when parsing command-line arguments.
        The *exit_code* attribute will be an int whose value is a recommended exit code to specify
        to sys.exit() to terminate the application.
        """

        # an exit code of 2 conventionally indicates invalid command-line arguments
        DEFAULT_EXIT_CODE = 2

        def __init__(self, message, exit_code=None):
            """
            Initializes a new instance of this class.
            *message* must be a string whose value describes the error.
            *exit_code* must be an int whose value is the recommended exit code to specify to
            sys.exit() in response to this error; may be None (the default) to use
            self.DEFAULT_EXIT_CODE.
            """
            super(self, ArgumentParser.Error).__init__(message)
            self.exit_code = exit_code if exit_code is not None else self.DEFAULT_EXIT_CODE


# Allows this file to be run as an application to test parsing command-line arguments
if __name__ == "__main__":
    parser = ArgumentParser()
    parsed_args = parser.parse()
    if parsed_args is not None:
        parsed_args.print()
