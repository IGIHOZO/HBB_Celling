from django.db import models

# Create your models here.

class HBBCustomer(models.Model):
    """Existing hbb_customers table in PostgreSQL."""
    id = models.BigAutoField(primary_key=True)
    msisdn = models.CharField(max_length=50, blank=True, null=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    product_code = models.CharField(max_length=255, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    price_plan_order_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    rn = models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'hbb_customers'
        managed = False
    
    def __str__(self):
        return f"{self.msisdn or self.id}"


class CustomerCoordinate(models.Model):
    """Existing customer_coordinates table in PostgreSQL."""
    id = models.BigAutoField(primary_key=True)
    msisdn = models.CharField(max_length=50, blank=True, null=True)
    custom1 = models.BigIntegerField(blank=True, null=True)
    custom2 = models.DateTimeField(blank=True, null=True)
    custom8 = models.DateTimeField(blank=True, null=True)
    billing_day = models.IntegerField(blank=True, null=True, db_column='billingday')
    custom3 = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    isp = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    activation_date = models.TextField(blank=True, null=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'customer_coordinates'
        managed = False
    
    def __str__(self):
        return f"{self.msisdn or self.id}"

    @property
    def custom3_cells(self):
        if not self.custom3:
            return []
        return [cell.strip() for cell in self.custom3.split(',') if cell.strip()]


class CellTower(models.Model):
    """Master table for cell coordinates used in nearest-cell suggestions."""
    cell_id = models.CharField(max_length=120, unique=True)
    cell_name = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=8)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    region = models.CharField(max_length=120, blank=True, null=True)
    site_name = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cell_towers'
        indexes = [
            models.Index(fields=['cell_id']),
            models.Index(fields=['region']),
        ]

    def __str__(self):
        return self.cell_id


class CellsInfo(models.Model):
    """Existing cells_info source table in PostgreSQL."""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    eutracelid = models.IntegerField(blank=True, null=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    lon = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    sector = models.CharField(max_length=255, blank=True, null=True)
    cell = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'cells_info'
        managed = False

    def __str__(self):
        return str(self.eutracelid or self.id)


class CustomerDataFromExcelRaw(models.Model):
    """Existing customer_data_fromexcel_raw table in PostgreSQL."""
    msisdn = models.TextField(blank=True, null=True)
    isp = models.TextField(blank=True, null=True)
    prod_name = models.TextField(blank=True, null=True, db_column='prod_name')
    region = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    activation_date = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    cid = models.CharField(max_length=255, blank=True, null=True)
    cid_status = models.CharField(max_length=255, blank=True, null=True, db_column='CID STATUS')

    class Meta:
        db_table = 'customer_data_fromexcel_raw'
        managed = False

    def __str__(self):
        return self.msisdn or 'Unknown MSISDN'
