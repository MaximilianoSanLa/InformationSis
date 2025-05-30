# Generated by Django 5.0 on 2025-05-25 22:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_item_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SoldService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sold', models.DecimalField(decimal_places=2, max_digits=10)),
                ('warranty', models.CharField(editable=False, max_length=9, unique=True)),
                ('license_plate', models.CharField(max_length=20)),
                ('service_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.servicetype')),
            ],
        ),
    ]
