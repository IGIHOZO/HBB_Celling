from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('converter', '0002_hbbcustomer'),
    ]

    operations = [
        migrations.CreateModel(
            name='CellTower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cell_id', models.CharField(max_length=120, unique=True)),
                ('cell_name', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.DecimalField(decimal_places=8, max_digits=12)),
                ('longitude', models.DecimalField(decimal_places=8, max_digits=12)),
                ('region', models.CharField(blank=True, max_length=120, null=True)),
                ('site_name', models.CharField(blank=True, max_length=255, null=True)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'cell_towers',
                'indexes': [
                    models.Index(fields=['cell_id'], name='cell_towers_cell_id_2fd0f6_idx'),
                    models.Index(fields=['region'], name='cell_towers_region_1caa52_idx'),
                ],
            },
        ),
    ]
