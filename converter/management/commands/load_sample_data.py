from django.core.management.base import BaseCommand
from converter.models import CustomerCoordinate

class Command(BaseCommand):
    help = 'Load sample customer coordinate data'
    
    def handle(self, *args, **options):
        """Load sample customer coordinate data"""
        
        # Clear existing data
        CustomerCoordinate.objects.all().delete()
        
        # Sample customer coordinates
        sample_customers = [
            {
                'customer_id': '250737138455',
                'latitude': -1.9506,
                'longitude': 30.0584,
                'cell_tower_id': 'TWR_001',
                'cell_tower_name': 'Kigali Tower 1',
                'is_active': True
            },
            {
                'customer_id': '250771013120',
                'latitude': -1.9522,
                'longitude': 30.0917,
                'cell_tower_id': 'TWR_002',
                'cell_tower_name': 'Kigali Tower 2',
                'is_active': True
            },
            {
                'customer_id': '071032054',
                'latitude': -1.9234,
                'longitude': 30.1023,
                'cell_tower_id': '',  # No coordinates - unlimited access
                'cell_tower_name': '',
                'is_active': False
            }
        ]
        
        # Load sample data
        for customer_data in sample_customers:
            CustomerCoordinate.objects.create(**customer_data)
        
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(sample_customers)} sample customer records"))
        
        # Display loaded customers
        self.stdout.write("Sample customers with coordinates:")
        for customer in CustomerCoordinate.objects.all():
            status = "🟢 Active" if customer.is_active else "🔴 Inactive"
            self.stdout.write(f"  {customer.customer_id} - {customer.cell_tower_name} ({status})")
        
        self.stdout.write("\nCustomers without coordinates (unlimited access):")
        unlimited_customers = CustomerCoordinate.objects.filter(cell_tower_id='')
        for customer in unlimited_customers:
            self.stdout.write(f"  {customer.customer_id} - No coordinates (unlimited)")
