from rest_framework import serializers
from catalogs.warehouse.models import WarehouseLocation
from catalogs.product.models import Product
from warehouses.warehouse_exit.models import WExitConfirmation , ExitPalletPesoVariable, WarehouseExitPallet
from warehouses.warehouse_entrance.models import EntrancePalletPesoVariable
class ProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product
		fields = ('id', 'product_code', 'customer_product_code',
			'product_family', 'product_description', 'gross_weight',
			'net_weight', 'variable_weight', 'storage_type', 'beds_per_pallet',
			'packages_per_pallet', 'min_expiration_for_reception', 'min_expiration_for_shipping')

class WarehouseLocationSerializer(serializers.ModelSerializer):
	product = ProductSerializer()
	class Meta:
		model = WarehouseLocation
		fields = ('product', 'location_number')

class WExitConfirmationSerializer(serializers.ModelSerializer):
	class Meta:
		model = WExitConfirmation
		fields = '__all__'

class PalletPesoVariableSerializer(serializers.ModelSerializer):
	class Meta:
		model = ExitPalletPesoVariable
		fields = '__all__'

class EntrancePalletPesoVariableSerializer(serializers.ModelSerializer):
	class Meta:
		model = EntrancePalletPesoVariable
		fields = '__all__'

class ExitPalletMenuoverSerializer(serializers.ModelSerializer):
    pallet_url = serializers.SerializerMethodField()
    pallet_location_url = serializers.SerializerMethodField()  
    warehouse_name = serializers.SerializerMethodField()
    warehouse_number = serializers.SerializerMethodField()
    warehouse_location_number = serializers.SerializerMethodField()
    retained_reason = serializers.SerializerMethodField()
    class Meta:
        model = WarehouseExitPallet
        fields = ('pk','warehouse', 'location', 'palet_lot', 'rack_number', 'boxes', 'werehouse_exit_confirmation', 'cost_lot', 'exp_date', 'gross_weight', 'net_weight', 'invoice_weight', 'retained_quantity', 'retained_reason', 'box_kg', 'confirmed','warehouse_name','warehouse_number','warehouse_location_number','pallet_url','pallet_location_url')    
    def get_warehouse_name(self, obj):
        return obj.warehouse.description    
    def get_warehouse_number(self, obj):
        if obj.rack_number:
            return obj.rack_number.index
        return 0
    def get_warehouse_location_number(self, obj):
        try:
            return obj.location.location_number  
        except:
            return ""
            
    def get_retained_reason(self, obj):
        try:
            return obj.retained_reason
        except:
            return ""
    def get_pallet_url(self, obj):
        return obj.get_exit_pallet_information

    def get_pallet_location_url(self, obj):
        return obj.get_exit_warehouse_information

class WarehouseExitConfirmationPalletSerializer(serializers.ModelSerializer):
    exit_pallet_data = serializers.SerializerMethodField()
    product_id =  serializers.SerializerMethodField()
    product_desc = serializers.SerializerMethodField()
    retained_reason = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    class Meta:
        model = WExitConfirmation
        fields = ('pk','code', 'product_id', 'product_desc', 'cost_lot', 'exp_date', 'gross_weight', 'net_weight', 'invoice_weight', 'retained_quantity', 'retained_reason','exit_pallet_data','exit_product_measurement')

    def get_exit_pallet_data(self, obj):
        return ExitPalletMenuoverSerializer(obj.warehouseexitpallet_set.all().order_by('id'),many=True).data
    def get_product_id(self, obj):
        return obj.product.pk
    def get_product_desc(self, obj):
        return obj.product.product_description
    def get_code(self, obj):
        return obj.product.product_code
    def get_retained_reason(self, obj):
        try:
            return obj.retained_reason
        except:
            return ""

class WarehouseExitConfirmationPalletConfSerializer(serializers.ModelSerializer):
    exit_pallet_data = serializers.SerializerMethodField()
    total_pallet_count = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    class Meta:
        model = WExitConfirmation
        fields = ('id',
                'product_name',
                'product_id',
                'total_pallet_count',
                'exit_pallet_data',
                'exit_product_measurement',
                'cost_lot',
                'exp_date',
                'gross_weight',
                'net_weight',
                'invoice_weight',
                'retained_quantity',
                'retained_reason',)

    def get_exit_pallet_data(self, obj):
        return WarehousePalletConfSerializer(obj.warehouseexitpallet_set.all().order_by('id'),many=True).data
            
    def get_total_pallet_count(self, obj):
        return obj.warehouseexitpallet_set.all().count()

    def get_product_name(self, obj):
        return obj.product.product_description

    def get_product_id(self, obj):
        return obj.product.id

class WarehousePalletConfSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.SerializerMethodField()
    warehouse_number = serializers.SerializerMethodField()
    warehouse_location_number = serializers.SerializerMethodField()
    inventory_id = serializers.SerializerMethodField()
    inventory_gross_weight = serializers.SerializerMethodField()
    inventory_net_weight = serializers.SerializerMethodField()
    location_code = serializers.SerializerMethodField()
    class Meta:
        model = WarehouseExitPallet
        fields = ('id',
                'warehouse_name',
                'warehouse_number',
                'warehouse_location_number',
                'inventory_id',
                'inventory_gross_weight',
                'inventory_net_weight',
                'palet_lot',
                'boxes',
                'box_kg',
                'warehouse',
                'rack_number',
                'location',
                'cost_lot',
                'exp_date',
                'gross_weight',
                'net_weight',
                'invoice_weight',
                'retained_quantity',
                'retained_reason',
                'inventory',
                'werehouse_exit_confirmation',
                'location_code',
                'confirmed'
                )

    def get_warehouse_name(self, obj):
        return obj.warehouse.code    
    def get_warehouse_number(self, obj):
        try:
            return obj.rack_number.index
        except:
            return 0
    def get_warehouse_location_number(self, obj):
        try:
            return obj.location.location_number
        except:
            return ""

    def get_inventory_id(self, obj):
        return obj.inventory_id

    def get_inventory_gross_weight(self, obj):
        try:
            return obj.inventory.available_gross_weight
        except:
            return 0

    def get_inventory_net_weight(self, obj):
        try:
            return obj.inventory.available_net_weight
        except:
            return 0
    def get_location_code(self, obj):
        try:
            return obj.location.shortcode
        except:
            return 0
class WarehouseExitPalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseExitPallet
        fields = '__all__'



class WarehouseExitPalletDetailSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = WarehouseExitPallet
        fields = '__all__'

    def get_retained_boxes(self, obj):
        return obj.get_pallet_retained_boxes

    def get_client_name(self, obj):
        try:
            return obj.werehouse_exit_confirmation.werehouse_entrance.customer.name
        except:
            return ""

    def get_product_description(self, obj):
        try:
            return obj.werehouse_exit_confirmation.product.product_description
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
            return obj.werehouse_exit_confirmation.product_id
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
            return obj.werehouse_exit_confirmation.product.product_code
        except:
            return ""
    def get_location_uniq_code(self, obj):
        if obj.location != None:
            return obj.location.shortcode
        else:
            return ""
