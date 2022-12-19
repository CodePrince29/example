from django.contrib import admin
from auditlog.registry import auditlog

# Register your models here.
from .models import Carrier

admin.site.register(Carrier)
auditlog.register(Carrier)
