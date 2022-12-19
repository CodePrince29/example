from django.contrib import admin

from .models import Warehouse, WarehouseLocation, WarehouseRow, WarehouseSection, WarehouseDepthLevel, \
    WarehouseHeightLevel, WarehouseInventory, WarehouseInventoryLog, Branch, WarehouseTruckBays
from warehouses.warehouse_entrance.models import WarehouseEntrance
from django.db.models import Sum
import decimal
import pdb
from auditlog.registry import auditlog
admin.site.register(Warehouse)
admin.site.register(WarehouseRow)
admin.site.register(WarehouseSection)
admin.site.register(WarehouseDepthLevel)
admin.site.register(WarehouseHeightLevel)
admin.site.register(WarehouseInventoryLog)
admin.site.register(Branch)
class TruckBayAdmin(admin.ModelAdmin):
	list_display = ('id', 'branch', 'bay', 'time_slot', 'loading',)
	readonly_fields = ('branch', 'bay', 'time_slot','content_type','object_id',)
	exclude = ('content_object',)
	
admin.site.register(WarehouseTruckBays, TruckBayAdmin)
auditlog.register(Warehouse)
auditlog.register(WarehouseLocation)
auditlog.register(WarehouseInventory)
auditlog.register(WarehouseInventoryLog)
auditlog.register(WarehouseRow)
auditlog.register(WarehouseSection)
auditlog.register(WarehouseHeightLevel)
auditlog.register(WarehouseDepthLevel)

class WarehouseInventoryAdmin(admin.ModelAdmin):
	list_display = ('__str__','pallet_name','entrance','updated_at')
	readonly_fields = ('updated_at',)
	search_fields = ('warehouse_entrance_pallet__palet_lot',)
	
	def pallet_name(self,obj):
		return obj.warehouse_entrance_pallet.palet_lot

	def entrance(self,obj):
		return obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.id

admin.site.register(WarehouseInventory,WarehouseInventoryAdmin)


# class WarehouseLocationAdmin(admin.ModelAdmin):
# 	list_display = ('warehouse', 'location_number','total_stored_kg','total_stored_boxes','available_weight','available_volume')
# 	list_filter = ('warehouse','location_number')
# 	search_fields = ('warehouse__code', 'location_number')
# 	readonly_fields = ('total_available_weight','total_available_volume')
	
# 	def total_available_weight(self,obj):
		
# 		total_available_weight,total_available_volume = self.calculate_available_weight(obj)
# 		return total_available_weight

# 	def total_available_volume(self,obj):
# 		total_available_weight,total_available_volume = self.calculate_available_weight(obj)
# 		return total_available_volume

# 	def calculate_available_weight(self,obj):
# 		w_stored_weight=0
# 		w_excluded_weight = 0
# 		w_stored_volume = 0
# 		w_excluded_volume = 0
# 		for entrance_pallet in obj.warehouseentrancepallet_set.all():
# 			if entrance_pallet !=None:
# 				if entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.status == 'finish':
# 					w_stored_weight += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_weight
# 					w_stored_volume += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_volume

# 		for exit_pallet in obj.warehouseexitpallet_set.all():
# 			if exit_pallet !=None:
# 				if exit_pallet.werehouse_exit_confirmation.werehouse_exit.status == 'finish':
# 					w_excluded_weight += exit_pallet.boxes * exit_pallet.werehouse_exit_confirmation.product.get_available_weight
# 					w_excluded_volume += exit_pallet.boxes * exit_pallet.werehouse_exit_confirmation.product.get_available_volume
			
# 		total_available_weight=obj.available_weight-(w_stored_weight-w_excluded_weight)
# 		total_available_volume=obj.available_volume-(w_stored_volume-w_excluded_volume)

# 		return total_available_weight,total_available_volume		
	       

# admin.site.register(WarehouseLocation,WarehouseLocationAdmin)
admin.site.register(WarehouseLocation)