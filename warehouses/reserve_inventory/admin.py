from __future__ import unicode_literals
from django.contrib import admin
from .models import *
from auditlog.registry import auditlog

class ReserveInventoryAdmin(admin.ModelAdmin):
	list_display = ('id', 'motive_to_reserve', 'reserve_boxes', 'boxes')
	readonly_fields = ('inventory',)

admin.site.register(ReserveInventory, ReserveInventoryAdmin)
admin.site.register(ReserveInventoryLog)

auditlog.register(ReserveInventory)
auditlog.register(ReserveInventoryLog)

