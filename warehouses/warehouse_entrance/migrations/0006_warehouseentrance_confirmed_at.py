# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-12-21 08:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_entrance', '0005_auto_20211216_0218'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseentrance',
            name='confirmed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Confirmed At'),
        ),
    ]
