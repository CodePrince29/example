from django.contrib import admin
from auditlog.registry import auditlog

from .models import GeneralParams

admin.site.register(GeneralParams)
auditlog.register(GeneralParams)
