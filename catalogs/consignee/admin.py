from django.contrib import admin
from auditlog.registry import auditlog


# Register your models here.
from .models import Consignee

admin.site.register(Consignee)
auditlog.register(Consignee)
