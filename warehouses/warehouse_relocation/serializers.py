from rest_framework import serializers
from warehouses.warehouse_entrance.models import WarehouseEntrance,WProductMeasurement,WarehouseEntrancePallet, WarehouseEntranceConfirmation
from catalogs.warehouse.models import WarehouseLocation
from .models import WarehouseRelocation

class WarehouseEntranceSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntrance
		fields = '__all__'

class WarehouseEntranceConfirmationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntranceConfirmation
		fields = '__all__'

class WarehouseSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseLocation
		fields = ('id', 'location_number','shortcode',)

class WarehouseRelocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseRelocation
		fields = '__all__'

class WarehouseEntranceConfirmationProductSerializer(serializers.ModelSerializer):

	warehouse_detail = serializers.SerializerMethodField('get_warehouse_name')
	location_detail = serializers.SerializerMethodField('get_location_detail_id')
	class Meta:
		model = WarehouseEntranceConfirmation
		fields = ( 'id','warehouse_detail', 'warehouse', 'location','location_detail')

	def get_warehouse_name(self, obj):
		return obj.warehouse.code


	def get_location_detail_id(self, obj):
		warehouse = WarehouseLocation.objects.get(warehouse=obj.warehouse,location_number=obj.location).id
		return warehouse

class WarehousePalletSerializer(serializers.ModelSerializer):
	customer = serializers.SerializerMethodField('get_customer_name')
	product_description = serializers.SerializerMethodField('get_product_name')
	getavailable_boxes = serializers.SerializerMethodField('get_available_boxes')
	werehouse_entrance = serializers.SerializerMethodField()
	code = serializers.SerializerMethodField()
	cost_lot = serializers.SerializerMethodField()
	exp_date = serializers.SerializerMethodField()
	gross_weight = serializers.SerializerMethodField()
	retained_quantity = serializers.SerializerMethodField()
	warehouse_detail = serializers.SerializerMethodField()
	location_detail = serializers.SerializerMethodField()
	class Meta:
		model = WarehouseEntrancePallet
		fields = ( 'warehouse','location','warehouse_detail','location_detail', 'werehouse_entrance','customer', 'code', 'product_description', 'cost_lot', 'palet_lot', 'exp_date', 'gross_weight','retained_quantity','getavailable_boxes')

	def get_customer_name(self, obj):
		return obj.werehouse_entrance_confirmation.product.customer.name

	def get_product_name(self, obj):
		return obj.werehouse_entrance_confirmation.product.product_description

	def get_available_boxes(self, obj):
		available_boxes = WProductMeasurement.objects.filter(werehouse_entrance=obj.werehouse_entrance_confirmation.werehouse_entrance,product=obj.werehouse_entrance_confirmation.product).first().boxes
		return available_boxes

	def get_code(self, obj):
		return obj.werehouse_entrance_confirmation.product.product_code

	def get_werehouse_entrance(self, obj):
		return obj.werehouse_entrance_confirmation.werehouse_entrance.id

	def get_cost_lot(self, obj):
		return obj.werehouse_entrance_confirmation.cost_lot
	def get_exp_date(self, obj):
		return obj.werehouse_entrance_confirmation.exp_date

	def get_gross_weight(self, obj):
		return str(obj.werehouse_entrance_confirmation.gross_weight)
	def get_retained_quantity(self, obj):
		return str(obj.werehouse_entrance_confirmation.retained_quantity)

	def get_warehouse_detail(self, obj):
		return obj.warehouse.code

	def get_location_detail(self, obj):
		return obj.location.location_number