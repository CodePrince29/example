from catalogs.warehouse.models import WarehouseInventory
from catalogs.clients.models import Client
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
class InventorySerializer(serializers.ModelSerializer):
	client = serializers.SerializerMethodField('get_customer_name')
	warehouse_entrance_id = serializers.SerializerMethodField('get_warehouse_entrance')
	product = serializers.SerializerMethodField('get_product_name')
	warehouse_location_number = serializers.SerializerMethodField('get_warehouse_location')
	warehouse_entrance_confirmation_code = serializers.SerializerMethodField('get_warehouse_entrance_confirmation')
	class Meta:
		model = WarehouseInventory
		fields = ( 'id','product', 'warehouse_location_number', 'warehouse_entrance_confirmation_code', 'client',"total_kg","total_boxes","exp_date","warehouse_entrance_id")

	def get_customer_name(self, obj):
		return obj.client.name

	def get_product_name(self, obj):
		return obj.product.product_description

	def get_warehouse_location(self, obj):
		return obj.warehouse_location.location_number

	def get_warehouse_entrance_confirmation(self, obj):
		if obj.warehouse_entrance_pallet.werehouse_entrance_confirmation != None:
			return obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.code
		else:
			return "N/A"
	def get_warehouse_entrance(self, obj):
		if obj.warehouse_entrance_pallet.werehouse_entrance_confirmation != None:
			return obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.id
		else:
			return "N/A"