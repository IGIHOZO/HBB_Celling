from django.core.management.base import BaseCommand
from converter.models import HBBCustomer, CustomerCoordinate

class Command(BaseCommand):
    help = 'Populate the hbb_customers table with sample data'

    def handle(self, *args, **options):
        # Clear existing data
        HBBCustomer.objects.all().delete()
        
        # Sample customers with their cell assignments
        sample_customers = [
            {
                'customer_id': '250737138455',
                'msisdn': '250737138455',
                'custom1': 'John Doe',
                'custom2': 'Kigali',
                'custom8': 'Sales Rep',
                'billing_day': 15,
                'custom3_cells': 'KGL001,KGL002'  # Assigned to multiple towers
            },
            {
                'customer_id': '250771013120',
                'msisdn': '250771013120',
                'custom1': 'Jane Smith',
                'custom2': 'Kigali',
                'custom8': 'Manager',
                'billing_day': 20,
                'custom3_cells': 'KGL002,KGL003'
            },
            {
                'customer_id': '250712345678',
                'msisdn': '250712345678',
                'custom1': 'David Kamau',
                'custom2': 'Kigali',
                'custom8': 'Technician',
                'billing_day': 10,
                'custom3_cells': 'KGL001'
            },
            {
                'customer_id': '250722345678',
                'msisdn': '250722345678',
                'custom1': 'Maria Garcia',
                'custom2': 'Kigali',
                'custom8': 'Consultant',
                'billing_day': 25,
                'custom3_cells': 'KGL003'
            },
            {
                'customer_id': '250782345678',
                'msisdn': '250782345678',
                'custom1': 'Paul Nkusi',
                'custom2': 'Butare',
                'custom8': 'Field Agent',
                'billing_day': 5,
                'custom3_cells': 'BUT001'
            },
            {
                'customer_id': '250792345678',
                'msisdn': '250792345678',
                'custom1': 'Sarah Johnson',
                'custom2': 'Butare',
                'custom8': 'Support Staff',
                'billing_day': 12,
                'custom3_cells': 'BUT001'
            },
            {
                'customer_id': '250732345678',
                'msisdn': '250732345678',
                'custom1': 'Robert Mwenda',
                'custom2': 'Gisenyi',
                'custom8': 'Regional Manager',
                'billing_day': 1,
                'custom3_cells': 'GIS001'
            },
            {
                'customer_id': '250742345678',
                'msisdn': '250742345678',
                'custom1': 'Anne Kabui',
                'custom2': 'Gisenyi',
                'custom8': 'Operator',
                'billing_day': 8,
                'custom3_cells': 'GIS001'
            },
            {
                'customer_id': '243981234567',
                'msisdn': '243981234567',
                'custom1': 'Michel Kabusu',
                'custom2': 'Goma',
                'custom8': 'Liaison Officer',
                'billing_day': 15,
                'custom3_cells': 'GOM001'
            },
            {
                'customer_id': '250752345678',
                'msisdn': '250752345678',
                'custom1': 'Emily Omondi',
                'custom2': 'Muhanga',
                'custom8': 'Tech Lead',
                'billing_day': 20,
                'custom3_cells': 'MUH001'
            },
            {
                'customer_id': '071032054',
                'msisdn': '071032054',
                'custom1': 'Corporate Account',
                'custom2': 'Multiple Regions',
                'custom8': 'Enterprise',
                'billing_day': 1,
                'custom3_cells': ''  # No specific cells assigned
            },
            {
                'customer_id': '250762345678',
                'msisdn': '250762345678',
                'custom1': 'Inactive Customer',
                'custom2': 'Kigali',
                'custom8': 'Former Employee',
                'billing_day': None,
                'custom3_cells': ''  # No cells
            },
            {
                'customer_id': '250772345678',
                'msisdn': '250772345678',
                'custom1': 'New Recruit',
                'custom2': 'Kigali',
                'custom8': 'Trainee',
                'billing_day': 30,
                'custom3_cells': 'KGL001,KGL002,KGL003'  # Has access to all Kigali towers
            },
            {
                'customer_id': '250781111111',
                'msisdn': '250781111111',
                'custom1': 'Alex Mutua',
                'custom2': 'Kigali',
                'custom8': 'Sales Executive',
                'billing_day': 17,
                'custom3_cells': 'KGL002'
            },
            {
                'customer_id': '250782222222',
                'msisdn': '250782222222',
                'custom1': 'Francis Nyambura',
                'custom2': 'Kigali',
                'custom8': 'Business Dev',
                'billing_day': 22,
                'custom3_cells': 'KGL001,KGL003'
            },
            {
                'customer_id': '250783333333',
                'msisdn': '250783333333',
                'custom1': 'Grace Mutesi',
                'custom2': 'Kigali',
                'custom8': 'HR Manager',
                'billing_day': 28,
                'custom3_cells': 'KGL003'
            },
            {
                'customer_id': '250784444444',
                'msisdn': '250784444444',
                'custom1': 'Henry Kagame',
                'custom2': 'Butare',
                'custom8': 'Operations',
                'billing_day': 14,
                'custom3_cells': 'BUT001'
            },
            {
                'customer_id': '250785555555',
                'msisdn': '250785555555',
                'custom1': 'Isabelle Dusabe',
                'custom2': 'Gisenyi',
                'custom8': 'Field Officer',
                'billing_day': 11,
                'custom3_cells': 'GIS001'
            },
            {
                'customer_id': '250786666666',
                'msisdn': '250786666666',
                'custom1': 'James Mwaura',
                'custom2': 'Muhanga',
                'custom8': 'IT Specialist',
                'billing_day': 19,
                'custom3_cells': 'MUH001'
            },
            {
                'customer_id': '250787777777',
                'msisdn': '250787777777',
                'custom1': 'Kathy Wambui',
                'custom2': 'Kigali',
                'custom8': 'Inactive',
                'billing_day': None,
                'custom3_cells': 'KGL001'  # Has assigned cells but inactive
            },
            {
                'customer_id': '250788888888',
                'msisdn': '250788888888',
                'custom1': 'Liam Nkomo',
                'custom2': 'Unknown',
                'custom8': 'No Data',
                'billing_day': None,
                'custom3_cells': ''  # No coordinates and no cells
            },
            {
                'customer_id': '250789999999',
                'msisdn': '250789999999',
                'custom1': 'Margaret Kipchoge',
                'custom2': 'Unknown',
                'custom8': 'No Data',
                'billing_day': None,
                'custom3_cells': ''
            },
            {
                'customer_id': '243982222222',
                'msisdn': '243982222222',
                'custom1': 'Olivier Kaseke',
                'custom2': 'Goma',
                'custom8': 'Border Agent',
                'billing_day': 10,
                'custom3_cells': 'GOM001'
            },
        ]
        
        created = 0
        for customer_data in sample_customers:
            customer, created_flag = HBBCustomer.objects.update_or_create(
                customer_id=customer_data['customer_id'],
                defaults={
                    'msisdn': customer_data['msisdn'],
                    'custom1': customer_data['custom1'],
                    'custom2': customer_data['custom2'],
                    'custom8': customer_data['custom8'],
                    'billing_day': customer_data['billing_day'],
                    'custom3_cells': customer_data['custom3_cells'],
                }
            )
            if created_flag:
                created += 1
        
        total = HBBCustomer.objects.count()
        with_cells = HBBCustomer.objects.exclude(custom3_cells='').count()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created/updated {total} customer records')
        )
        self.stdout.write(f'\nCustomer Summary:')
        self.stdout.write(f'  Total Customers: {total}')
        self.stdout.write(f'  With Cell Assignments: {with_cells}')
        self.stdout.write(f'  Without Cell Assignments: {total - with_cells}')
        
        # Show coordinates match
        coords_count = CustomerCoordinate.objects.count()
        matched = 0
        for customer in HBBCustomer.objects.all():
            if CustomerCoordinate.objects.filter(customer_id=customer.customer_id).exists():
                matched += 1
        
        self.stdout.write(f'\nCoordinates Link Summary:')
        self.stdout.write(f'  Total Customers with Coordinates: {coords_count}')
        self.stdout.write(f'  Customers Matched: {matched}')
