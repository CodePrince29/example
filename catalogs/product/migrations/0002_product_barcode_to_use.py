# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-10-23 01:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='barcode_to_use',
            field=models.CharField(default=django.utils.timezone.now, max_length=60, verbose_name='Barcode To Use'),
            preserve_default=False,
        ),
    ]
