from rest_framework import serializers
from catalogs.product_family.models import ProductFamily
from catalogs.product.models import Product
from catalogs.clients.models import Client
from warehouses.warehouse_entrance.models import WarehouseEntranceConfirmation,WProductMeasurement,WarehouseEntrancePallet
from warehouses.warehouse_exit.models import WExitConfirmation,WarehouseExitPallet,WExitProductMeasurement
from warehouses.warehouse_relocation.models import WarehouseRelocation

from .models import WarehouseInventory, WarehouseLocation

class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'product_code','product_description',)


class ProductFamilySerializer(serializers.ModelSerializer):
	product = ProductSerializer(source='product_set', many=True)
	class Meta:
		model = ProductFamily
		fields = ('id', 'code', 'description', 'product',)

class WarehouseInventorySerializer(serializers.ModelSerializer):
	customer_data = serializers.SerializerMethodField('get_customer_name')
	product_data = serializers.SerializerMethodField('get_product_code')
	lote_tarima = serializers.SerializerMethodField()
	lote_cliente = serializers.SerializerMethodField()

	
	class Meta:
		model = WarehouseInventory
		fields = ('id', 'customer_data','total_kg','total_boxes','exp_date','product_data','retained_boxes','lote_tarima','lote_cliente','available_gross_weight', 'available_total_boxes',)

	def get_customer_name(self, obj):
		return obj.client.name

	def get_product_code(self, obj):
		return obj.product.product_code

	def get_lote_tarima(self, obj):
		return obj.warehouse_entrance_pallet.palet_lot
	def get_lote_cliente(self, obj):
		return obj.warehouse_entrance_pallet.cost_lot

class WarehouseInventoryFilterSerializer(serializers.ModelSerializer):
	customer_data = serializers.SerializerMethodField('get_customer_name')
	product_data = serializers.SerializerMethodField('get_product_code')

	
	class Meta:
		model = WarehouseInventory
		fields = ('id','location_number', 'customer_data','total_kg','total_boxes','retained_boxes')

	def get_customer_name(self, obj):
		return obj.client.name

	def get_product_code(self, obj):
		return obj.product.product_code
	


class WarehouseEntranceConfirmationSerializer(serializers.ModelSerializer):
	customer = serializers.SerializerMethodField('get_customer_name')
	product_description = serializers.SerializerMethodField('get_customer_name')
	getavailable_boxes = serializers.SerializerMethodField('get_available_boxes')
	class Meta:
		model = WarehouseEntranceConfirmation
		fields = ( 'werehouse_entrance','customer', 'code', 'product_description', 'cost_lot', 'palet_lot', 'exp_date', 'gross_weight','retained_quantity','getavailable_boxes')

	def get_customer_name(self, obj):
		return obj.product.customer.name

	def get_product_name(self, obj):
		return obj.product.product_description

	def get_available_boxes(self, obj):
		available_boxes = WProductMeasurement.objects.filter(werehouse_entrance=obj.werehouse_entrance,product=obj.product).first().boxes
		return available_boxes

class WarehouseExitPalletSerializer(serializers.ModelSerializer):
	customer = serializers.SerializerMethodField('get_customer_name')
	product_description = serializers.SerializerMethodField('get_product_name')
	getavailable_boxes = serializers.SerializerMethodField('get_available_boxes')
	werehouse_exit = serializers.SerializerMethodField()
	code = serializers.SerializerMethodField()
	cost_lot = serializers.SerializerMethodField()
	exp_date = serializers.SerializerMethodField()
	gross_weight = serializers.SerializerMethodField()
	retained_quantity = serializers.SerializerMethodField()
	class Meta:
		model = WarehouseEntrancePallet
		fields = ( 'werehouse_exit','customer', 'code', 'product_description', 'cost_lot', 'palet_lot', 'exp_date', 'gross_weight','retained_quantity','getavailable_boxes','box_kg')

	def get_customer_name(self, obj):
		return obj.werehouse_exit_confirmation.product.customer.name

	def get_product_name(self, obj):
		return obj.werehouse_exit_confirmation.product.product_description

	def get_available_boxes(self, obj):
		return obj.boxes

	def get_code(self, obj):
		return obj.werehouse_exit_confirmation.product.product_code

	def get_werehouse_exit(self, obj):
		return obj.werehouse_exit_confirmation.werehouse_exit.id

	def get_cost_lot(self, obj):
		return obj.cost_lot
	def get_exp_date(self, obj):
		return obj.exp_date

	def get_gross_weight(self, obj):
		return str(obj.gross_weight)
	def get_retained_quantity(self, obj):
		return str(obj.retained_quantity)
	
		
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
	class Meta:
		model = WarehouseEntrancePallet
		fields = ( 'werehouse_entrance','customer', 'code', 'product_description', 'cost_lot', 'palet_lot', 'exp_date', 'gross_weight','retained_quantity','getavailable_boxes','box_kg')

	def get_customer_name(self, obj):
		return obj.werehouse_entrance_confirmation.product.customer.name

	def get_product_name(self, obj):
		return obj.werehouse_entrance_confirmation.product.product_description

	def get_available_boxes(self, obj):
		# available_boxes = WProductMeasurement.objects.filter(werehouse_entrance=obj.werehouse_entrance_confirmation.werehouse_entrance,product=obj.werehouse_entrance_confirmation.product).first().boxes
		return obj.boxes

	def get_code(self, obj):
		return obj.werehouse_entrance_confirmation.product.product_code

	def get_werehouse_entrance(self, obj):
		return obj.werehouse_entrance_confirmation.werehouse_entrance.id

	def get_cost_lot(self, obj):
		return obj.cost_lot
	def get_exp_date(self, obj):
		return obj.exp_date

	def get_gross_weight(self, obj):
		return str(obj.gross_weight)
	def get_retained_quantity(self, obj):
		return str(obj.retained_quantity)


