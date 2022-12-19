from django.contrib import admin
from .models import Service
from auditlog.registry import auditlog

admin.site.register(Service)
auditlog.register(Service)
