from django.contrib import admin
from .models import *
from auditlog.registry import auditlog

class WareHouseEntraceAdmin(admin.ModelAdmin):
	list_display = ('__str__','status', 'customer')
admin.site.register(WarehouseEntrance, WareHouseEntraceAdmin)
admin.site.register(WProductMeasurement)
admin.site.register(WProductVehicleInspection)
admin.site.register(WIncidenceProduct)
admin.site.register(WIncidenceImage)
admin.site.register(WarehouseEntranceConfirmation)
admin.site.register(EntrancePalletPesoVariable)



class WarehouseEntrancePalletAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'warehouse', 'rack_number', 'location','palet_lot', 'boxes', 'box_kg','confirmed',)
	readonly_fields = ('created_at','updated_at')
	search_fields = ('palet_lot', 'cost_lot', 'gross_weight', 'net_weight')
admin.site.register(WarehouseEntrancePallet, WarehouseEntrancePalletAdmin)


# auditlog.register(WarehouseEntrance)
# auditlog.register(WProductMeasurement)
# auditlog.register(WProductVehicleInspection)
# auditlog.register(WIncidenceProduct)
# auditlog.register(WIncidenceImage)
# auditlog.register(WarehouseEntranceConfirmation)
# auditlog.register(WarehouseEntrancePallet)
# auditlog.register(EntrancePalletPesoVariable)