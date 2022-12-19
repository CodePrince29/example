from django.contrib import admin
from .models import Client
from auditlog.registry import auditlog

admin.site.register(Client)
auditlog.register(Client)
