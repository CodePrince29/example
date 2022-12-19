from __future__ import unicode_literals

from django.db import models
from django.shortcuts import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save

class GeneralParams(models.Model):
    key = models.CharField(max_length=250, null=False, blank=False)
    value = models.CharField(max_length=250, null=False, blank=False)
    description = models.TextField()

    def __str__(self):
        return self.key

    def get_absolute_url(self):
        return reverse('gp-list')

@receiver(post_save,sender=GeneralParams)
def update_logout_time(sender,**kwargs):
    obj = kwargs['instance']
    if obj.key == "AutoLogoffTime":
        from django.conf import settings
        if hasattr(settings, 'SESSION_COOKIE_AGE'):
        	settings.SESSION_COOKIE_AGE =  int(obj.value) * 60
