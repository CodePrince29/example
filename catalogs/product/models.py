from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse

from catalogs.clients.models import Client
from catalogs.packaging.models import Packaging
from catalogs.product_family.models import ProductFamily


class Product(models.Model):
    FROZEN = 'frozen'
    REFRIGERATED = 'refrigerated'
    STORAGE_TYPES = (
        (FROZEN, _('Frozen')),
        (REFRIGERATED, _('Refrigerated'))
    )

    product_code = models.CharField(
        verbose_name=_('Product Code'), max_length=120,
        null=False, blank=False,
        # unique=True
    )
    customer_product_code = models.CharField(
        verbose_name=_('Customer Product Code'), max_length=120, null=False, blank=False
    )
    product_family = models.ForeignKey(ProductFamily)
    customer = models.ForeignKey(Client, verbose_name=_('Customer'))
    product_description = models.CharField(
        verbose_name='Product Description', null=True, blank=True,
        help_text="Product Description as it appears in outer package label",
        max_length=250
    )
    replacement_value = models.IntegerField(verbose_name=_('Replacement Value'), default=0)
    package_type = models.ForeignKey(Packaging)
    storage_temperature = models.CharField(verbose_name=_('Storage Temperature'), null=False, blank=False,
                                           max_length=40)
    # gross_weight = models.PositiveIntegerField(verbose_name=_('Gross Weight'))
    gross_weight = models.FloatField(verbose_name=_('Gross Weight'),default=0)
    net_weight = models.FloatField(verbose_name=_('Net Weight'),default=0)
    variable_weight = models.BooleanField(verbose_name=_('Variable Weight'), default=False)
    storage_type = models.CharField(
        verbose_name=_('Storage Type'), max_length=20, choices=STORAGE_TYPES,
        default=FROZEN, null=False, blank=False
    )

    special_observations = models.TextField(verbose_name=_('Special Observations'))

    length = models.FloatField(verbose_name=_('Length'))
    width = models.FloatField(verbose_name=_('Width'))
    height = models.FloatField(verbose_name=_('Height'))
    diameter = models.FloatField(verbose_name=_('Diameter'))
    packages_per_bed = models.PositiveIntegerField(verbose_name=_('Packages per Bed'))
    beds_per_pallet = models.PositiveIntegerField(verbose_name=_('Beds per Pallet'))
    packages_per_pallet = models.PositiveIntegerField(verbose_name=_('Packages per Pallet'))
    min_expiration_for_reception = models.CharField(verbose_name=_('Min Expiration for Reception'), max_length=60)
    min_expiration_for_shipping = models.CharField(verbose_name=_('Min Expiration for Shipping'), max_length=60)
    barcode_to_use = models.CharField(verbose_name=_('Barcode To Use'), max_length=60)
    average_weight = models.BooleanField(verbose_name=_('Peso Promedio'), default=False)

    def __str__(self):
        return self.product_code

    def __unicode__(self):
        return unicode(self.product_code)

    def get_absolute_url(self):
        return reverse('product-list')

    @property
    def product_location(self):
        queryset = self.warehouseinventory_set.all().order_by('exp_date')
        if queryset.exists():
            return unicode(queryset.first().warehouse_location.location_number)
        else:
            return None
    @property
    def get_available_weight(self):
        data = self.net_weight
        return data

    @property
    def get_available_volume(self):
        data = ((self.length/100) * (self.width/100) * (self.height/100))
        return data

    @property
    def can_delete(self):
        from warehouses.warehouse_entrance.models import WProductMeasurement
        from warehouses.warehouse_exit.models import WExitProductMeasurement
        entrance_product = WProductMeasurement.objects.filter(product=self)
        exit_product = WExitProductMeasurement.objects.filter(product=self)
        if len(entrance_product) > 0 or len(exit_product):
            return True
        else:
            return False
    class Meta:
        unique_together = ("product_code", "customer")
