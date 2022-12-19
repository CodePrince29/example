# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-08-27 14:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_client_user'),
        ('product', '0001_initial'),
        ('warehouse_entrance', '0002_auto_20200827_0941'),
        ('maniobras', '0002_auto_20200602_0353'),
    ]

    operations = [
        migrations.CreateModel(
            name='TakingInventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taking_date', models.DateField(auto_now_add=True, verbose_name='Taking Inventory Date')),
                ('taking_hour', models.TimeField(auto_now_add=True, verbose_name='Taking Inventory Hour')),
                ('total_kg', models.FloatField(blank=True, default=0, null=True, verbose_name='Total Kg')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('finish', 'Finish')], default='pending', max_length=20, verbose_name='Warehouse Entrance Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client', verbose_name='Customer')),
                ('product', models.ManyToManyField(to='product.Product', verbose_name='Product')),
                ('warehouseentrancepallet', models.ManyToManyField(to='warehouse_entrance.WarehouseEntrancePallet', verbose_name='WarehouseEntrancePallet')),
            ],
        ),
    ]
