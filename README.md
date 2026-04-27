# EXML to XML Converter

A Python converter that transforms EXML (Erlang XML format) into standard XML documents.

## Overview

EXML is how XML data is often represented in Erlang applications using tuples and lists. This converter parses the EXML format and generates well-formed XML output.

## EXML Format

The converter handles EXML in this format:
```
{element, "tagname", [{attribute, "attr_name", "attr_value"}], [children...]}
```

### Components:
- **Elements**: `{element, "tagname", attributes, children}`
- **Attributes**: `{attribute, "name", "value"}`
- **Text content**: `"text string"`
- **Children**: List of elements or text strings

## Installation

No external dependencies required. Uses Python's standard library.

```bash
# Clone or download the files
# Ensure Python 3.6+ is installed
```

## Usage

### Basic Usage

```python
from exml_to_xml_converter import EXMLToXMLConverter

converter = EXMLToXMLConverter()

# Simple element
exml = '{element, "root", [], []}'
xml = converter.convert(exml)
print(xml)
# Output: <root />

# Element with attributes
exml = '{element, "person", [{attribute, "id", "123"}, {attribute, "name", "John"}], []}'
xml = converter.convert(exml)
print(xml)
# Output: <person id="123" name="John" />

# Element with children
exml = '{element, "book", [{attribute, "title", "Python Guide"}], [{element, "author", [], []}]}'
xml = converter.convert(exml)
print(xml)
```

### Command Line Usage

```bash
# Run the built-in examples
python exml_to_xml_converter.py

# Run tests
python test_converter.py
```

### File Processing

```python
# Read EXML from file and convert to XML
with open('input.exml', 'r') as f:
    exml_content = f.read()

converter = EXMLToXMLConverter()
xml_output = converter.convert(exml_content)

with open('output.xml', 'w') as f:
    f.write(xml_output)
```

## Examples

### Simple Element
```exml
{element, "message", [], ["Hello World"]}
```
```xml
<message>
  Hello World
</message>
```

### Complex Structure
```exml
{element, "person", [{attribute, "id", "123"}], [{element, "name", [], ["John Doe"]}, {element, "email", [], ["john@example.com"]}]}
```
```xml
<person id="123">
  <name>
    John Doe
  </name>
  <email>
    john@example.com
  </email>
</person>
```

## Testing

Run the test suite:

```bash
python -m unittest test_converter.py
```

The test suite covers:
- Simple elements
- Elements with attributes
- Text content
- Nested structures
- Error handling

## Files

- `exml_to_xml_converter.py` - Main converter class
- `test_converter.py` - Unit tests
- `examples.exml` - Example EXML inputs
- `README.md` - This documentation

## Error Handling

The converter raises `ValueError` for:
- Invalid EXML format
- Malformed tuples
- Missing required components
- Unbalanced brackets

## Limitations

- Currently supports standard EXML element format
- Handles basic attribute types (strings)
- Text content is treated as CDATA
- No XML namespace support yet

## Contributing

Feel free to extend the converter for additional EXML formats or XML features.

## License

This project is open source and available under the MIT License.
