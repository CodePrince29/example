from __future__ import unicode_literals

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Carrier(models.Model):
    code = models.CharField(verbose_name=_('Carrier Code'), max_length=250, null=False, blank=False)
    name = models.CharField(verbose_name=_('Carrier Name'), max_length=250, null=False, blank=False)
    telephone = models.CharField(verbose_name=_('Carrier Telephone'), max_length=250, null=False, blank=False)
    address = models.CharField(verbose_name=_('Carrier Address'), max_length=255, blank=True)
    email = models.CharField(verbose_name=_('Carrier Email'), max_length=255, null=False, blank=False)
    attend_person = models.CharField(verbose_name=_('Carrier AttendPerson'), max_length=255, blank=True)


    def __str__(self):
        return self.code

    def __unicode__(self):
        return unicode(self.code)

    def get_absolute_url(self):
        return reverse('carrier-list')
    @property
    def can_delete(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrance
        from warehouses.warehouse_exit.models import WarehouseExit
        entrance_vehicle = WarehouseEntrance.objects.filter(carrier=self)
        exit_vehicle = WarehouseExit.objects.filter(carrier=self)
        if len(entrance_vehicle) >0 or len(exit_vehicle) >0:
            return True
        else:
            return False

