from django.core.management.base import BaseCommand
from converter.models import CustomerCoordinate
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Populate the database with sample customer coordinates'

    def handle(self, *args, **options):
        # Clear existing data
        CustomerCoordinate.objects.all().delete()
        
        # Sample data
        sample_data = [
            # Kigali Area
            {'customer_id': '250737138455', 'latitude': -1.9506, 'longitude': 30.0584, 'cell_tower_id': 'KGL001', 'cell_tower_name': 'Kigali Tower 1', 'is_active': True},
            {'customer_id': '250771013120', 'latitude': -1.9522, 'longitude': 30.0917, 'cell_tower_id': 'KGL002', 'cell_tower_name': 'Kigali Tower 2', 'is_active': True},
            {'customer_id': '250712345678', 'latitude': -1.9450, 'longitude': 30.0650, 'cell_tower_id': 'KGL001', 'cell_tower_name': 'Kigali Tower 1', 'is_active': True},
            {'customer_id': '250722345678', 'latitude': -1.9480, 'longitude': 30.0880, 'cell_tower_id': 'KGL003', 'cell_tower_name': 'Kigali Tower 3', 'is_active': True},
            
            # Butare Area
            {'customer_id': '250782345678', 'latitude': -2.5985, 'longitude': 29.7412, 'cell_tower_id': 'BUT001', 'cell_tower_name': 'Butare Main Tower', 'is_active': True},
            {'customer_id': '250792345678', 'latitude': -2.6050, 'longitude': 29.7500, 'cell_tower_id': 'BUT001', 'cell_tower_name': 'Butare Main Tower', 'is_active': True},
            
            # Gisenyi Area
            {'customer_id': '250732345678', 'latitude': -1.7037, 'longitude': 29.2677, 'cell_tower_id': 'GIS001', 'cell_tower_name': 'Gisenyi Lakeside Tower', 'is_active': True},
            {'customer_id': '250742345678', 'latitude': -1.7100, 'longitude': 29.2750, 'cell_tower_id': 'GIS001', 'cell_tower_name': 'Gisenyi Lakeside Tower', 'is_active': False},
            
            # Goma Area (DRC)
            {'customer_id': '243981234567', 'latitude': -1.6821, 'longitude': 29.2342, 'cell_tower_id': 'GOM001', 'cell_tower_name': 'Goma Central Tower', 'is_active': True},
            
            # Muhanga Area
            {'customer_id': '250752345678', 'latitude': -1.9701, 'longitude': 30.6855, 'cell_tower_id': 'MUH001', 'cell_tower_name': 'Muhanga Tech Park', 'is_active': True},
            
            # Customers without coordinates (null)
            {'customer_id': '071032054', 'latitude': -1.9234, 'longitude': 30.1023, 'cell_tower_id': None, 'cell_tower_name': 'Unassigned', 'is_active': True},
            {'customer_id': '250762345678', 'latitude': None, 'longitude': None, 'cell_tower_id': None, 'cell_tower_name': '', 'is_active': False},
            {'customer_id': '250772345678', 'latitude': None, 'longitude': None, 'cell_tower_id': None, 'cell_tower_name': '', 'is_active': True},
        ]
        
        # Add more realistic sample data
        additional_customers = [
            ('250781111111', -1.9440, 30.0700, 'KGL002', 'Kigali Tower 2', True),
            ('250782222222', -1.9550, 30.0750, 'KGL001', 'Kigali Tower 1', True),
            ('250783333333', -1.9480, 30.0820, 'KGL003', 'Kigali Tower 3', True),
            ('250784444444', -2.6000, 29.7450, 'BUT001', 'Butare Main Tower', True),
            ('250785555555', -1.7050, 29.2700, 'GIS001', 'Gisenyi Lakeside Tower', True),
            ('250786666666', -1.9700, 30.6900, 'MUH001', 'Muhanga Tech Park', True),
            ('250787777777', -1.9500, 30.0600, 'KGL001', 'Kigali Tower 1', False),
            ('250788888888', None, None, None, '', True),
            ('250789999999', None, None, None, '', False),
            ('243982222222', -1.6850, 29.2400, 'GOM001', 'Goma Central Tower', True),
        ]
        
        created_count = 0
        
        # Create sample records
        for data in sample_data:
            if data['latitude'] is not None and data['longitude'] is not None:
                customer = CustomerCoordinate.objects.create(
                    customer_id=data['customer_id'],
                    latitude=data['latitude'],
                    longitude=data['longitude'],
                    cell_tower_id=data['cell_tower_id'] or '',
                    cell_tower_name=data['cell_tower_name'],
                    is_active=data['is_active']
                )
                created_count += 1
        
        # Create additional customers
        for customer_id, lat, lon, tower_id, tower_name, is_active in additional_customers:
            if lat is not None and lon is not None:
                customer = CustomerCoordinate.objects.create(
                    customer_id=customer_id,
                    latitude=lat,
                    longitude=lon,
                    cell_tower_id=tower_id or '',
                    cell_tower_name=tower_name,
                    is_active=is_active
                )
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} customer records')
        )
        
        # Display summary
        total = CustomerCoordinate.objects.count()
        active = CustomerCoordinate.objects.filter(is_active=True).count()
        with_coords = CustomerCoordinate.objects.exclude(cell_tower_id='').count()
        
        self.stdout.write(f'\nDatabase Summary:')
        self.stdout.write(f'  Total Customers: {total}')
        self.stdout.write(f'  Active Customers: {active}')
        self.stdout.write(f'  With Coordinates: {with_coords}')
        self.stdout.write(f'  Without Coordinates: {total - with_coords}')
