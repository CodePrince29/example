from django.contrib import admin
from auditlog.registry import auditlog
from .models import ProductFamily

admin.site.register(ProductFamily)
auditlog.register(ProductFamily)
