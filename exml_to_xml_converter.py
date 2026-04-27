#!/usr/bin/env python3
"""
EXML to XML Converter

This converter handles EXML (Erlang XML format) and converts it to standard XML.
EXML typically represents XML data as Erlang tuples and lists.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Union, Any


class EXMLToXMLConverter:
    """Converter for EXML (Erlang XML) format to standard XML."""
    
    def __init__(self):
        self.indentation = "  "
    
    def parse_exml_tuple(self, exml_str: str) -> Dict[str, Any]:
        """
        Parse EXML tuple string into a structured dictionary.
        
        EXML format examples:
        - {element, "tag", [{attribute, "name", "value"}], [children...]}
        - {element, "tag", [], [children...]}
        - {element, "tag", [], []}
        """
        # Remove outer braces and clean up
        exml_str = exml_str.strip()
        if exml_str.startswith('{') and exml_str.endswith('}'):
            exml_str = exml_str[1:-1].strip()
        
        # Parse the tuple components
        if exml_str.startswith('element,'):
            return self._parse_element(exml_str[8:].strip())
        else:
            raise ValueError(f"Unsupported EXML format: {exml_str}")
    
    def _parse_element(self, element_str: str) -> Dict[str, Any]:
        """Parse an element tuple: "tag", [attributes], [children]"""
        # Extract tag name
        if element_str.startswith('"') and '"' in element_str[1:]:
            tag_end = element_str.find('"', 1)
            tag = element_str[1:tag_end]
            remaining = element_str[tag_end + 1:].strip()
        else:
            raise ValueError(f"Invalid tag format: {element_str}")
        
        # Skip comma
        if remaining.startswith(','):
            remaining = remaining[1:].strip()
        
        # Parse attributes
        if remaining.startswith('['):
            attr_end = self._find_matching_bracket(remaining, 0, '[', ']')
            attr_str = remaining[1:attr_end]
            attributes = self._parse_attributes(attr_str)
            remaining = remaining[attr_end + 1:].strip()
        else:
            attributes = {}
        
        # Skip comma
        if remaining.startswith(','):
            remaining = remaining[1:].strip()
        
        # Parse children
        if remaining.startswith('['):
            child_end = self._find_matching_bracket(remaining, 0, '[', ']')
            child_str = remaining[1:child_end]
            children = self._parse_children(child_str)
        else:
            children = []
        
        return {
            'tag': tag,
            'attributes': attributes,
            'children': children
        }
    
    def _parse_attributes(self, attr_str: str) -> Dict[str, str]:
        """Parse attributes list: [{attribute, "name", "value"}, ...]"""
        attributes = {}
        attr_str = attr_str.strip()
        
        if not attr_str:
            return attributes
        
        # Split by comma outside of brackets
        attr_items = self._split_by_comma(attr_str)
        
        for attr_item in attr_items:
            attr_item = attr_item.strip()
            if attr_item.startswith('{attribute,'):
                attr_content = attr_item[11:-1].strip()  # Remove {attribute, and }
                parts = self._split_by_comma(attr_content)
                if len(parts) >= 2:
                    name = parts[0].strip().strip('"')
                    value = parts[1].strip().strip('"')
                    attributes[name] = value
        
        return attributes
    
    def _parse_children(self, child_str: str) -> List[Dict[str, Any]]:
        """Parse children list: [element1, element2, ...]"""
        children = []
        child_str = child_str.strip()
        
        if not child_str:
            return children
        
        # Split by comma outside of brackets
        child_items = self._split_by_comma(child_str)
        
        for child_item in child_items:
            child_item = child_item.strip()
            if child_item:
                if child_item.startswith('{element,'):
                    children.append(self.parse_exml_tuple(child_item))
                elif child_item.startswith('"') and child_item.endswith('"'):
                    # Text content
                    children.append({
                        'type': 'text',
                        'content': child_item[1:-1]
                    })
        
        return children
    
    def _find_matching_bracket(self, s: str, start: int, open_bracket: str, close_bracket: str) -> int:
        """Find the position of the matching closing bracket."""
        count = 0
        for i in range(start, len(s)):
            if s[i] == open_bracket:
                count += 1
            elif s[i] == close_bracket:
                count -= 1
                if count == 0:
                    return i
        raise ValueError(f"No matching bracket found in: {s}")
    
    def _split_by_comma(self, s: str) -> List[str]:
        """Split string by comma, respecting nested brackets."""
        parts = []
        current = ""
        bracket_count = 0
        in_quotes = False
        
        for char in s:
            if char == '"' and (not current.endswith('\\') or current.endswith('\\\\')):
                in_quotes = not in_quotes
            elif not in_quotes:
                if char in '[{':
                    bracket_count += 1
                elif char in ']}':
                    bracket_count -= 1
                elif char == ',' and bracket_count == 0:
                    parts.append(current.strip())
                    current = ""
                    continue
            
            current += char
        
        if current.strip():
            parts.append(current.strip())
        
        return parts
    
    def to_xml_element(self, exml_data: Dict[str, Any]) -> ET.Element:
        """Convert parsed EXML data to XML Element."""
        element = ET.Element(exml_data['tag'])
        
        # Add attributes
        for name, value in exml_data['attributes'].items():
            element.set(name, value)
        
        # Add children
        for child in exml_data['children']:
            if child.get('type') == 'text':
                element.text = child['content']
            else:
                child_element = self.to_xml_element(child)
                element.append(child_element)
        
        return element
    
    def convert(self, exml_input: str) -> str:
        """
        Convert EXML string to XML string.
        
        Args:
            exml_input: EXML format string
            
        Returns:
            XML string
        """
        try:
            # Parse EXML
            exml_data = self.parse_exml_tuple(exml_input)
            
            # Convert to XML Element
            xml_element = self.to_xml_element(exml_data)
            
            # Format and return XML string
            return self._format_xml(xml_element)
            
        except Exception as e:
            raise ValueError(f"Conversion failed: {str(e)}")
    
    def _format_xml(self, element: ET.Element, level: int = 0) -> str:
        """Format XML element with proper indentation."""
        indent = self.indentation * level
        result = []
        
        # Start tag
        attrs = []
        for name, value in element.attrib.items():
            attrs.append(f'{name}="{value}"')
        
        if attrs:
            result.append(f'{indent}<{element.tag} {" ".join(attrs)}>')
        else:
            result.append(f'{indent}<{element.tag}>')
        
        # Content
        if element.text and element.text.strip():
            result.append(f'{indent}{self.indentation}{element.text}')
        
        # Children
        for child in element:
            result.append(self._format_xml(child, level + 1))
        
        # End tag
        if len(element) == 0 and (not element.text or not element.text.strip()):
            # Empty element - use self-closing tag
            result[-1] = result[-1][:-1] + ' />'
            return '\n'.join(result)
        else:
            result.append(f'{indent}</{element.tag}>')
        
        return '\n'.join(result)


def main():
    """Example usage of the EXML to XML converter."""
    converter = EXMLToXMLConverter()
    
    # Example EXML input
    exml_examples = [
        # Simple element
        '{element, "root", [], []}',
        
        # Element with attributes
        '{element, "person", [{attribute, "id", "123"}, {attribute, "name", "John"}], []}',
        
        # Element with children
        '{element, "book", [{attribute, "title", "Python Guide"}], [{element, "author", [], [{element, "name", [], []}]}, {element, "publisher", [], []}]}',
        
        # Element with text content
        '{element, "message", [], ["Hello World"]}',
    ]
    
    for i, exml_input in enumerate(exml_examples, 1):
        print(f"Example {i}:")
        print(f"EXML: {exml_input}")
        try:
            xml_output = converter.convert(exml_input)
            print(f"XML:\n{xml_output}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)


if __name__ == "__main__":
    main()
