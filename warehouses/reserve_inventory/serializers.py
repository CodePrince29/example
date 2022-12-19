from catalogs.warehouse.models import WarehouseInventory,WarehouseInventoryLog
from catalogs.clients.models import Client
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

class InventorySerializer(serializers.ModelSerializer):
	client_name = serializers.SerializerMethodField()
	product_name = serializers.SerializerMethodField()
	location_number = serializers.SerializerMethodField()
	warehouse_name = serializers.SerializerMethodField()
	lote_tarima = serializers.SerializerMethodField()
	lote_cliente = serializers.SerializerMethodField()
	peso_bruto = serializers.SerializerMethodField()
	peso_neto = serializers.SerializerMethodField()

	class Meta:
		model = WarehouseInventory
		fields = '__all__'

	def get_client_name(self, obj):
		return obj.client.name
	def get_product_name(self, obj):
		return obj.product.product_description
	def get_lote_tarima(self, obj):
		return obj.warehouse_entrance_pallet.palet_lot
	def get_lote_cliente(self, obj):
		return obj.warehouse_entrance_pallet.cost_lot
	def get_location_number(self, obj):
		return obj.warehouse_location.location_number
	def get_warehouse_name(self, obj):
		return obj.warehouse_entrance_pallet.warehouse.code
	def get_peso_bruto(self, obj):
		return obj.warehouse_entrance_pallet.gross_weight
	def get_peso_neto(self, obj):
		return obj.warehouse_entrance_pallet.net_weight