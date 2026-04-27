from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from django.conf import settings
from .exml_parser import EXMLToXMLConverter


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
