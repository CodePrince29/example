# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2022-01-25 06:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_exit', '0005_wexitproductmeasurement_werehouse_entrance_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouseexit',
            name='boxes',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Boxes'),
        ),
        migrations.AlterField(
            model_name='warehouseexitpallet',
            name='boxes',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Boxes'),
        ),
        migrations.AlterField(
            model_name='wexitproductmeasurement',
            name='boxes',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Boxes'),
        ),
    ]
