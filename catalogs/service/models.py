from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse


class Service(models.Model):
    code = models.CharField(verbose_name=_('Code'), max_length=250, null=False, blank=False)
    description = models.CharField(verbose_name=_('Description'), max_length=255, blank=True)
    billable = models.BooleanField(default=True, help_text=_('Service Billable to the Customer'))

    def __str__(self):
        return self.description

    def __unicode__(self):
        return unicode(self.description)

    def get_absolute_url(self):
        return reverse('service-list')

