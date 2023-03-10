# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-12-26 06:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_entrance', '0006_warehouseentrance_confirmed_at'),
        ('warehouse_exit', '0002_auto_20200827_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='wexitproductmeasurement',
            name='cost_lot',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Cust Lot'),
        ),
        migrations.AddField(
            model_name='wexitproductmeasurement',
            name='exp_date',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Expiration Date'),
        ),
        migrations.AddField(
            model_name='wexitproductmeasurement',
            name='palet_lot',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Palet Lot'),
        ),
    ]
