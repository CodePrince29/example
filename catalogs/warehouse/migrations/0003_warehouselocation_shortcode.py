# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-11-16 02:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0002_auto_20200602_0353'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouselocation',
            name='shortcode',
            field=models.CharField(blank=True, max_length=250, null=True, unique=True, verbose_name='Short Code'),
        ),
    ]
