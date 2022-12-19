# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-11-29 08:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_entrance', '0002_auto_20200827_0941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouseentrance',
            name='status',
            field=models.CharField(choices=[('control', 'Control'), ('in_receipt', 'In Receipt'), ('InManeuvers', 'In Maneuvers'), ('ManeuverComplete', 'Maneuver Complete'), ('finish', 'Finish')], default='control', max_length=20, verbose_name='Warehouse Entrance Status'),
        ),
        migrations.AlterField(
            model_name='warehouseentrancepallet',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse.WarehouseLocation', verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='warehouseentrancepallet',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='warehouse.Warehouse', verbose_name='Warehouse'),
        ),
    ]