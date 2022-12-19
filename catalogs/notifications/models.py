from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from users.models import UserProfile
from django.contrib.postgres.fields import ArrayField



class Notification(models.Model):
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ('-occurred_dt',)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    occurred_dt = models.DateTimeField(verbose_name=_('Occurred Datetime of the Notification'), null=True)
    created_by = models.PositiveIntegerField(verbose_name=_('Created By'),null=True)
    message = models.CharField(verbose_name=_('Message'), max_length=250, null=True, blank=True)
    status = models.BooleanField(default=False)
    deleted_by = ArrayField(models.IntegerField(),null=True, blank=True)

    def __str__(self):
        return smart_str("%s" % ( self.content_object))

    @property
    def object_class_name(self):
        return self.content_type.name