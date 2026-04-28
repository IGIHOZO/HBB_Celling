from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
import csv
import io
from django.conf import settings
from .exml_parser import EXMLToXMLConverter, FlatSubscriberDataParser, MixedXmlFlatParser


def index(request):
    """
    Main page with EXML converter interface
    """
    return render(request, 'converter/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def convert_exml(request):
    """
    Convert EXML to XML via AJAX
    """
    try:
        # Get EXML data from request
        data = json.loads(request.body)
        exml_input = data.get('exml', '').strip()
        
        if not exml_input:
            return JsonResponse({
                'success': False,
                'error': 'EXML input cannot be empty'
            })
        
        # Convert EXML to XML
        converter = EXMLToXMLConverter()
        xml_output = converter.convert(exml_input)
        
        return JsonResponse({
            'success': True,
            'xml': xml_output,
            'exml': exml_input
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@require_http_methods(["GET"])
def example_exml(request):
    """
    Return example EXML inputs
    """
    examples = [
        {
            'name': 'Simple Element',
            'exml': '{element, "root", [], []}'
        },
        {
            'name': 'Element with Attributes',
            'exml': '{element, "person", [{attribute, "id", "123"}, {attribute, "name", "John Doe"}], []}'
        },
        {
            'name': 'Element with Text',
            'exml': '{element, "message", [], ["Hello, World!"]}'
        },
        {
            'name': 'Nested Elements',
            'exml': '{element, "book", [{attribute, "title", "Python Guide"}], [{element, "author", [], [{element, "name", [], ["John Smith"]}]}, {element, "publisher", [], ["Tech Books"]}]}'
        },
        {
            'name': 'Complex Structure',
            'exml': '{element, "html", [{attribute, "lang", "en"}], [{element, "head", [], [{element, "title", [], ["My Page"]}]}, {element, "body", [], [{element, "h1", [], ["Welcome"]}, {element, "p", [], ["This is a paragraph."]}]}]}'
        }
    ]
    
    return JsonResponse({
        'success': True,
        'examples': examples
    })


def api_documentation(request):
    """
    API documentation page
    """
    return render(request, 'converter/api.html')


@csrf_exempt
@require_http_methods(["POST"])
def convert_to_csv(request):
    """
    Convert EXML data or flat subscriber data to CSV format extracting specific properties
    """
    try:
        # Get EXML data from request
        data = json.loads(request.body)
        exml_input = data.get('exml', '').strip()
        
        if not exml_input:
            return JsonResponse({
                'success': False,
                'error': 'EXML input cannot be empty'
            })
        
        # Check for different data formats
        flat_parser = FlatSubscriberDataParser()
        mixed_parser = MixedXmlFlatParser()
        csv_data = []
        xml_output = ""
        
        if mixed_parser.is_mixed_format(exml_input):
            # Parse mixed XML/flat subscriber data
            csv_data = mixed_parser.extract_csv_data(exml_input)
            xml_output = "<root>Mixed XML/flat subscriber data format - converted directly to CSV</root>"
        elif flat_parser.is_flat_format(exml_input):
            # Parse flat subscriber data directly
            csv_data = flat_parser.extract_csv_data(exml_input)
            xml_output = "<root>Flat subscriber data format - converted directly to CSV</root>"
        else:
            # Try to convert as EXML first
            try:
                converter = EXMLToXMLConverter()
                xml_output = converter.convert(exml_input)
                
                # Parse XML and extract CSV data
                csv_data = extract_csv_properties(xml_output)
            except ValueError as e:
                if "Unsupported EXML format" in str(e):
                    # If EXML parsing fails, try mixed format first, then flat format as fallback
                    if mixed_parser.is_mixed_format(exml_input):
                        csv_data = mixed_parser.extract_csv_data(exml_input)
                        xml_output = "<root>Mixed XML/flat subscriber data format - converted directly to CSV</root>"
                    else:
                        csv_data = flat_parser.extract_csv_data(exml_input)
                        xml_output = "<root>Flat subscriber data format - converted directly to CSV</root>"
                else:
                    raise e
        
        # Generate CSV content
        csv_content = generate_csv(csv_data)
        
        return JsonResponse({
            'success': True,
            'csv': csv_content,
            'xml': xml_output,
            'exml': exml_input,
            'record_count': len(csv_data)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def extract_csv_properties(xml_content):
    """
    Extract specific properties (MSISDN, Custom1, Custom2, Custom8, BillingDay, Custom3) from XML
    """
    import xml.etree.ElementTree as ET
    
    # Parse XML
    root = ET.fromstring(xml_content)
    
    # Properties to extract
    target_properties = ['MSISDN', 'Custom1', 'Custom2', 'Custom8', 'BillingDay', 'Custom3']
    
    csv_data = []
    
    # Find all subscriber records or similar elements
    for element in root.iter():
        # Check if this element contains any of our target properties
        record_data = {}
        has_target_properties = False
        
        # Check direct children for target properties
        for child in element:
            if child.tag in target_properties:
                record_data[child.tag] = child.text or ''
                has_target_properties = True
        
        # If we found target properties in this element, add to results
        if has_target_properties:
            # Ensure all target properties are present (even if empty)
            for prop in target_properties:
                if prop not in record_data:
                    record_data[prop] = ''
            
            csv_data.append(record_data)
    
    return csv_data


def generate_csv(csv_data):
    """
    Generate CSV string from extracted data
    """
    if not csv_data:
        return "MSISDN,Custom1,Custom2,Custom8,BillingDay,Custom3\n"
    
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)  # Quote all fields to handle commas properly
    
    # Write header
    writer.writerow(['MSISDN', 'Custom1', 'Custom2', 'Custom8', 'BillingDay', 'Custom3'])
    
    # Write data rows
    for row in csv_data:
        writer.writerow([
            row.get('MSISDN', ''),
            row.get('Custom1', ''),
            row.get('Custom2', ''),
            row.get('Custom8', ''),
            row.get('BillingDay', ''),
            row.get('Custom3', '')
        ])
    
    return output.getvalue()


@csrf_exempt
@require_http_methods(["POST"])
def upload_exml_file(request):
    """
    Handle EXML file upload and convert to XML
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            })
        
        uploaded_file = request.FILES['file']
        
        # Validate file extension
        if not (uploaded_file.name.lower().endswith('.exml') or uploaded_file.name.lower().endswith('.xml')):
            return JsonResponse({
                'success': False,
                'error': 'Please upload an .exml or .xml file'
            })
        
        # Validate file size (max 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'File size must be less than 50MB'
            })
        
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')
        
        if not file_content.strip():
            return JsonResponse({
                'success': False,
                'error': 'File is empty'
            })
        
        # Check if it's regular XML or EXML
        if file_content.strip().startswith('<?xml') or file_content.strip().startswith('<'):
            # It's regular XML - just return it as-is with formatting
            import xml.dom.minidom as minidom
            try:
                # Clean up the content first
                content = file_content.strip()
                
                # Remove XML declaration if present (minidom doesn't like it in the middle)
                if content.startswith('<?xml'):
                    # Find the end of the declaration
                    end_decl = content.find('?>') + 2
                    content = content[end_decl:].strip()
                
                # Try to parse as-is first
                try:
                    dom = minidom.parseString(content)
                    xml_output = dom.toprettyxml(indent="  ")
                    # Remove extra blank lines
                    xml_output = '\n'.join([line for line in xml_output.split('\n') if line.strip()])
                except Exception as parse_error:
                    # If parsing fails, try to fix multiple root elements
                    if 'junk after document element' in str(parse_error) or 'multiple root elements' in str(parse_error):
                        # Wrap content in a root element
                        wrapped_content = f"<root>\n{content}\n</root>"
                        dom = minidom.parseString(wrapped_content)
                        xml_output = dom.toprettyxml(indent="  ")
                        # Remove extra blank lines and the wrapper tags
                        lines = [line for line in xml_output.split('\n') if line.strip()]
                        # Remove the <root> and </root> lines
                        if lines and '<root>' in lines[0]:
                            lines = lines[1:]
                        if lines and '</root>' in lines[-1]:
                            lines = lines[:-1]
                        xml_output = '\n'.join(lines)
                    else:
                        raise parse_error
                
                return JsonResponse({
                    'success': True,
                    'xml': xml_output,
                    'exml': file_content,
                    'filename': uploaded_file.name,
                    'format': 'XML'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid XML format: {str(e)}'
                })
        else:
            # It's EXML - convert to XML
            converter = EXMLToXMLConverter()
            xml_output = converter.convert(file_content)
            return JsonResponse({
                'success': True,
                'xml': xml_output,
                'exml': file_content,
                'filename': uploaded_file.name,
                'format': 'EXML'
            })
        
    except UnicodeDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'File encoding error. Please ensure the file is UTF-8 encoded.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'File processing error: {str(e)}'
        })
