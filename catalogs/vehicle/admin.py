from django.contrib import admin
from auditlog.registry import auditlog
# Register your models here.
from .models import Vehicle

admin.site.register(Vehicle)
auditlog.register(Vehicle)
