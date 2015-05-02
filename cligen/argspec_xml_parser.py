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
The parser for the cligen XML specification file.
"""

import xml.etree.ElementTree

from cligen.argspec import ArgumentParserSpec


class ArgumentSpecParser:

    XML_NAMESPACE = "http://schemas.cligen.io/arguments"

    def parse_string(self, xml_string):
        try:
            root_element = xml.etree.ElementTree.fromstring(xml_string)
        except xml.etree.ElementTree.ParseError as e:
            raise self.XmlParseError("{}".format(e))
        else:
            return self._parse_document(root_element)

    def parse_file(self, path):
        try:
            doc = xml.etree.ElementTree.parse(path)
        except xml.etree.ElementTree.ParseError as e:
            raise self.XmlParseError("{}".format(e))
        else:
            root_element = doc.getroot()
            return self._parse_document(root_element)

    def _parse_document(self, root):
        ns = {"cligen", self.XML_NAMESPACE}
        data = self.ParsedData()

        expected_root_tag = self._qualified_tag("cligen")
        if root.tag != expected_root_tag:
            raise self.CligenXmlError(
                "incorrect tag name of XML root element: {} (expected {})".format(
                    root.tag, expected_root_tag))

        for element in root:
            if self._is_qualified_tag(element, "argument"):
                argument = self._parse_argument(element)
                data.arguments.append(argument)
            elif self._is_qualified_tag(element, "options"):
                self._parse_options(element, data.options)

        if data.options.default_help_argument:
            help_argument = ArgumentParserSpec.Argument(
                keys=("-h", "--help"),
                help_text="Print the help information then exit",
            )
            data.arguments.append(help_argument)
            data.help_argument = help_argument

        return ArgumentParserSpec(
            arguments=tuple(data.arguments),
            help_argument=data.help_argument,
        )

    def _parse_argument(self, root):
        keys = []
        help_text = None

        for element in root:
            if self._is_qualified_tag(element, "key"):
                key = self._element_text(element)
                keys.append(key)
            elif self._is_qualified_tag(element, "help"):
                help_text = self._element_text(element)

        return ArgumentParserSpec.Argument(
            keys=tuple(keys),
            help_text=help_text,
        )

    def _parse_options(self, root, options):
        for element in root:
            if self._is_qualified_tag(element, "add-builtin-help-argument"):
                value = self._element_text(element, default_value="").lower()
                if value == "true":
                    options.default_help_argument = True
                elif value == "false":
                    options.default_help_argument = False
                else:
                    raise self.CligenXmlError(
                        "invalid text in element {}: {} (expected \"true\" or \"false\")".format(
                            element.tag, value))

        return options

    @classmethod
    def _qualified_tag(cls, tag):
        return "{{{}}}{}".format(cls.XML_NAMESPACE, tag)

    @classmethod
    def _is_qualified_tag(cls, element, tag):
        expected_tag = cls._qualified_tag(tag)
        actual_tag = element.tag
        return (actual_tag == expected_tag)

    @staticmethod
    def _element_text(element, default_value=None):
        text = element.text
        if text is None:
            return default_value
        else:
            return text.strip()

    class Error(Exception):
        pass

    class XmlParseError(Error):
        pass

    class CligenXmlError(Error):
        pass

    class ParsedData:

        def __init__(self):
            self.arguments = []
            self.help_argument = None
            self.options = self.Options()

        class Options:

            def __init__(self):
                self.default_help_argument = True
