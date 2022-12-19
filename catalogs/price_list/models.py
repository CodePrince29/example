from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse
from django.utils.encoding import smart_str

from catalogs.service.models import Service


class PriceList(models.Model):
    class Meta:
        verbose_name = _('Price List')
        verbose_name_plural = _('Price Lists')

    code = models.CharField(verbose_name=_('Code'), max_length=250, null=False, blank=False)
    description = models.CharField(verbose_name=_('Description'), max_length=250, null=False, blank=False)
    is_baseline = models.BooleanField(
        verbose_name=_('Baseline Price List'), default=False,
        help_text=_('Use this list as baseline price list')
    )

    def __str__(self):
        return smart_str(self.description)

    def __unicode__(self):
        return smart_str(self.description)

    def get_absolute_url(self):
        return reverse('pricelist-list')

    def services(self):
        return self.servicerelation_set.all()


class ServiceRelation(models.Model):
    class Meta:
        verbose_name = "Price List Item"
        verbose_name_plural = "Price List Items"

    service = models.ForeignKey(to=Service, verbose_name=_('Service'))
    price = models.FloatField(verbose_name=_('Price'), default=0.00)
    price_list = models.ForeignKey(PriceList)

    def __str__(self):
        return smart_str(self.price_list)

    def __unicode__(self):
        return smart_str(self.price_list)

    # def get_absolute_url(self):
    #     return reverse('pricelistservicerelation-list')
