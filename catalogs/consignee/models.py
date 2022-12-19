from __future__ import unicode_literals

from django.db import models
from catalogs.clients.models import Client
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Consignee(models.Model):
    code = models.CharField(verbose_name=_('Code'), max_length=250, null=False, blank=False)
    name = models.CharField(verbose_name=_('Full Name'), max_length=250, null=False, blank=False)
    customer = models.ForeignKey(Client, null=False,verbose_name=_('Customer'))
    email = models.CharField(verbose_name=_('Email'), max_length=255, null=False, blank=False)
    contact_phone = models.CharField(verbose_name=_('Contact Phone Number'), max_length=255, blank=True)
    signature = models.FileField(verbose_name=_('Signature'), blank=True)


    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return reverse('consignee-list')

    @property
    def can_delete(self):
        from warehouses.warehouse_exit.models import WarehouseExit
        exit_consignee = WarehouseExit.objects.filter(consignee=self)
        if len(exit_consignee) >0:
            return True
        else:
            return False
