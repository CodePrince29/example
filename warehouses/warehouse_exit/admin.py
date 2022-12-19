from django.contrib import admin

from .models import *
from auditlog.registry import auditlog

class WarehouseExitAdmin(admin.ModelAdmin):
	list_display = ('__str__','status', 'customer')

admin.site.register(WarehouseExit, WarehouseExitAdmin)
admin.site.register(WExitProductMeasurement)
admin.site.register(WExitConfirmation)
admin.site.register(WarehouseExitPallet)
admin.site.register(ExitPalletPesoVariable)

auditlog.register(WarehouseExit)
auditlog.register(WExitProductMeasurement)
auditlog.register(WExitProductVehicleInspection)
auditlog.register(WExitConfirmation)
auditlog.register(WarehouseExitPallet)
auditlog.register(ExitPalletPesoVariable)

