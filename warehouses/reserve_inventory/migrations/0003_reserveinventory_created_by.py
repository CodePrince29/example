# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2022-04-06 05:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reserve_inventory', '0002_auto_20200602_0353'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserveinventory',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Created By'),
        ),
    ]
