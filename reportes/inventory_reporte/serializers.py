from catalogs.warehouse.models import WarehouseInventory,WarehouseInventoryLog
from warehouses.warehouse_entrance.models import WarehouseEntrance
from catalogs.clients.models import Client
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
class InventorySerializer(serializers.ModelSerializer):
	total_kg = serializers.SerializerMethodField()
	client = serializers.SerializerMethodField('get_customer_name')
	warehouse_entrance_id = serializers.SerializerMethodField('get_warehouse_entrance')
	product = serializers.SerializerMethodField('get_product_name')
	warehouse_location_number = serializers.SerializerMethodField('get_warehouse_location')
	warehouse_entrance_confirmation_code = serializers.SerializerMethodField('get_warehouse_entrance_confirmation')
	class Meta:
		model = WarehouseInventory		
		fields = ( 'id','product', 'warehouse_location_number', 'warehouse_entrance_confirmation_code', 'client',"total_kg","total_boxes","exp_date","warehouse_entrance_id",'available_gross_weight','available_net_weight')

	def get_customer_name(self, obj):
		return obj.client.name

	def get_product_name(self, obj):
		return obj.product.product_description

	def get_warehouse_location(self, obj):
		return obj.warehouse_location.location_number

	def get_warehouse_entrance_confirmation(self, obj):
		if obj.warehouse_entrance_pallet != None:
			return obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.code
		else:
			return "N/A"
	def get_warehouse_entrance(self, obj):
		if obj.warehouse_entrance_pallet != None:
			return obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.id
		else:
			return "N/A"

	def get_total_kg(self,obj):
		import math
		if  math.isnan(float(obj.total_kg)):
			return 0
		return obj.total_kg

class InventoryLogSerializer(serializers.ModelSerializer):
	customer_data = serializers.SerializerMethodField('get_customer_name')
	product_data = serializers.SerializerMethodField('get_product_code')

	
	class Meta:
		model = WarehouseInventoryLog
		fields = ('id', 'customer_data','total_kg','total_boxes','product_data','retained_boxes','user','adjust_reason','description')

	def get_customer_name(self, obj):
		return obj.warehouse_inventory.client.name

	def get_product_code(self, obj):
		return obj.warehouse_inventory.product.product_code

class WarehouseEntranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseEntrance
        fields = '__all__'