# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-12-26 07:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_exit', '0003_auto_20211226_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouseexit',
            name='carrier',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='carrier.Carrier', verbose_name='Carrier'),
        ),
        migrations.AlterField(
            model_name='warehouseexit',
            name='status',
            field=models.CharField(choices=[('control', 'Control'), ('InManeuvers', 'In Maneuvers'), ('ManeuverComplete', 'Maneuver Complete'), ('finish', 'Finish')], default='control', max_length=20, verbose_name='Warehouse Exit Status'),
        ),
        migrations.AlterField(
            model_name='warehouseexit',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='vehicle.Vehicle', verbose_name='Vehicle'),
        ),
    ]