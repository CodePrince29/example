# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2022-04-06 04:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('warehouse_exit', '0007_auto_20220330_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehouseexit',
            name='confirmed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exit_confirmed_by', to=settings.AUTH_USER_MODEL, verbose_name='Confirmed by'),
        ),
        migrations.AddField(
            model_name='warehouseexit',
            name='sent_to_maniobras_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exit_maniobras_by', to=settings.AUTH_USER_MODEL, verbose_name='Sent To Maniobras by'),
        ),
        migrations.AddField(
            model_name='warehouseexitpallet',
            name='maniobras_completed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Sent To Maniobras by'),
        ),
    ]