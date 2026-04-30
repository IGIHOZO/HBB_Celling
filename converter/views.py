from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
import math
import json
import csv
import io
from .exml_parser import EXMLToXMLConverter, FlatSubscriberDataParser, MixedXmlFlatParser
from .models import CustomerCoordinate, HBBCustomer, CellsInfo, CustomerDataFromExcelRaw


def find_customer_by_lookup(customer_lookup):
    customer = HBBCustomer.objects.filter(msisdn=customer_lookup).first()
    if customer:
        return customer
    if str(customer_lookup).isdigit():
        return HBBCustomer.objects.filter(id=int(customer_lookup)).first()
    return None


def find_customer_coordinates(hbb_customer):
    return CustomerCoordinate.objects.filter(msisdn=hbb_customer.msisdn).first()


def haversine_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    p1 = math.radians(float(lat1))
    p2 = math.radians(float(lat2))
    d_lat = math.radians(float(lat2) - float(lat1))
    d_lon = math.radians(float(lon2) - float(lon1))
    a = math.sin(d_lat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def parse_custom3_cells(raw_custom3):
    if not raw_custom3:
        return []
    cleaned = str(raw_custom3).replace('[', '').replace(']', '')
    parts = [p.strip() for p in cleaned.split(',') if p.strip()]
    unique = []
    for part in parts:
        if part not in unique:
            unique.append(part)
    return unique


def cells_info_table_exists():
    try:
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
        return 'cells_info' in tables
    except Exception:
        return False


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

def dashboard(request):
    """
    Dashboard page - main entry point with navigation to converter and coordinates
    """
    # Calculate real statistics from database
    total_customers = HBBCustomer.objects.count()
    total_coordinates = CustomerCoordinate.objects.count()
    total_cells = CellsInfo.objects.count()
    
    # Calculate customers with coordinates
    customers_with_coords = CustomerCoordinate.objects.filter(
        msisdn__in=HBBCustomer.objects.values_list('msisdn', flat=True)
    ).count()
    
    # Calculate success rate (customers with coordinates / total customers)
    success_rate = 0
    if total_customers > 0:
        success_rate = round((customers_with_coords / total_customers) * 100, 1)
    
    # Calculate growth based on MSISDN comparison between HBB customers and excel raw data
    excel_raw_customers = CustomerDataFromExcelRaw.objects.exclude(msisdn__isnull=True).exclude(msisdn='').count()
    
    # Calculate growth as percentage of excel customers that are in HBB system
    customer_change = 0
    if excel_raw_customers > 0:
        customer_change = round((total_customers / excel_raw_customers) * 100, 1)
    
    # Calculate coverage percentage
    coverage_percentage = 0
    if total_customers > 0:
        coverage_percentage = round((customers_with_coords / total_customers) * 100, 1)
    
    context = {
        'total_customers': total_customers,
        'customers_with_coordinates': customers_with_coords,
        'active_cells': total_cells,
        'success_rate': success_rate,
        'customer_change': customer_change,
        'coverage_percentage': coverage_percentage,
        'excel_raw_customers': excel_raw_customers,
    }
    
    return render(request, 'converter/dashboard.html', context)

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


@csrf_exempt
@require_http_methods(["POST"])
def get_customer_coordinates(request):
    """
    Get customer coordinates and cell tower information
    """
    try:
        data = json.loads(request.body)
        customer_lookup = data.get('customer_id', '').strip()
        
        if not customer_lookup:
            return JsonResponse({
                'success': False,
                'error': 'Customer ID or MSISDN is required'
            })

        hbb_customer = find_customer_by_lookup(customer_lookup)
        if not hbb_customer:
            return JsonResponse({
                'success': False,
                'error': f'Customer {customer_lookup} not found in hbb_customers'
            })

        coord = find_customer_coordinates(hbb_customer)
        if not coord:
            return JsonResponse({
                'success': False,
                'error': f'No coordinate data found for MSISDN {hbb_customer.msisdn}',
                'customer': {
                    'customer_id': str(hbb_customer.id),
                    'msisdn': hbb_customer.msisdn,
                    'name': hbb_customer.customer_name,
                    'custom3_cells': [],
                    'has_cell_assignment': False,
                }
            })

        return JsonResponse({
            'success': True,
            'customer': {
                'customer_id': str(hbb_customer.id),
                'msisdn': hbb_customer.msisdn,
                'name': hbb_customer.customer_name,
                'latitude': coord.latitude,
                'longitude': coord.longitude,
                'cell_tower_id': coord.location or '',
                'cell_tower_name': coord.location or '',
                'assigned_at': coord.created_at.isoformat() if coord.created_at else None,
                'is_active': True,
                'custom3_cells': coord.custom3_cells,
                'has_cell_assignment': len(coord.custom3_cells) > 0,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["POST"])
def check_customer_cells(request):
    """
    Check if customer has cell towers assigned from Custom3 data
    """
    try:
        data = json.loads(request.body)
        customer_lookup = data.get('customer_id', '').strip()
        
        if not customer_lookup:
            return JsonResponse({
                'success': False,
                'error': 'Customer ID or MSISDN is required'
            })

        hbb_customer = find_customer_by_lookup(customer_lookup)
        if not hbb_customer:
            return JsonResponse({
                'success': False,
                'error': f'Customer {customer_lookup} not found in hbb_customers'
            })

        coord = find_customer_coordinates(hbb_customer)
        custom3_cells = coord.custom3_cells if coord else []
        has_cell_assignment = len(custom3_cells) > 0

        has_coordinates = coord is not None and coord.latitude is not None and coord.longitude is not None
        coordinates_cell_tower_id = coord.location if coord and coord.location else ''
        coordinates_cell_in_custom3 = bool(
            coordinates_cell_tower_id and coordinates_cell_tower_id in custom3_cells
        )

        return JsonResponse({
            'success': True,
            'customer_id': str(hbb_customer.id),
            'msisdn': hbb_customer.msisdn,
            'has_coordinates': has_coordinates,
            'custom3_cells': custom3_cells,
            'has_cell_assignment': has_cell_assignment,
            'coordinates_cell_tower_id': coordinates_cell_tower_id,
            'coordinates_cell_in_custom3': coordinates_cell_in_custom3,
            'message': (
                'Coordinates and custom3 cells are aligned'
                if has_coordinates and coordinates_cell_in_custom3
                else 'Review customer assignment: coordinates/custom3 mismatch or missing data'
            ),
            'unlimited_access': (not has_cell_assignment) and (not has_coordinates)
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })


def coordinates_page(request):
    """
    Display all HBB customers
    """
    customers = list(HBBCustomer.objects.all().order_by('id'))
    coords = CustomerCoordinate.objects.exclude(msisdn__isnull=True).exclude(msisdn='')
    coord_by_msisdn = {}
    for coord in coords:
        coord_by_msisdn[coord.msisdn] = coord
    coord_msisdn_set = set(coord_by_msisdn.keys())

    all_customers = []
    found_customers = []
    unlocked_customers = []
    for customer in customers:
        coord = coord_by_msisdn.get(customer.msisdn) if customer.msisdn in coord_msisdn_set else None
        custom3_value = (coord.custom3 or '').strip() if coord else ''

        if coord:
            status = 'Locked' if custom3_value else 'UnLocked'
        else:
            status = 'NotFound'

        all_customers.append({
            'customer': customer,
            'status': status,
        })

        if coord:
            has_coordinates = coord.latitude is not None and coord.longitude is not None
            is_locked = bool(custom3_value)
            found_customers.append({
                'customer': customer,
                'is_locked': is_locked,
                'custom3': custom3_value,
                'custom3_cells': parse_custom3_cells(custom3_value),
            })
            if not is_locked:
                unlocked_customers.append({
                    'customer': customer,
                    'latitude': coord.latitude,
                    'longitude': coord.longitude,
                    'has_coordinates': has_coordinates,
                })
    not_found_customers = [c for c in customers if c.msisdn not in coord_msisdn_set]
    has_cells_info_table = cells_info_table_exists()
    cells_info_count = CellsInfo.objects.count() if has_cells_info_table else 0

    return render(
        request,
        'converter/coordinates.html',
        {
            'customers': customers,
            'all_customers': all_customers,
            'found_customers': found_customers,
            'not_found_customers': not_found_customers,
            'unlocked_customers': unlocked_customers,
            'cell_towers_count': cells_info_count,
            'has_cell_towers_table': has_cells_info_table,
        },
    )


@csrf_exempt
@require_http_methods(["GET"])
def suggest_nearest_cells(request):
    try:
        if not cells_info_table_exists():
            return JsonResponse({
                'success': False,
                'error': 'cells_info table is missing in database',
            })

        msisdn = request.GET.get('msisdn', '').strip()
        if not msisdn:
            return JsonResponse({'success': False, 'error': 'msisdn is required'})

        customer = HBBCustomer.objects.filter(msisdn=msisdn).first()
        if not customer:
            return JsonResponse({'success': False, 'error': f'Customer {msisdn} not found'})

        coord = CustomerCoordinate.objects.filter(msisdn=msisdn).first()
        if not coord or coord.latitude is None or coord.longitude is None:
            return JsonResponse({'success': False, 'error': f'Coordinates not available for {msisdn}'})

        towers = CellsInfo.objects.exclude(lat__isnull=True).exclude(lon__isnull=True)
        if not towers.exists():
            return JsonResponse({
                'success': False,
                'error': 'No cells found in cells_info table',
            })

        customer_lat = float(coord.latitude)
        customer_lon = float(coord.longitude)
        nearest = []
        for tower in towers:
            distance_km = haversine_km(customer_lat, customer_lon, tower.lat, tower.lon)
            nearest.append({
                'cell_id': str(tower.eutracelid or tower.id),
                'cell_name': tower.name or (tower.cell or ''),
                'region': tower.district or tower.province or '',
                'site_name': tower.sector or '',
                'latitude': float(tower.lat),
                'longitude': float(tower.lon),
                'distance_km': round(distance_km, 3),
            })

        nearest.sort(key=lambda row: row['distance_km'])
        nearest = nearest[:10]

        return JsonResponse({
            'success': True,
            'customer': {
                'id': customer.id,
                'msisdn': customer.msisdn,
                'name': customer.customer_name,
                'latitude': customer_lat,
                'longitude': customer_lon,
                'current_cells': coord.custom3_cells,
            },
            'suggested_cells': nearest,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})


@csrf_exempt
@require_http_methods(["POST"])
def save_customer_cells(request):
    try:
        payload = json.loads(request.body)
        msisdn = str(payload.get('msisdn', '')).strip()
        selected_cells = payload.get('selected_cells', [])
        if not msisdn:
            return JsonResponse({'success': False, 'error': 'msisdn is required'})
        if not isinstance(selected_cells, list):
            return JsonResponse({'success': False, 'error': 'selected_cells must be a list'})

        cell_ids = [str(c).strip() for c in selected_cells if str(c).strip()]
        unique_cell_ids = []
        for cid in cell_ids:
            if cid not in unique_cell_ids:
                unique_cell_ids.append(cid)

        coord = CustomerCoordinate.objects.filter(msisdn=msisdn).first()
        if not coord:
            return JsonResponse({'success': False, 'error': f'Customer coordinate row not found for {msisdn}'})

        coord.custom3 = ','.join(unique_cell_ids)
        coord.save(update_fields=['custom3'])

        return JsonResponse({
            'success': True,
            'msisdn': msisdn,
            'saved_cells': unique_cell_ids,
            'message': 'Customer cells updated successfully',
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON body'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})


@csrf_exempt
@require_http_methods(["GET"])
def registered_cell_distances(request):
    try:
        if not cells_info_table_exists():
            return JsonResponse({'success': False, 'error': 'cells_info table is missing in database'})

        msisdn = request.GET.get('msisdn', '').strip()
        if not msisdn:
            return JsonResponse({'success': False, 'error': 'msisdn is required'})

        customer = HBBCustomer.objects.filter(msisdn=msisdn).first()
        if not customer:
            return JsonResponse({'success': False, 'error': f'Customer {msisdn} not found'})

        coord = CustomerCoordinate.objects.filter(msisdn=msisdn).first()
        if not coord or coord.latitude is None or coord.longitude is None:
            return JsonResponse({'success': False, 'error': f'Coordinates not available for {msisdn}'})

        registered_cells = parse_custom3_cells(coord.custom3 or '')
        if not registered_cells:
            return JsonResponse({'success': True, 'customer': {'msisdn': msisdn}, 'distances': []})

        customer_lat = float(coord.latitude)
        customer_lon = float(coord.longitude)
        distance_rows = []
        not_found = []

        for cell_id in registered_cells:
            cell_obj = None
            if cell_id.isdigit():
                cell_obj = CellsInfo.objects.filter(eutracelid=int(cell_id)).first()
                if not cell_obj:
                    cell_obj = CellsInfo.objects.filter(id=int(cell_id)).first()
            if not cell_obj:
                cell_obj = CellsInfo.objects.filter(name=cell_id).first()

            if not cell_obj or cell_obj.lat is None or cell_obj.lon is None:
                not_found.append(cell_id)
                continue

            distance_km = haversine_km(customer_lat, customer_lon, cell_obj.lat, cell_obj.lon)
            distance_rows.append({
                'cell_id': cell_id,
                'cell_name': cell_obj.name or (cell_obj.cell or ''),
                'latitude': float(cell_obj.lat),
                'longitude': float(cell_obj.lon),
                'region': cell_obj.district or cell_obj.province or '',
                'distance_km': round(distance_km, 3),
            })

        distance_rows.sort(key=lambda row: row['distance_km'])

        return JsonResponse({
            'success': True,
            'customer': {
                'id': customer.id,
                'msisdn': customer.msisdn,
                'name': customer.customer_name,
                'latitude': customer_lat,
                'longitude': customer_lon,
            },
            'distances': distance_rows,
            'not_found_cells': not_found,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'})


@csrf_exempt
@require_http_methods(["GET"])
def get_all_customers(request):
    """
    Get all customers with their coordinate status
    """
    try:
        customers = CustomerCoordinate.objects.all().order_by('-created_at')
        
        customer_list = []
        for customer in customers:
            customer_list.append({
                'customer_id': customer.msisdn or str(customer.id),
                'latitude': customer.latitude,
                'longitude': customer.longitude,
                'cell_tower_id': customer.location or '',
                'cell_tower_name': customer.location or '',
                'assigned_at': customer.created_at.isoformat() if customer.created_at else '',
                'is_active': True
            })
        
        return JsonResponse({
            'success': True,
            'customers': customer_list,
            'total_count': len(customer_list)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })


@csrf_exempt
@require_http_methods(["GET"])
def get_customers_with_coords(request):
    """
    Get all HBB customers with their coordinates and cell assignments
    """
    try:
        customers = HBBCustomer.objects.all().order_by('id')
        
        customer_list = []
        for customer in customers:
            # Try to find coordinates for this customer using msisdn reference
            coords = None
            coord = find_customer_coordinates(customer)
            if coord:
                coords = {
                    'latitude': coord.latitude,
                    'longitude': coord.longitude,
                    'cell_tower_id': coord.location or '',
                    'cell_tower_name': coord.location or '',
                    'is_active': True
                }
            assigned_cells = coord.custom3_cells if coord else []
            coordinates_cell_in_custom3 = bool(
                coords and coords.get('cell_tower_id') and coords.get('cell_tower_id') in assigned_cells
            )
            
            customer_list.append({
                'customer_id': str(customer.id),
                'msisdn': customer.msisdn,
                'name': customer.customer_name,
                'region': coord.region if coord else '',
                'role': coord.custom8 if coord else '',
                'billing_day': coord.billing_day if coord else None,
                'assigned_cells': assigned_cells,
                'has_cell_assignment': len(assigned_cells) > 0,
                'coordinates': coords,
                'has_coordinates': coords is not None,
                'coordinates_cell_in_custom3': coordinates_cell_in_custom3,
                'updated_at': customer.created_at.isoformat() if customer.created_at else ''
            })
        
        return JsonResponse({
            'success': True,
            'customers': customer_list,
            'total_count': len(customer_list),
            'with_coords': len([c for c in customer_list if c['has_coordinates']]),
            'with_cells': len([c for c in customer_list if c['has_cell_assignment']]),
            'both': len([c for c in customer_list if c['has_coordinates'] and c['has_cell_assignment']]),
            'cells_match_coords': len([c for c in customer_list if c['coordinates_cell_in_custom3']])
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        })
