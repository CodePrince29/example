# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-06-02 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=250, verbose_name='Code')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Description')),
                ('billable', models.BooleanField(default=True, help_text='Service Billable to the Customer')),
            ],
        ),
    ]
