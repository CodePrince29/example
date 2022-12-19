from __future__ import unicode_literals

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

class Vehicle(models.Model):
    code = models.CharField(verbose_name=_('Code'), max_length=250, null=False, blank=False)
    description = models.CharField(verbose_name=_('Description'), max_length=255, blank=True)
    capicity = models.CharField(verbose_name=_('Capicity'), max_length=255, blank=True)

    def __str__(self):
        return self.description

    def __unicode__(self):
        return unicode(self.description)

    def get_absolute_url(self):
        return reverse('vehicle-list')

    @property
    def can_delete(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrance
        from warehouses.warehouse_exit.models import WarehouseExit
        entrance_vehicle = WarehouseEntrance.objects.filter(vehicle=self)
        exit_vehicle = WarehouseExit.objects.filter(vehicle=self)
        if len(entrance_vehicle) >0 or len(exit_vehicle) >0:
            return True
        else:
            return False


