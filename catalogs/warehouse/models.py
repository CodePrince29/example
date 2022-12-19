from __future__ import unicode_literals
from django.db.models.signals import pre_save, post_save, pre_delete
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse

from catalogs.clients.models import Client
from users.models import UserProfile
from catalogs.product.models import Product
from catalogs.general_params.models import GeneralParams
from catalogs.product_family.models import ProductFamily
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Warehouse(models.Model):
    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')

    code = models.CharField(verbose_name=_('Code'), max_length=250, null=False, blank=False)
    description = models.CharField(verbose_name=_('Description'), max_length=255, blank=True)
    rows = models.PositiveIntegerField(verbose_name=_('Rows'), default=0)
    depth_levels = models.PositiveIntegerField(verbose_name=_('Depth Levels'), default=0)
    height_levels = models.PositiveIntegerField(verbose_name=_('Height Levels'), default=0)
    sections_per_row = models.PositiveIntegerField(verbose_name=_('Sections per Row'), default=0)

    def __str__(self):
        return self.code

    def __unicode__(self):
        return unicode(self.code)

    @property
    def total_locations(self):
        return int(self.rows) * int(self.sections_per_row) * int(self.height_levels) * int(self.depth_levels)

    def get_absolute_url(self):
        return reverse('warehouse-list')

    @property
    def rows_locations(self):
        return self.warehouserow_set.all().order_by('-index')
    @property
    def rows_location_entrance(self):
        return self.warehouserow_set.all().order_by('index')

       
    def deletable(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        from warehouses.warehouse_exit.models import WarehouseExitPallet
        result = WarehouseEntrancePallet.objects.filter(warehouse=self, warehouseinventory__available_total_boxes__gt=0)
        exit_warehouse = WarehouseExitPallet.objects.filter(warehouse=self, inventory__available_total_boxes__gt=0)
        if len(result) > 0 or len(exit_warehouse)>0:
            return False
        else:
            return True    

    def get_section(self,location_number):
        try:
            location_number = [int(i) for i in location_number.split(",")]
            total_rack = u""
            for row in self.rows_locations:
                for section in row.sections:
                    for height in section.heights:
                        for depth in height.depths:
                            if depth.warehouse_location.location_number in location_number:
                                if total_rack == "":
                                    total_rack = str(section.index)
                                else:
                                    # total_rack = total_rack + ", "+ str(section.index)
                                    total_rack = total_rack
            return total_rack
        except:
            return 0

    def get_section_id(self,location_number):
        try:
            location_number = [int(i) for i in location_number.split(",")]
            total_rack = u""
            for row in self.rows_locations:
                for section in row.sections:
                    for height in section.heights:
                        for depth in height.depths:
                            if depth.warehouse_location.location_number in location_number:
                                if total_rack == "":
                                    total_rack = str(section.id)
                                else:
                                    # total_rack = total_rack + ", "+ str(section.index)
                                    total_rack = total_rack
            return total_rack
        except:
            return 0

    def get_warehouse_section(self,location_number):
        try:            
            total_rack = u""
            for row in self.rows_locations:
                for section in row.sections:
                    for height in section.heights:
                        for depth in height.depths:
                            if depth.warehouse_location.location_number == int(location_number):
                                if total_rack == "":
                                    total_rack = str(section.index)
                                else:
                                    total_rack = total_rack
            return total_rack
        except:
            return 0



class WarehouseLocation(models.Model):
    class Meta:
        verbose_name = _('Warehouse Location')
        verbose_name_plural = _('Warehouse Locations')

    warehouse = models.ForeignKey(Warehouse, null=True, blank=False)
    location_number = models.PositiveIntegerField()
    total_stored_kg = models.FloatField(verbose_name=_('Total Stored Kg'), default=0)
    total_stored_boxes = models.PositiveIntegerField(verbose_name=_('Total Stored Boxes'), default=0)
    total_retained_boxes = models.PositiveIntegerField(verbose_name=_('Total Retained Boxes'), default=0)
    is_locked = models.BooleanField(verbose_name=_('Blocked Location'), default=False)
    available_weight = models.FloatField(verbose_name=_('Available Weight'), default=0)
    available_volume = models.FloatField(verbose_name=_('Available Volume'), default=0)
    shortcode = models.CharField(verbose_name=_('Short Code'), max_length=250, null=True, blank=True, unique=True)
    def __str__(self):
        return self.location_number

    def __unicode__(self):
        return unicode(self.location_number)

    def get_absolute_url(self):
        return reverse('warehouselocation-list')
    
    def has_broduct(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        location = len(WarehouseEntrancePallet.objects.filter(location=self.location_number))
        if location > 0:
            return True
        else:
            return False

    def get_rack(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        location = len(WarehouseEntrancePallet.objects.filter(location=self.location_number))
        if location > 0:
            return True
        else:
            return False

    def get_product(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        result = WarehouseEntrancePallet.objects.filter(location__location_number=self.location_number,warehouse_id=self.warehouse.id)
       
        if len(result)>0:            
            return list(result.values_list('werehouse_entrance_confirmation__product_id',flat=True))
        else:
            return list()

    def get_product_family(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        result = WarehouseEntrancePallet.objects.filter(location=self.id,warehouse_id=self.warehouse.id)
        if len(result)>0:            
            return list(result.values_list('werehouse_entrance_confirmation__product__product_family_id',flat=True))
        else:
            return list()

    def get_customer(self):
        from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
        result = WarehouseEntrancePallet.objects.filter(location=self.id,warehouse_id=self.warehouse.id)
        if len(result)>0:
            return list(result.values_list('werehouse_entrance_confirmation__werehouse_entrance__customer_id',flat=True))
        else:
            return list()        

class WarehouseInventory(models.Model):
    product = models.ForeignKey(Product, null=True)
    warehouse_location = models.ForeignKey(WarehouseLocation)
    warehouse_entrance_pallet = models.ForeignKey("warehouse_entrance.WarehouseEntrancePallet", null=True, blank=True)
    client = models.ForeignKey(Client, null=True)
    total_kg = models.FloatField(verbose_name=_('Total Kg'), default=0)
    total_boxes = models.PositiveIntegerField(verbose_name=_('Total Boxes'), default=0)
    exp_date = models.DateField(verbose_name=_('Expiration Date'), max_length=100, blank=True)
    rack = models.CharField(verbose_name=_('Rack Number'), max_length=250, null=True, blank=True)
    retained_boxes = models.IntegerField(verbose_name=_('Retained Qty'), blank=True,null=True)
    available_gross_weight = models.FloatField(verbose_name=_('Gross Weight'), default=0)
    available_net_weight = models.FloatField(verbose_name=_('Net Weight'), default=0)
    is_locked = models.BooleanField(verbose_name=_('Blocked Inventory'), default=False)
    available_total_boxes = models.PositiveIntegerField(verbose_name=_('Available Total Boxes'), default=0)
    
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        try:
            return str(_("Warehouse Location"))+" : "+str(self.warehouse_location.location_number) +" -- " + str(_("Product")) + " : "+str(self.product.product_description.encode('ascii', 'ignore').decode('ascii'))
        except:
            return str(self.id)
    @property
    def get_exit_total_boxes(self):
        from warehouses.warehouse_exit.models import WarehouseExit

        result = sum([float(confirm.boxes) for confirm in self.warehouseexitpallet_set.all().filter(werehouse_exit_confirmation__exit_product_measurement__werehouse_exit__status__in= ['InManeuvers', 'ManeuverComplete'])])
        return result
    @property
    def get_exit_total_kg(self):
        from warehouses.warehouse_exit.models import WarehouseExit

        result = sum([float(confirm.gross_weight) for confirm in self.warehouseexitpallet_set.all()])
        return result


class WarehouseInventoryLog(models.Model):
    warehouse_inventory = models.ForeignKey(WarehouseInventory)
    user = models.ForeignKey(UserProfile, null=True)
    total_kg = models.FloatField(verbose_name=_('Total Kg'), default=0)
    total_boxes = models.PositiveIntegerField(verbose_name=_('Total Boxes'), default=0)
    retained_boxes = models.IntegerField(verbose_name=_('Retained Qty'), blank=True,null=True)
    adjust_reason = models.CharField(verbose_name=_('Motivo del Ajuste'), blank=True,null=True, max_length=100)
    description = models.CharField(verbose_name=_('Ob Servaciones'), blank=True,null=True, max_length=200)
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.adjust_reason



    
class WarehouseRow(models.Model):
    warehouse = models.ForeignKey(Warehouse, null=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    index = models.PositiveIntegerField()

    @property
    def sections(self):
        return self.warehousesection_set.all().order_by('index')


class WarehouseSection(models.Model):
    index = models.PositiveIntegerField()
    row = models.ForeignKey(WarehouseRow)

    def __str__(self):
        return str(self.index)

    @property
    def heights(self):
        return self.warehouseheightlevel_set.all().order_by('index')


class WarehouseHeightLevel(models.Model):
    description = models.CharField(max_length=250, null=True, blank=True)
    index = models.PositiveIntegerField()
    section = models.ForeignKey(WarehouseSection)

    @property
    def depths(self):
        return self.warehousedepthlevel_set.all().order_by('index')


class WarehouseDepthLevel(models.Model):
    warehouse_location = models.ForeignKey(WarehouseLocation)
    description = models.CharField(max_length=250, null=True, blank=True)
    index = models.PositiveIntegerField()
    height = models.ForeignKey(WarehouseHeightLevel)
    depth_mts = models.FloatField(verbose_name=_('Depth MTS'), default=0)
    height_mts = models.FloatField(verbose_name=_('Height MTS'), default=0)
    width_mts = models.FloatField(verbose_name=_('Width MTS'), default=0)
    weight_kg = models.FloatField(verbose_name=_('Weight KG'), default=0)
    location_volume = models.FloatField(verbose_name=_('Location Volume'), default=0)

    def __str__(self):
        return self.warehouse_location.location_number

    def __unicode__(self):
        return unicode(self.warehouse_location.location_number)

    @property
    def location(self):
        return self.warehouse_location

    @property
    def get_depth_color(self): 
        total = self.weight_kg
        if total == 0:
            total=1
        available = self.warehouse_location.available_weight
        available_percent = (available*100)/total

        actual = 100 - available_percent
        if(actual >=0 and actual <=25):
           return self.get_color("ColorCapacity1","#548235")
        elif(actual >25 and actual <=50):
           return self.get_color("ColorCapacity2","#c6e0b4")
        elif(actual >50 and actual <=75):
           return self.get_color("ColorCapacity3","#ffff00")
        elif(actual >75 and actual <=85):
           return self.get_color("ColorCapacity4","#ffc000")
        elif(actual >85 and actual <=100):
           return self.get_color("ColorCapacity5","#c00000")
        else:
            return self.get_color("ColorCapacity6","#808080")

    def get_color(self,color_key,color):
        param = GeneralParams.objects.filter(key=color_key)
        if param.exists():
            color = param.first().value
        return color  



    @property
    def get_rack_details(self):
        warehouse_name = (self.warehouse_location.warehouse.description).replace(' ','_')
        warehouse_id = self.warehouse_location.warehouse.id
        rack_id = self.height.section.id
        rack_index = self.height.section.index
        location_id = self.warehouse_location.id
        location_number = self.warehouse_location.location_number
        data = '%22WarehouseName%22:%22{0}%22,%22WarehouseId%22:%22{1}%22,%22RackId%22:%22{2}%22,%22RackIndex%22:%22{3}%22,%22LocationId%22:%22{4}%22,%22LocationNumber%22:%22{5}%22'.format(warehouse_name,warehouse_id,rack_id, rack_index, location_id, location_number)
        return "{%s}"%data

class Branch(models.Model):
    class Meta:
        verbose_name = _('Branch')
        verbose_name_plural = _('Branch')

    name = models.CharField(max_length=250, verbose_name=_('Name'))
    address = models.CharField(max_length=250, verbose_name=_('Address'))
    total_bays = models.IntegerField(verbose_name=_('Truck Bays'),default=0)
    service_interval = models.FloatField(verbose_name=_('Service Interval'),default=0)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)

    def __str__(self):
        return self.name

    @property
    def deletable(self):
        return not self.warehousetruckbays_set.filter(loading=True).exists()
    
class WarehouseTruckBays(models.Model):
    class Meta:
        verbose_name=_('Warehouse Truck Bays')
        verbose_name_plural = _('Warehouse Truck Bays')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    branch = models.ForeignKey(Branch, null=True, blank=True, on_delete=models.CASCADE)
    time_slot = models.DateTimeField(verbose_name=_('Time'))
    bay = models.IntegerField(verbose_name=_('Truck Bay'),default=0)
    loading = models.BooleanField(verbose_name=_('Contain Vehicle is loading'),default=True)
    

    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)

    def __str__(self):
        return str(self.bay)