class WarehouseExitConfirmationSerializer(serializers.ModelSerializer):
	customer = serializers.SerializerMethodField('get_customer_name')
	product_description = serializers.SerializerMethodField('get_customer_name')
	getavailable_boxes = serializers.SerializerMethodField('get_available_boxes')
	class Meta:
		model = WExitConfirmation
		fields = ( 'werehouse_exit','customer', 'code', 'product_description', 'cost_lot', 'palet_lot', 'exp_date', 'gross_weight','retained_quantity','getavailable_boxes')

	def get_customer_name(self, obj):
		return obj.product.customer.name

	def get_product_name(self, obj):
		return obj.product.product_description
	def get_available_boxes(self, obj):
		available_boxes = WExitProductMeasurement.objects.get(werehouse_exit=obj.werehouse_exit,product=obj.product).boxes
		return available_boxes


class WarehouseRelocationSerializer(serializers.ModelSerializer):
	customer = serializers.SerializerMethodField('get_customer_name')
	gettotal_kg = serializers.SerializerMethodField('get_total_kg')
	product = serializers.SerializerMethodField('get_product_description')
	s_location_number = serializers.SerializerMethodField('get_source_location_number')
	s_warehouse_code = serializers.SerializerMethodField('get_source_warehouse_code')
	d_location_number = serializers.SerializerMethodField('get_dest_location_number')
	d_warehouse_code = serializers.SerializerMethodField('get_dest_warehouse_code')
	entrance_id = serializers.SerializerMethodField('get_w_entrance_id')
	s_location_short_code = serializers.SerializerMethodField('get_source_location_short_code')
	d_location_short_code = serializers.SerializerMethodField('get_dest_location_short_code')
	class Meta:
		model = WarehouseRelocation
		fields = ( 'id','description','customer','entrance_id', 'product','palet_lot','gettotal_kg','source_warehouse','source_location','destination_warehouse','destination_location','d_location_number','d_warehouse_code','s_location_number','s_warehouse_code','s_location_short_code', 'd_location_short_code')
	
	def get_w_entrance_id(self, obj):
		return obj.werehouse_entrance.id

	def get_customer_name(self, obj):
		return obj.customer.name

	def get_total_kg(self, obj):
		return obj.werehouse_entrance.total_kg

	def get_product_description(self, obj):
		return obj.product.product_code

	def get_dest_location_number(self, obj):
		return obj.destination_location.location_number

	def get_dest_warehouse_code(self, obj):
		return obj.destination_warehouse.code

	def get_source_location_number(self, obj):
		if obj.source_location:
			results = WarehouseLocation.objects.filter(id=obj.source_location)
			if results.exists():
				return results.first().location_number
		return ''


	def get_source_warehouse_code(self, obj):
		if obj.source_location:
			results = WarehouseLocation.objects.filter(id=obj.source_location)
			if results.exists():
				return results.first().warehouse.code
		return ''

	def get_source_location_short_code(self, obj):
		if obj.source_location:
			results = WarehouseLocation.objects.filter(id=obj.source_location)
			if results.exists():
				return results.first().shortcode
		return ''
	def get_dest_location_short_code(self, obj):
		if obj.source_location:
			results = WarehouseLocation.objects.filter(id=obj.source_location)
			if results.exists():
				return results.first().shortcode
		return ''

	
