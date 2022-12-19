from rest_framework import serializers

from catalogs.product.models import Product
from catalogs.clients.models import Client
from catalogs.warehouse.models import WarehouseSection,WarehouseLocation
from ..models import WarehouseEntranceConfirmation,EntrancePalletPesoVariable,WarehouseEntrancePallet
class ProductSerializer(serializers.ModelSerializer):
	available_weight = serializers.SerializerMethodField()
	available_volume = serializers.SerializerMethodField()
	pallet = serializers.SerializerMethodField()

	product_location = serializers.CharField()
	class Meta:
		model = Product
		fields = ('id', 'product_code', 'product_description' , 'product_location','available_weight','available_volume', 'pallet', 'variable_weight',)

	def get_available_weight(self, obj):
		return obj.net_weight

	def get_available_volume(self, obj):
		return ((obj.length/100) * (obj.width/100) * (obj.height/100))

	def get_pallet(self, obj):
		return obj.packages_per_pallet

class WarehouseEntranceConfirmationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseEntranceConfirmation
		fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseSection
		fields = '__all__'

class PalletPesoVariableSerializer(serializers.ModelSerializer):
	class Meta:
		model = EntrancePalletPesoVariable
		fields = ('id', 'peso_variable_quantity','werehouse_entrance_pallet',)



class WarehouseLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WarehouseLocation
		fields = '__all__'

class WarehouseEntrancePalletSerializer(serializers.ModelSerializer):
	client_name = serializers.SerializerMethodField()
	product_description = serializers.SerializerMethodField()
	product_id = serializers.SerializerMethodField()
	warehouse_name = serializers.SerializerMethodField()
	warehouse_number = serializers.SerializerMethodField()
	warehouse_location_number = serializers.SerializerMethodField()
	available_gross_weight = serializers.SerializerMethodField()
	available_net_weight = serializers.SerializerMethodField()
	inventory_total_kg = serializers.SerializerMethodField()
	inventory_total_boxes = serializers.SerializerMethodField()
	inventory_available_total_boxes = serializers.SerializerMethodField()
	retained_boxes = serializers.SerializerMethodField()
	product_code = serializers.SerializerMethodField()
	location_uniq_code = serializers.SerializerMethodField()
	inventory_id = serializers.SerializerMethodField()
	product_per_pallet = serializers.SerializerMethodField()

	class Meta:
		model = WarehouseEntrancePallet
		fields = '__all__'

	def get_retained_boxes(self, obj):
		return obj.get_pallet_retained_boxes

	def get_client_name(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.werehouse_entrance.customer.name
		except:
			return ""

	def get_product_description(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.product.product_description
		except:
			return ""

	def get_warehouse_name(self, obj):
		try:
			return obj.warehouse.description
		except:
			return ""

	def get_warehouse_number(self, obj):
		if obj.rack_number:
			return obj.rack_number.index
		return 0


	def get_warehouse_location_number(self, obj):
		try:
			return obj.location.location_number
		except:
			return ""

	def get_product_id(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.product_id
		except:
			return 0

	def get_available_gross_weight(self, obj):
		return obj.get_pallet_available_gross_weight

	def get_available_net_weight(self, obj):
		return obj.get_pallet_available_net_weight

	def get_inventory_available_total_boxes(self, obj):
		return obj.get_pallet_inventory_available_total_boxes

	def get_inventory_total_boxes(self, obj):
		return obj.get_pallet_inventory_total_boxes

	def get_inventory_total_kg(self, obj):
		return obj.get_pallet_inventory_total_kg

	def get_product_code(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.product.product_code
		except:
			return ""
	def get_location_uniq_code(self, obj):
		if obj.location != None:
			return obj.location.shortcode
		else:
			return ""

	def get_inventory_id(self, obj):
		if obj.warehouseinventory_set.all().exists():
			return obj.warehouseinventory_set.first().id
		else:
			""
	def get_product_per_pallet(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.product.packages_per_pallet
		except:
			return ""

class EntrancePalletSerializer(serializers.ModelSerializer):
	client_name = serializers.SerializerMethodField()
	product_description = serializers.SerializerMethodField()
	entrance = serializers.SerializerMethodField()
	
	class Meta:
		model = WarehouseEntrancePallet
		fields = '__all__'

	def get_client_name(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.werehouse_entrance.customer.name
		except:
			return ""

	def get_product_description(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.product.product_description
		except:
			return ""

	def get_entrance(self, obj):
		try:
			return obj.werehouse_entrance_confirmation.werehouse_entrance.id
		except:
			return 0

class EntrancePalletMenuoverSerializer(serializers.ModelSerializer):
    pallet_url = serializers.SerializerMethodField()
    pallet_location_url = serializers.SerializerMethodField()    
    warehouse_name = serializers.SerializerMethodField()
    warehouse_number = serializers.SerializerMethodField()
    warehouse_location_number = serializers.SerializerMethodField()
    retained_reason = serializers.SerializerMethodField()
    class Meta:
        model = WarehouseEntrancePallet
        fields = ('pk','warehouse', 'location', 'palet_lot', 'rack_number', 'boxes', 'werehouse_entrance_confirmation', 'cost_lot', 'exp_date', 'gross_weight', 'net_weight', 'invoice_weight', 'retained_quantity', 'retained_reason', 'box_kg', 'confirmed','pallet_url','warehouse_name','warehouse_number','warehouse_location_number','pallet_location_url',)
        
    def get_pallet_url(self, obj):
        return obj.get_pallet_information
    def get_warehouse_name(self, obj):
    	if obj.warehouse:
        	return obj.warehouse.description
        else:
        	return ""
    def get_warehouse_number(self, obj):
        if obj.rack_number:
            return obj.rack_number.index
        return 0
    def get_warehouse_location_number(self, obj):
    	if obj.location:
        	return obj.location.location_number
        else:
        	return ""
    def get_pallet_location_url(self, obj):
        return obj.get_warehouse_information
    def get_retained_reason(self, obj):
        if obj.retained_reason != None:
            return obj.retained_reason
        else:
            return ""
class WarehouseEntranceConfirmation1Serializer(serializers.ModelSerializer):
	pallet_data = serializers.SerializerMethodField()
	product_id =  serializers.SerializerMethodField()
	product_desc = serializers.SerializerMethodField()
	retained_reason = serializers.SerializerMethodField()
	class Meta:
		model = WarehouseEntranceConfirmation
		fields = ('pk','code', 'product_id', 'product_desc', 'cost_lot', 'exp_date', 'gross_weight', 'net_weight', 'invoice_weight', 'retained_quantity', 'retained_reason','pallet_data','w_product_measurement',)
	def get_pallet_data(self, obj):
		return EntrancePalletMenuoverSerializer(obj.warehouseentrancepallet_set.all().order_by('id'),many=True).data
	def get_product_id(self, obj):
		return obj.product.pk
	def get_product_desc(self, obj):
		return obj.product.product_description
	def get_retained_reason(self, obj):
		try:
			return obj.retained_reason
		except:
			return ""