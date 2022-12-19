# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-06-02 08:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
        ('warehouse_entrance', '0001_initial'),
        #('clients', '0002_client_user'),
        ('warehouse', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WarehouseRelocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Reason for Relocation')),
                ('source_warehouse', models.CharField(default='', max_length=255, verbose_name='Source Warehouse')),
                ('source_location', models.CharField(default='', max_length=255, verbose_name='Source Location')),
                ('palet_lot', models.CharField(blank=True, max_length=255, null=True, verbose_name='Palet Lot')),
                ('created_at', models.DateField(auto_now=True)),
                ('updated_at', models.DateField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client', verbose_name='Customer')),
                ('destination_location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.WarehouseLocation', verbose_name='Destination Location')),
                ('destination_warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.Warehouse', verbose_name='Destination Warehouse')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product', verbose_name='Product')),
                ('werehouse_entrance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse_entrance.WarehouseEntrance', verbose_name='Entrance')),
            ],
        ),
    ]