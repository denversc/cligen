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

    TAG_ROOT = "cligen"
    TAG_ARGUMENT = "argument"
    TAG_KEY = "key"

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

        expected_root_tag = self._qualified_tag(self.TAG_ROOT)
        if root.tag != expected_root_tag:
            raise self.CligenXmlError(
                "incorrect tag name of XML root element: {} (expected {})".format(
                    root.tag, expected_root_tag))

        argument_tag = self._qualified_tag(self.TAG_ARGUMENT)
        for element in root:
            if element.tag == argument_tag:
                argument = self._parse_argument(element)
                data.arguments.append(argument)

        return ArgumentParserSpec(
            arguments=tuple(data.arguments),
        )

    def _parse_argument(self, root):
        keys = []

        key_tag = self._qualified_tag(self.TAG_KEY)

        for element in root:
            if element.tag == key_tag:
                key = element.text.strip()
                keys.append(key)

        return ArgumentParserSpec.Argument(
            keys=tuple(keys),
        )

    @classmethod
    def _qualified_tag(cls, tag):
        return "{{{}}}{}".format(cls.XML_NAMESPACE, tag)

    class Error(Exception):
        pass

    class XmlParseError(Error):
        pass

    class CligenXmlError(Error):
        pass

    class ParsedData:

        def __init__(self):
            self.arguments = []
