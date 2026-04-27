#!/usr/bin/env python3
"""
Test cases for EXML to XML converter
"""

import unittest
from exml_to_xml_converter import EXMLToXMLConverter


class TestEXMLToXMLConverter(unittest.TestCase):
    
    def setUp(self):
        self.converter = EXMLToXMLConverter()
    
    def test_simple_element(self):
        """Test conversion of simple element without attributes or children."""
        exml = '{element, "root", [], []}'
        xml = self.converter.convert(exml)
        expected = '<root />\n'
        self.assertEqual(xml, expected)
    
    def test_element_with_attributes(self):
        """Test conversion of element with attributes."""
        exml = '{element, "person", [{attribute, "id", "123"}, {attribute, "name", "John"}], []}'
        xml = self.converter.convert(exml)
        expected = '<person id="123" name="John" />\n'
        self.assertEqual(xml, expected)
    
    def test_element_with_text_content(self):
        """Test conversion of element with text content."""
        exml = '{element, "message", [], ["Hello World"]}'
        xml = self.converter.convert(exml)
        expected = '<message>\n  Hello World\n</message>\n'
        self.assertEqual(xml, expected)
    
    def test_element_with_children(self):
        """Test conversion of element with child elements."""
        exml = '{element, "book", [{attribute, "title", "Python Guide"}], [{element, "author", [], [{element, "name", [], []}]}, {element, "publisher", [], []}]}'
        xml = self.converter.convert(exml)
        expected = '<book title="Python Guide">\n  <author>\n    <name />\n  </author>\n  <publisher />\n</book>\n'
        self.assertEqual(xml, expected)
    
    def test_nested_structure(self):
        """Test conversion of deeply nested structure."""
        exml = '{element, "root", [{attribute, "version", "1.0"}], [{element, "header", [], [{element, "title", [], ["Document Title"]}]}, {element, "body", [], [{element, "paragraph", [{attribute, "class", "intro"}], ["This is a paragraph."]}]}]}'
        xml = self.converter.convert(exml)
        expected = '<root version="1.0">\n  <header>\n    <title>\n      Document Title\n    </title>\n  </header>\n  <body>\n    <paragraph class="intro">\n      This is a paragraph.\n    </paragraph>\n  </body>\n</root>\n'
        self.assertEqual(xml, expected)
    
    def test_invalid_exml_format(self):
        """Test handling of invalid EXML format."""
        with self.assertRaises(ValueError):
            self.converter.convert('invalid format')
        
        with self.assertRaises(ValueError):
            self.converter.convert('{invalid, "tag", [], []}')
    
    def test_empty_attributes_and_children(self):
        """Test element with empty attributes and children lists."""
        exml = '{element, "empty", [], []}'
        xml = self.converter.convert(exml)
        expected = '<empty />\n'
        self.assertEqual(xml, expected)


if __name__ == '__main__':
    unittest.main()
