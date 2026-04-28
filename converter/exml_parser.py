"""
EXML to XML Converter for Django

This module handles the conversion of EXML (Erlang XML format) to standard XML.
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


class FlatSubscriberDataParser:
    """Parser for flat subscriber data format (non-EXML format)."""
    
    def __init__(self):
        self.required_fields = ['MSISDN', 'Custom1', 'Custom2', 'Custom8', 'BillingDay', 'Custom3']
    
    def parse_subscriber_data(self, data_str: str) -> List[Dict[str, str]]:
        """
        Parse flat subscriber data string and extract required fields.
        
        Expected format: Each subscriber record on a new line with fields separated by commas
        Fields are in order: MSISDN, Custom1, Custom2, Custom8, BillingDay, Custom3, ...
        """
        subscribers = []
        lines = data_str.strip().split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Split by comma and clean up each field
            fields = [field.strip() for field in line.split(',')]
            
            if len(fields) < 6:
                # Skip lines that don't have enough fields
                continue
            
            # Extract the required fields (first 6 fields)
            subscriber_data = {
                'MSISDN': fields[0],
                'Custom1': fields[1],
                'Custom2': fields[2],
                'Custom8': fields[3],
                'BillingDay': fields[4],
                'Custom3': fields[5]
            }
            
            subscribers.append(subscriber_data)
        
        return subscribers
    
    def extract_csv_data(self, data_str: str) -> List[Dict[str, str]]:
        """
        Extract CSV data from flat subscriber format.
        
        Returns:
            List of dictionaries containing the required fields for each subscriber
        """
        return self.parse_subscriber_data(data_str)
    
    def is_flat_format(self, data_str: str) -> bool:
        """
        Check if the data string is in flat subscriber format.
        
        Returns:
            True if the data appears to be flat subscriber format
        """
        # Check if it doesn't start with EXML tuple format
        data_str = data_str.strip()
        if not data_str.startswith('{') or not data_str.startswith('element,'):
            # Check if it contains comma-separated values that look like subscriber data
            lines = data_str.split('\n')
            if len(lines) > 1:
                # Check first few lines for comma-separated numeric/string data
                for line in lines[:5]:
                    line = line.strip()
                    if line and ',' in line:
                        fields = line.split(',')
                        if len(fields) >= 6:
                            # Likely flat subscriber format
                            return True
        return False


class MixedXmlFlatParser:
    """Parser for mixed XML/flat subscriber data format."""
    
    def __init__(self):
        self.required_fields = ['MSISDN', 'Custom1', 'Custom2', 'Custom8', 'BillingDay', 'Custom3']

    def _clean_custom3_value(self, value: str) -> str:
        """
        Clean up Custom3 field values that may contain tab-separated or
        space-separated numbers, and return them as a JSON integer array.

        Input example : '269875\t272406\t275252\t278039'
        Output example: '[269875, 272406, 275252, 278039]'

        Non-numeric tokens are kept as strings inside the array.
        """
        import json

        if not value:
            return '[]'

        # Split on tabs, runs of spaces (2+), or existing commas
        tokens = re.split(r'[\t,]+| {2,}', value)
        # Drop empty tokens and strip stray whitespace
        tokens = [t.strip() for t in tokens if t.strip()]

        # Convert to int where possible, fall back to str
        parsed = []
        for t in tokens:
            try:
                parsed.append(int(t))
            except ValueError:
                parsed.append(t)

        return json.dumps(parsed)

    def parse_mixed_data(self, data_str: str) -> List[Dict[str, str]]:
        """
        Parse mixed XML/flat subscriber data format.
        
        This format contains XML-like subscriber records mixed with comma-separated values.
        Each line may contain:
        - XML subscriber record with field elements
        - Comma-separated additional values
        """
        subscribers = []
        lines = data_str.strip().split('\n')
        
                
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # Check if this line contains XML subscriber record
            if '<subscriberRecord>' in line or '<subscriber>' in line:
                subscriber_data = self._parse_xml_line(line)
                if subscriber_data:
                    # Check if there are comma-separated values after the XML part
                    if ',' in line and '>' in line:
                        # Split at the first '>' after the XML part
                        xml_end = line.rfind('>') + 1
                        xml_part = line[:xml_end]
                        csv_part = line[xml_end:]
                        
                        # Parse the CSV part for missing fields
                        if csv_part.strip():
                            csv_fields = [field.strip() for field in csv_part.split(',')]
                            # Custom3 is often the first field after the XML
                            if len(csv_fields) > 0 and not subscriber_data.get('Custom3'):
                                custom3_value = csv_fields[0].strip('"')
                                custom3_value = self._clean_custom3_value(custom3_value)
                                subscriber_data['Custom3'] = custom3_value
                    
                    subscribers.append(subscriber_data)
            else:
                # Try to parse as simple comma-separated data
                fields = [field.strip() for field in line.split(',')]
                if len(fields) >= 6:
                    subscriber_data = {
                        'MSISDN': fields[0],
                        'Custom1': fields[1],
                        'Custom2': fields[2],
                        'Custom8': fields[3],
                        'BillingDay': fields[4],
                        'Custom3': fields[5]
                    }
                    subscribers.append(subscriber_data)
        
        return subscribers
    
    def _parse_xml_line(self, line: str) -> Dict[str, str]:
        """
        Parse a line containing XML subscriber record.
        
        Extract field values from XML-like structure.
        """
        # Initialize with empty values
        subscriber_data = {
            'MSISDN': '',
            'Custom1': '',
            'Custom2': '',
            'Custom8': '',
            'BillingDay': '',
            'Custom3': ''
        }
        
        # Try multiple regex patterns to match different XML field formats
        patterns = [
            r'<field\s+name=""([^""]+)"">([^<]*)</field>',  # Double quotes around name
            r'<field\s+name="([^"]+)">([^<]*)</field>',      # Single quotes around name
            r'<field\s+name=([^>\s]+)>([^<]*)</field>',      # No quotes around name
            r'<field[^>]*name=([^>\s]+)[^>]*>([^<]*)</field>' # More flexible pattern
        ]
        
        matches = []
        for pattern in patterns:
            matches = re.findall(pattern, line)
            if matches:
                break
        
        for field_name, field_value in matches:
            if field_name in subscriber_data:
                cleaned_value = field_value.strip()
                # Special cleanup for Custom3 field to handle tab-separated values
                if field_name == 'Custom3':
                    cleaned_value = self._clean_custom3_value(cleaned_value)
                subscriber_data[field_name] = cleaned_value
        
        # Check if we got any meaningful data
        if any(subscriber_data.values()):
            return subscriber_data
        else:
            return None
    
    def extract_csv_data(self, data_str: str) -> List[Dict[str, str]]:
        """
        Extract CSV data from mixed XML/flat format.
        
        Returns:
            List of dictionaries containing the required fields for each subscriber
        """
        return self.parse_mixed_data(data_str)
    
    def is_mixed_format(self, data_str: str) -> bool:
        """
        Check if the data string is in mixed XML/flat format.
        
        Returns:
            True if the data appears to be mixed XML/flat format
        """
        data_str = data_str.strip()
        # Check for XML tags mixed with comma-separated values
        return ('<subscriberRecord>' in data_str or 
                '<subscriber>' in data_str or 
                '<field name=' in data_str) and ',' in data_str