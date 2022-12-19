from django.contrib import admin
from auditlog.registry import auditlog

from .models import Unit

admin.site.register(Unit)
auditlog.register(Unit)
