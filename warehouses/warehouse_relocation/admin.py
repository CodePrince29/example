from django.contrib import admin
from auditlog.registry import auditlog
from .models import *

admin.site.register(WarehouseRelocation)

auditlog.register(WarehouseRelocation)