# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-08-01 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_client_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='barcoderead',
            field=models.BooleanField(default=False, verbose_name='Bar Code'),
        ),
    ]
