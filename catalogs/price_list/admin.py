from django.contrib import admin
from .models import PriceList, ServiceRelation
from auditlog.registry import auditlog


admin.site.register(PriceList)
admin.site.register(ServiceRelation)

auditlog.register(PriceList)
auditlog.register(ServiceRelation)
