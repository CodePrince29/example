from django.contrib import admin
from auditlog.registry import auditlog
from .models import Packaging

admin.site.register(Packaging)
auditlog.register(Packaging)