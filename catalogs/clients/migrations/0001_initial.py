# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-06-02 08:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('price_list', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Name')),
                ('username', models.CharField(max_length=150, verbose_name='Customer User Name')),
                ('password', models.CharField(max_length=150, verbose_name='Password')),
                ('client_code', models.CharField(max_length=150, verbose_name='Client Code')),
                ('contact_name', models.CharField(max_length=150, verbose_name='Contact Name')),
                ('contact_phone', models.CharField(default='', max_length=30, verbose_name='Contact Phone')),
                ('email', models.CharField(max_length=150, verbose_name='Email')),
                ('price_list', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='price_list.PriceList')),
            ],
        ),
    ]