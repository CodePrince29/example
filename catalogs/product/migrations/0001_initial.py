# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2020-06-02 08:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
        ('product_family', '0001_initial'),
        ('packaging', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_code', models.CharField(max_length=120, verbose_name='Product Code')),
                ('customer_product_code', models.CharField(max_length=120, verbose_name='Customer Product Code')),
                ('product_description', models.CharField(blank=True, help_text='Product Description as it appears in outer package label', max_length=250, null=True, verbose_name='Product Description')),
                ('replacement_value', models.IntegerField(default=0, verbose_name='Replacement Value')),
                ('storage_temperature', models.CharField(max_length=40, verbose_name='Storage Temperature')),
                ('gross_weight', models.FloatField(default=0, verbose_name='Gross Weight')),
                ('net_weight', models.FloatField(default=0, verbose_name='Net Weight')),
                ('variable_weight', models.BooleanField(default=False, verbose_name='Variable Weight')),
                ('storage_type', models.CharField(choices=[('frozen', 'Frozen'), ('refrigerated', 'Refrigerated')], default='frozen', max_length=20, verbose_name='Storage Type')),
                ('special_observations', models.TextField(verbose_name='Special Observations')),
                ('length', models.FloatField(verbose_name='Length')),
                ('width', models.FloatField(verbose_name='Width')),
                ('height', models.FloatField(verbose_name='Height')),
                ('diameter', models.FloatField(verbose_name='Diameter')),
                ('packages_per_bed', models.PositiveIntegerField(verbose_name='Packages per Bed')),
                ('beds_per_pallet', models.PositiveIntegerField(verbose_name='Beds per Pallet')),
                ('packages_per_pallet', models.PositiveIntegerField(verbose_name='Packages per Pallet')),
                ('min_expiration_for_reception', models.CharField(max_length=60, verbose_name='Min Expiration for Reception')),
                ('min_expiration_for_shipping', models.CharField(max_length=60, verbose_name='Min Expiration for Shipping')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clients.Client', verbose_name='Customer')),
                ('package_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='packaging.Packaging')),
                ('product_family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_family.ProductFamily')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together=set([('product_code', 'customer')]),
        ),
    ]