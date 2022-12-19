
from __future__ import unicode_literals
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.db.models.signals import pre_save, post_save
from catalogs.warehouse.models import Warehouse, WarehouseInventory,WarehouseLocation,WarehouseSection
from django.dispatch import receiver
from decimal import Decimal
from catalogs.general_params.models import GeneralParams
from django.db.models import Sum, Q
import datetime
from django.db.models import F
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from catalogs.notifications.models import Notification
from catalogs.warehouse.models import WarehouseTruckBays
from users.models import UserProfile
from django.utils.functional import cached_property
from django.urls import reverse_lazy
from django.db.models.functions import Cast, Coalesce


class WarehouseEntranceFinishedQuerySet(models.QuerySet):
    def finished_objects(self):
        return self.filter(status=WarehouseEntrance.FINISH)


class WarehouseEntranceFinished(models.Manager):
    def get_queryset(self):
        return WarehouseEntranceFinishedQuerySet(self.model, using=self._db)  # Important!

    def finished_objects(self):
        return self.get_queryset().finished_objects()

class WarehouseEntrance(models.Model):
    PENDING = "control"
    IN_RECEIPT = 'in_receipt'
    FINISH = 'finish'
    IN_MANEUVERS = "InManeuvers"
    MANEUVER_COMPLETE = "ManeuverComplete"   

    STATUS = (
        (PENDING, _('Control')),
        (IN_RECEIPT, _('In Receipt')), 
        (IN_MANEUVERS, _('In Maneuvers')),
        (MANEUVER_COMPLETE,_("Maneuver Complete")),
        (FINISH, _('Finish')))

    PACKEGED = 'P'
    LOOSE = 'A'
    CARGO_TYPE = ((PACKEGED, _('P')), 
        (LOOSE, _('A')))

    entrance_date = models.DateField(verbose_name=_('Entrance Date'))
    entrance_hour = models.TimeField(verbose_name=_('Entrance Hour'),blank=True)
    carrier = models.ForeignKey(Carrier, null=False,verbose_name=_('Carrier'))
    vehicle = models.ForeignKey(Vehicle, null=False,verbose_name=_('Vehicle'))
    license_plate = models.CharField(verbose_name=_('License Plates'), max_length=250, null=True, blank=True)
    customer = models.ForeignKey(Client, null=False,verbose_name=_('Customer'))

    total_kg = models.FloatField(verbose_name=_('Total Kg'), null=True, blank=True,default=0)  

    total_price = models.FloatField(verbose_name=_('Total Price'), null=True, blank=True,default=0)
    kg_per_price = models.FloatField(verbose_name=_('Kg Per Price'), null=True, blank=True,default=0)
    boxes = models.IntegerField(verbose_name=_('Boxes'), null=True, blank=True,default=0)
    kg_per_boxes = models.FloatField(verbose_name=_('Kg Per Box'), null=True, blank=True,default=0)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)

    vehicle_temograph = models.IntegerField(verbose_name=_('Vehicle has Termograph'),default=0)
    temprature_cel = models.IntegerField(verbose_name=_('Temperature celcious'),default=0)
    cont_flr_sta = models.IntegerField(verbose_name=_('Container Floor Status'),default=0)
    fasteners = models.IntegerField(verbose_name=_('Fasteners'),default=0)
    container_clean = models.IntegerField(verbose_name=_('Container Clean'),default=0)
    inside_container_good = models.IntegerField(verbose_name=_('Inside The Container is in Good Condition'),default=0)
    loading_availity = models.BooleanField(verbose_name=_('ContainVehicle able for loading/unloading'),default=0)
    notes = models.CharField(verbose_name=_('Notes'), max_length=255, blank=True)

    prente = models.BooleanField(verbose_name=_('Frente'),default= False)
    lado_izquerdo = models.BooleanField(default= False)
    vista_inferior = models.BooleanField(default= False)
    puerta_tresera_deregha = models.BooleanField(default= False)
    duerta_tresera_inquiera = models.BooleanField(default= False)
    techa = models.BooleanField(default= False)
    puerta_referal = models.BooleanField(default= False)
    puerta = models.BooleanField(default= False)
    lado_denecha = models.BooleanField(default= False)
    status = models.CharField(verbose_name=_('Warehouse Entrance Status'), max_length=20, default=PENDING, null=False, blank=False, choices=STATUS)
    cargo_type =  models.CharField(verbose_name=_('Cargo Type'), max_length=100, choices=CARGO_TYPE)
    cargo_sender = models.CharField(verbose_name=_('Cargo Sender'), max_length=100, blank=True, default="")
    # new driver info
    driver_name = models.CharField(verbose_name=_('Name Of The Driver'), max_length=100, blank=True, default="")
    temp_front = models.FloatField(verbose_name=_('Temprature Front'), default=0)
    temp_middle = models.FloatField(verbose_name=_('Temprature Middel'), default=0)
    temp_back = models.FloatField(verbose_name=_('Temprature Back'), default=0)

    cust_reference = models.CharField(verbose_name=_('Referencia'), max_length=255, blank=True, default="")
    seal1 = models.CharField(verbose_name=_('Fleje/Sello 1'), max_length=255, blank=True, default="")
    seal2 = models.CharField(verbose_name=_('Fleje/Sello 2'), max_length=255, blank=True, default="")
    created_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Created By'))
    confirmed_at = models.DateTimeField(verbose_name=_('Confirmed At'),auto_now_add=False, null=True, blank=True)
    sent_to_maniobras_at = models.DateTimeField(verbose_name=_('Sent to Maniobras At'),auto_now_add=False, null=True, blank=True)

    sent_to_maniobras_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Sent To Maniobras by'), related_name='entrance_maniobras_by')
    confirmed_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Confirmed by'), related_name='entrance_confirmed_by')

    notifications = GenericRelation(Notification)
    bays = GenericRelation(WarehouseTruckBays)

    objects = WarehouseEntranceFinished()
    def __str__(self):
        return str(self.id) +"---#-"+ str(self.entrance_date)

    def __unicode__(self):
        return str(self.id) +"---#-"+ str(self.entrance_date)

    def get_confirm_products(self, pallet_id=None):
        from .models import WarehouseEntrancePallet
        if pallet_id == None:
            
            products = self.warehouseentranceconfirmation_set.all().order_by('product_id').annotate(
                p_id=F('id'),
                p_product_id=F('product_id'),
                p_product_code= F('product__product_code'),
                p_product_length= F('product__length'),
                p_product_width= F('product__width'),
                p_product_height= F('product__height'),
                p_net_weight=F('product__net_weight'),
                total_boxes=Sum('warehouseentrancepallet__boxes')).values(
                'p_id','p_product_id', 'p_product_code',
                'p_product_length','p_product_width','p_product_height',
                'p_net_weight','total_boxes')
           
            # values('id', 'product_id', 'product__product_code','product__length','product__width','product__height','product__net_weight')
        else:
            products = WarehouseEntrancePallet.objects.filter(id=pallet_id).annotate(
                p_id=F('werehouse_entrance_confirmation__id'), 
                p_product_id = F('werehouse_entrance_confirmation__product_id'), 
                p_product_code = F('werehouse_entrance_confirmation__product__product_code'),
                p_product_length = F('werehouse_entrance_confirmation__product__length'),
                p_product_width = F('werehouse_entrance_confirmation__product__width'),
                p_product_height=F('werehouse_entrance_confirmation__product__height'),
                p_net_weight = F('werehouse_entrance_confirmation__product__net_weight'),
                total_boxes=Sum('boxes')).values(
                'p_id','p_product_id', 'p_product_code',
                'p_product_length','p_product_width','p_product_height',
                'p_net_weight','total_boxes')
        return products

    def get_product_measurementss(self, pallet_id=None):
        
        from .models import WarehouseEntrancePallet
        if pallet_id == None:
            measurement = self.wproductmeasurement_set.all().order_by('product_id').annotate(pm_id=F('id'),pm_product_id=F('product_id'),pm_boxes= F('boxes')).values('pm_id','pm_product_id', 'pm_boxes')
        else:
            measurement = WarehouseEntrancePallet.objects.filter(id=pallet_id).annotate(pm_id=F('werehouse_entrance_confirmation__w_product_measurement_id'),pm_product_id=F('werehouse_entrance_confirmation__w_product_measurement__product_id'),pm_boxes= F('werehouse_entrance_confirmation__w_product_measurement__boxes')).values('pm_id','pm_product_id', 'pm_boxes')
        return measurement

    def get_confirm_product_warehous(self, pallet_id=None):
        from .models import WarehouseEntrancePallet
        confirmation = self.warehouseentranceconfirmation_set.all().values_list('id')
        if pallet_id == None:
            warehouses = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=confirmation ).values('warehouse_id', 'warehouse__code')
        else:
            warehouses = WarehouseEntrancePallet.objects.filter(id=pallet_id).values('warehouse_id', 'warehouse__code')
        return warehouses

    # def get_confirm_palet_lot_warehous(self,pallet_id):
    #     from .models import WarehouseEntrancePallet
        
    #     return warehouses

    def get_confirm_product_entrance(self, pallet_id=None):
        from .models import WarehouseEntrancePallet
        confirmation = self.warehouseentranceconfirmation_set.all().values_list('id')
        if pallet_id == None:
            warehouses = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=confirmation).values('werehouse_entrance_confirmation__werehouse_entrance__id')
        else:
            warehouses = WarehouseEntrancePallet.objects.filter(id=pallet_id).values('werehouse_entrance_confirmation__werehouse_entrance__id') 
        return warehouses

    # def get_palet_lot_entrance(self,pallet_id):
    #     from .models import WarehouseEntrancePallet
    #     warehouses = WarehouseEntrancePallet.objects.filter(id=pallet_id).values('werehouse_entrance_confirmation__werehouse_entrance__id')
    #     return warehouses

    def get_confirm_product_locations(self, pallet_id=None):
        from .models import WarehouseEntrancePallet
        confirmation = self.warehouseentranceconfirmation_set.all().values_list('id')
        if pallet_id == None:
            query_result = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=confirmation ).values('location_id','location__location_number')
        else:
            query_result = WarehouseEntrancePallet.objects.filter(id=pallet_id).values('location_id','location__location_number')
        return query_result

    # def get_confirm_palet_lot_locations(self,pallet_id):
    #     from .models import WarehouseEntrancePallet
    #     query_result = WarehouseEntrancePallet.objects.filter(id=pallet_id).values('location_id','location__location_number')
    #     return query_result

    @property
    def get_total_gross_weight(self):
        result = sum([float(confirm.gross_weight) for confirm in self.warehouseentranceconfirmation_set.all()])
        return result
    @property
    def get_total_pallet_gross_weight(self):
        result = sum([float(confirm.gross_weight) for confirm in WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=self.warehouseentranceconfirmation_set.all().values_list('id',flat=True))])
        return result

    @property
    def get_total_net_weight(self):

        result = sum([float(confirm.net_weight) for confirm in self.warehouseentranceconfirmation_set.all()])
        return result
    @property
    def get_total_pallet_net_weight(self):

        result = sum([float(confirm.net_weight) for confirm in WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=self.warehouseentranceconfirmation_set.all().values_list('id',flat=True))])
        return result

    @property
    def get_total_boxes(self):

        result = sum([float(confirm.get_total_quantity) for confirm in self.warehouseentranceconfirmation_set.all()])
        return result
    @property
    def get_total_pallet_boxes(self):
        result = sum([float(confirm.boxes) for confirm in WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=self.warehouseentranceconfirmation_set.all().values_list('id',flat=True))])
        return int(result)

    @property
    def get_total_pallet_boxes_kgs(self):
        result = sum([float(confirm.box_kg) for confirm in WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=self.warehouseentranceconfirmation_set.all().values_list('id',flat=True))])
        return result

    def __get_label(self, field):
        from six import text_type
        return text_type(self._meta.get_field(field).verbose_name)

    @property
    def access_label(self, name):
        return self.__get_label(name)

    @property
    def list_product(self):
        return self.wproductmeasurement_set.all().order_by('id')

    @property
    def is_qr_enable(self):
        gp = GeneralParams.objects.filter(key="QR_Read")
        if gp.exists() and gp.first().value == "1":
            return True
        else:
            return False
    @property
    def is_qr_disable(self):
        gp = GeneralParams.objects.filter(key="QR_Read")
        if gp.exists() and gp.first().value != "1":
            return True
        else:
            return False

    @property
    def absolute_url(self):
        return reverse_lazy('update-entrance', args=[self.id])

    @property
    def absolute_maneobras_url(self):
        return reverse_lazy('maniobras-entrance-update', args=[self.id])

    @property
    def entrance_confirm_btn_disabled(self):
        from .models import WarehouseEntrancePallet
        pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance_id=self.id, maniobras=False)
        if pallets.exists():
            return True
        else:
            return False


class WProductMeasurement(models.Model):
    total_kg = models.FloatField(verbose_name=_('Total Kg'), null=True, blank=True,default=0)
    price = models.FloatField(verbose_name=_('Total Price'), null=True, blank=True,default=0)
    kg_per_price = models.FloatField(verbose_name=_('Kg Per Price'), null=True, blank=True,default=0)
    boxes = models.IntegerField(verbose_name=_('Boxes'), null=True, blank=True,default=0)
    kg_per_boxes = models.FloatField(verbose_name=_('Kg Per Box'), null=True, blank=True,default=0)
    werehouse_entrance = models.ForeignKey(WarehouseEntrance, null=False,verbose_name=_('Entrance'))
    product = models.ForeignKey(Product, null=False,verbose_name=_('Product'))
    product_description = models.CharField(verbose_name=_('Description'), max_length=60)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
    control_total_boxes = models.IntegerField(verbose_name=_('Control Total Boxes'), null=True, blank=True,default=0)  
    control_total_kg = models.FloatField(verbose_name=_('Control Total Kg'), null=True, blank=True,default=0)
    
    # def delete(self, *args, **kwargs):
    #    WarehouseEntranceConfirmation.objects.filter(product=self.product, werehouse_entrance=self.werehouse_entrance).delete()
    #    super(WProductMeasurement, self).delete(*args, **kwargs)
       
    def __str__(self):
        return self.product_description

    def __unicode__(self):
        return self.product_description

    def get_absolute_url(self):
        return reverse('warehouse-entrances-list')

    def get_total_palet_boxes(self):
        total_palet = self.warehouseentranceconfirmation.warehouseentrancepallet_set.all()
        if len(total_palet) > 0:
            pallet = total_palet.values('boxes').aggregate(total_boxes=Coalesce(Sum('boxes'), 0))
            return int(pallet['total_boxes'])
        else:
            return 0

    def get_total_palet_gross_weight(self):
        total_palet = self.warehouseentranceconfirmation.warehouseentrancepallet_set.all()
        if len(total_palet) > 0:
            pallet = total_palet.values('gross_weight').aggregate(total_gross_weight=Coalesce(Sum('gross_weight'), 0))
            return pallet['total_gross_weight']
        else:
            return 0

class WProductVehicleInspection(models.Model):
    vehicle_temograph = models.IntegerField(verbose_name=_('Vehicle has Termograph'),default=0)
    temprature_cel = models.IntegerField(verbose_name=_('Temperature celcious'),default=0)
    cont_flr_sta = models.IntegerField(verbose_name=_('Container Floor Status'),default=0)
    fasteners = models.IntegerField(verbose_name=_('Fasteners'),default=0)
    container_clean = models.IntegerField(verbose_name=_('Container Clean'),default=0)
    inside_container_good = models.IntegerField(verbose_name=_('Inside The Container is in Good Condition'),default=0)
    loading_availity = models.BooleanField(verbose_name=_('ContainVehicle able for loading/unloading'),default=0)
    notes = models.CharField(verbose_name=_('Notes'), max_length=255, blank=True)
    werehouse_entrance = models.ForeignKey(WarehouseEntrance, null=False,verbose_name=_('Entrance'))
    

    def __str__(self):
        return self.notes

    def __unicode__(self):
        return self.notes

    def get_absolute_url(self):
        return reverse('warehouse-entrances-list')


class WIncidenceProduct(models.Model):
    code = models.CharField(verbose_name=_('Code'), null=True, blank=True,max_length=255)
    product = models.ForeignKey(Product, null=False,verbose_name=_('Product'))
    incidence = models.FloatField(verbose_name=_('Kg Per Price'), null=True, blank=True,default=0)
    notes = models.CharField(verbose_name=_('Notes'), max_length=255, blank=True)
    werehouse_entrance = models.ForeignKey(WarehouseEntrance, null=False,verbose_name=_('Entrance'))
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
    
    
    def __str__(self):
        return self.notes

    def __unicode__(self):
        return self.notes

    def get_absolute_url(self):
        return reverse('warehouse-entrances-list')


class WIncidenceImage(models.Model):
   
    image = models.FileField(verbose_name=_('image'), blank=True)
    werehouse_entrance = models.ForeignKey(WarehouseEntrance, null=False,verbose_name=_('Entrance'))
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
    

    def get_absolute_url(self):
        return reverse('warehouse-entrances-list')

class WarehouseEntranceConfirmation(models.Model):
    w_product_measurement = models.OneToOneField(WProductMeasurement, null=True, blank=True, on_delete=models.CASCADE)
    # warehouse = models.ForeignKey(Warehouse, null=False,verbose_name=_('Warehouse'))
    # location = models.CharField(verbose_name=_('Location'), max_length=255, blank=True)
    code = models.CharField(verbose_name=_('Code'), max_length=255, blank=True)
    product = models.ForeignKey(Product, null=False,verbose_name=_('Product'))
    cost_lot = models.CharField(verbose_name=_('Cust Lot'), max_length=255, blank=False,default="")
    # palet_lot = models.CharField(verbose_name=_('Palet Lot'), max_length=255, blank=True)
    exp_date = models.CharField(verbose_name=_('Expiration Date'), max_length=255, blank=True)
    gross_weight = models.DecimalField(verbose_name=_('Gross Weight'), decimal_places=3, max_digits=20, blank=False,default=0)
    net_weight = models.DecimalField(verbose_name=_('Net Weight'), decimal_places=3, max_digits=20, blank=False,default=0)
    invoice_weight = models.DecimalField(verbose_name=_('Entrance Invoice Weight'), decimal_places=3, max_digits=20, blank=True,null=True,default=0)
    retained_quantity = models.IntegerField(verbose_name=_('Retained Qty'), blank=True,null=True,default=0)
    retained_reason = models.CharField(verbose_name=_('Retainment Reason'), max_length=255, blank=True,null=True)
    werehouse_entrance = models.ForeignKey(WarehouseEntrance, null=False,verbose_name=_('Warehouse Entrance'))
    # rack_number = models.CharField(verbose_name=_('Rack Number'), max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
    
    
    def __str__(self):
        return str(self.id) + "--#--"+str(self.updated_at.strftime('%Y-%m-%d, %H:%M %p'))

    def __unicode__(self):
        return str(self.id) + "--#--"+str(self.updated_at.strftime('%Y-%m-%d, %H:%M %p'))

    def get_absolute_url(self):
        return reverse('warehouse-entrances-list')

    def get_total_palet(self):
        total_palet = self.warehouseentrancepallet_set.all()
        if len(total_palet) > 0:
            return True
        else:
            return False



    @property
    def get_total_quantity(self):
        result = self.werehouse_entrance.wproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().boxes
        else:
            return 0

    @property
    def get_total_weight(self):
        result = self.werehouse_entrance.wproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().total_kg
        else:
            return 0
    @property
    def kg_per_boxes(self):
        result = self.werehouse_entrance.wproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().kg_per_boxes
        else:
            return 0
def increment_pallet_palet_lot():
    last_pallet = WarehouseEntrancePallet.objects.all().order_by('id').last()
    if not last_pallet:
        return 'FS0'
    pallet_palet_lot = last_pallet.palet_lot
 
    pallet_palet_lot = 'FS' + str(int(pallet_palet_lot.split('FS')[1]) + 1)
    return pallet_palet_lot

class WarehouseEntrancePallet(models.Model):
    
    warehouse = models.ForeignKey(Warehouse, null=True,verbose_name=_('Warehouse'))
    location =  models.ForeignKey(WarehouseLocation, null=True,verbose_name=_('Location'))
    palet_lot = models.CharField(verbose_name=_('Palet Lot'), max_length=255, blank=True,default=increment_pallet_palet_lot)
    rack_number = models.ForeignKey(WarehouseSection,verbose_name=_('Rack Number'), null=True, blank=True)
    boxes = models.IntegerField(verbose_name=_('Boxes'), null=True, blank=True,default=0)
    werehouse_entrance_confirmation = models.ForeignKey(WarehouseEntranceConfirmation, null=False,verbose_name=_('Warehouse Entrance'))
    
    #-------new Fields----------
    cost_lot = models.CharField(verbose_name=_('Cust Lot'), max_length=255, blank=False,default="")
    exp_date = models.CharField(verbose_name=_('Expiration Date'), max_length=255, blank=True)
    gross_weight = models.DecimalField(verbose_name=_('Gross Weight'), decimal_places=3, max_digits=20, blank=False,default=0.0)
    net_weight = models.DecimalField(verbose_name=_('Net Weight'), decimal_places=3, max_digits=20, blank=False,default=0.0)
    invoice_weight = models.DecimalField(verbose_name=_('Entrance Invoice Weight'), decimal_places=3, max_digits=20, blank=False,null=False, default=0)
    retained_quantity = models.IntegerField(verbose_name=_('Retained Qty'), blank=False,null=False,default=0)
    retained_reason = models.CharField(verbose_name=_('Retainment Reason'), max_length=255, blank=True,null=True)
    box_kg = models.FloatField(verbose_name=_('Box Kg'), null=True, blank=True,default=0)
    confirmed = models.BooleanField(verbose_name=_('Pallet Confirmed'),default=False)
    note = models.TextField(verbose_name=_('Note'),null=True, blank=True )
    maniobras = models.BooleanField(verbose_name=_('Maniobras'),default=False)
    maniobras_completed_at = models.DateTimeField(verbose_name=_('Maniobras Completed At'),auto_now_add=False, null=True, blank=True)
    sent_to_maniobras_at = models.DateTimeField(verbose_name=_('Sent To Maniobras'),auto_now_add=False, null=True, blank=True)
    maniobras_completed_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Sent To Maniobras by'))
    
    #-------------------------
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)    
   

    def __str__(self):
        return str(self.id) + "--#--"+str(self.updated_at.strftime('%Y-%m-%d, %H:%M %p'))

    def __unicode__(self):
        return str(self.id) + "--#--"+str(self.updated_at.strftime('%Y-%m-%d, %H:%M %p'))

    def get_absolute_url(self):
        return reverse('warehouse-entrances-list')

    @property
    def get_pallet_available_net_weight(self):
        if self.warehouseinventory_set.exists():
            return self.warehouseinventory_set.values('available_net_weight').aggregate(total_price=Sum('available_net_weight'))['total_price']
        return 0

    @property
    def get_pallet_location_height(self):
        try:
            return self.location.warehousedepthlevel_set.first().height.description
        except:
            return ''

    @property
    def get_pallet_available_gross_weight(self):
        if self.warehouseinventory_set.exists():
            return self.warehouseinventory_set.values('available_gross_weight').aggregate(total_price=Sum('available_gross_weight'))['total_price']
        return 0

    @property
    def get_pallet_inventory_available_total_boxes(self):
        if self.warehouseinventory_set.exists():
            return self.warehouseinventory_set.values('available_total_boxes').aggregate(total_boxes=Sum('available_total_boxes'))['total_boxes']
        return 0

    @property
    def get_pallet_inventory_total_boxes(self):
        if self.warehouseinventory_set.exists():
            return self.warehouseinventory_set.values('total_boxes').aggregate(total_boxes=Sum('total_boxes'))['total_boxes']
        return 0

    @property
    def get_pallet_inventory_total_kg(self):
        if self.warehouseinventory_set.exists():
            return self.warehouseinventory_set.values('total_kg').aggregate(total_kg=Sum('total_kg'))['total_kg']
        return 0
    
    @property
    def get_pallet_retained_boxes(self):
        if self.warehouseinventory_set.exists():
            return self.warehouseinventory_set.values('retained_boxes').aggregate(retained_boxes=Sum('retained_boxes'))['retained_boxes']
        return 0

    @property
    def get_pallet_detail_for_qr(self):
        Folio=  self.werehouse_entrance_confirmation.werehouse_entrance.id
        LOTECte= (self.cost_lot).replace(' ', '_')
        LOTETar= (self.palet_lot).replace(' ', '_')
        CLIENTE= (self.werehouse_entrance_confirmation.werehouse_entrance.customer.name).replace(' ', '_')
        KGTotal= self.box_kg
        CJTotal= self.boxes
        FCad=    (self.exp_date).replace(' ', '_')
        palet_id= self.id
        client_id= self.werehouse_entrance_confirmation.werehouse_entrance.customer_id
        product_id= self.werehouse_entrance_confirmation.product_id
        confirmation= self.werehouse_entrance_confirmation.id 
               
        data = '%22Folio%22:%22{0}%22,%22Lotecte%22:%22{1}%22,%22LOTETar%22:%22{2}%22,%22CLIENTE%22:%22{3}%22,%22KGTotal%22:%22{4}%22,%22CJTotal%22:%22{5}%22,%22FCad%22:%22{6}%22,%22palet_id%22:%22{7}%22,%22confirmation%22:%22{8}%22,%22client_id%22:%22{9}%22,%22product_id%22:%22{10}%22'.format(Folio,LOTECte,LOTETar, CLIENTE, KGTotal, CJTotal, FCad, palet_id, confirmation,client_id,product_id)
        return "{%s}"%data

    @property
    def get_pallet_information(self):
        return_value = {
            "Folio": self.werehouse_entrance_confirmation.werehouse_entrance.id,
            "LOTECte": self.cost_lot,
            "LOTETar": self.palet_lot,            
            "CLIENTE": self.werehouse_entrance_confirmation.werehouse_entrance.customer.name,
            "KGTotal": self.box_kg,
            "CJTotal": self.boxes,
            "FCad": self.exp_date,
            "palet_id": self.id,
            "confirmation": self.werehouse_entrance_confirmation.id
            

        }
        return str(return_value)

    @property
    def get_warehouse_information(self):
        if self.warehouse != None:
            warehouse_id = self.warehouse.id
            warehouse_code = self.warehouse.code
        else:
            warehouse_id = ""
            warehouse_code = ""
        if self.rack_number != None:
            rack_id =  self.rack_number.id
            rack_number  = self.rack_number.index
        else:
            rack_id =  ""
            rack_number  = ""
        if self.location != None:
            location_id =  self.location.id
            location_number  = self.location.location_number
        else:
            location_id =  ""
            location_number  = ""
        return_value = {
            str("warehouse_id"): warehouse_id,
            "warehouse_name": warehouse_code,
            "rack_id": rack_id,
            "rack_number": rack_number,
            "location_id": location_id,
            "location_number": location_number 
        }
        return str(return_value)
    @property
    def is_pallet_peso_variable_exists(self):
        pallet_peso_variable = EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet_id=self.id)
        total_pallet_peso_variable = sum(pallet_peso_variable.values_list('peso_variable_quantity',flat=True))

        if float(total_pallet_peso_variable) > 0:
            return True
        else:
            return False
    @property
    def pallet_peso_variable_with_zero_value(self):
        pallet_peso_variable = EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet_id=self.id, peso_variable_quantity=0)
        if pallet_peso_variable.exists():
            return True
        else:
            return False
    
class EntrancePalletPesoVariable(models.Model):

    peso_variable_quantity = models.FloatField(verbose_name=_('Peso Variable Quantity'), null=True, blank=True,default=0)
    werehouse_entrance_pallet = models.ForeignKey(WarehouseEntrancePallet, null=False,verbose_name=_('Warehouse Entrance Pallet'))
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)    
   

    def __str__(self):
        return "entrance_id--- " + str(self.werehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance_id ) + " pallet---- " + str(self.peso_variable_quantity)

    def __unicode__(self):
        return str(self.peso_variable_quantity)

class PalletConsolidate(models.Model):

    source_pallet = models.CharField(verbose_name=_('Source Pallet'), null=True, blank=True,max_length=255)
    destination_pallet = models.CharField(verbose_name=_('Destination Pallet'), null=True, blank=True,max_length=255)
    source_inventory = models.ForeignKey(WarehouseInventory, null=True,verbose_name=_('Source Inventory'), related_name='source_inventory')
    destination_inventory = models.ForeignKey(WarehouseInventory, null=True,verbose_name=_('Destination Inventory'), related_name='destination_inventory')
    source_boxes = models.CharField(verbose_name=_('Source Pallet'), null=True, blank=True,max_length=255)
    source_weight = models.CharField(verbose_name=_('Source Pallet'), null=True, blank=True,max_length=255)
    destination_boxes = models.CharField(verbose_name=_('Source Pallet'), null=True, blank=True,max_length=255)
    destination_weight = models.CharField(verbose_name=_('Source Pallet'), null=True, blank=True,max_length=255)
    reason = models.CharField(verbose_name=_('Source Pallet'), null=True, blank=True,max_length=255)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)


    def __str__(self):
        return self.reason

        def __unicode__(self):
            return self.reason


def update_entrance_total_kg(sender,instance,**kwargs):
    w_entrance_id = instance.werehouse_entrance_id
    
    replace_values= WProductMeasurement.objects.filter(werehouse_entrance_id=w_entrance_id).aggregate(Sum('total_kg'),Sum('kg_per_boxes')).values()
    WarehouseEntrance.objects.filter(pk=w_entrance_id).update(kg_per_boxes=replace_values[0],total_kg=replace_values[1])

post_save.connect(update_entrance_total_kg, sender=WProductMeasurement)

@receiver(pre_save,sender=WarehouseEntrancePallet)
def update_plate(sender,**kwargs):
    obj = kwargs['instance']
    try:
        obj.gross_weight = float("{0:.3f}".format(float(obj.gross_weight)))
        obj.net_weight = float("{0:.3f}".format(float(obj.net_weight)))
        datetime.datetime.strptime(obj.exp_date, '%Y-%m-%d')
    except:
        obj.gross_weight = float("{0:.3f}".format(float(obj.gross_weight)))
        obj.net_weight = float("{0:.3f}".format(float(obj.net_weight)))
        obj.exp_date= datetime.datetime.today().strftime('%Y-%m-%d')
    if not obj.id:
        obj.gross_weight = float("{0:.3f}".format(float(obj.gross_weight)))
        obj.net_weight = float("{0:.3f}".format(float(obj.net_weight)))
        obj.palet_lot = increment_pallet_palet_lot()

  
def create_entrance_production_confirmation(sender, instance, **kwargs):
    if not hasattr(instance,'warehouseentranceconfirmation'):
        WarehouseEntranceConfirmation.objects.create(product = instance.product, code=instance.product.product_code, exp_date = instance.werehouse_entrance.entrance_date, werehouse_entrance_id = int(instance.werehouse_entrance.id), w_product_measurement=instance)
post_save.connect(create_entrance_production_confirmation, sender=WProductMeasurement)

@receiver(post_save,sender=WarehouseEntrance)
def update_inventory_details(sender,**kwargs):
    entrance = kwargs['instance']
    from ..reserve_inventory.models import ReserveInventory
    if entrance.status == WarehouseEntrance.FINISH:

        message = "Retenido por Entrada Folio :%s"%entrance.id
        confirmations = entrance.warehouseentranceconfirmation_set.all()
        for confirmation in confirmations:
            product =  confirmation.product
            for instance in confirmation.warehouseentrancepallet_set.all():
                inventories = instance.warehouseinventory_set.filter(client=entrance.customer)
                try:
                    datetime.datetime.strptime(instance.exp_date, '%Y-%m-%d')
                except:
                    instance.exp_date= entrance.entrance_date
                    instance.save()

                createInventoryOnFinishEntrance(instance, confirmation,entrance, inventories)          
                # Create Retained Boxes
                if instance.retained_quantity >0 and inventories.exists():
                    inventory = inventories.first()
                    reserves = ReserveInventory.objects.filter(inventory=inventory,palet_lot=instance.palet_lot)
                    if not reserves.exists():
                        reserved = ReserveInventory(inventory=inventory,palet_lot=instance.palet_lot,motive_to_reserve=ReserveInventory.OTRO)
                        reserved.boxes = instance.boxes
                        reserved.reserve_boxes = instance.retained_quantity
                        reserved.released_store_box = instance.retained_quantity
                        reserved.notes = message
                        reserved.save()


def createInventoryOnFinishEntrance(pallet,confirmation,entrance, inventories):
    warehouse_location = pallet.location
    boxes = int(round(pallet.boxes))
    gross_weight = pallet.gross_weight
    available_total_boxes = boxes-pallet.retained_quantity
    if inventories.exists():
        inventories.update(
            total_kg=  gross_weight,
            total_boxes= boxes,
            rack = pallet.rack_number.index,
            exp_date=pallet.exp_date,
            retained_boxes=pallet.retained_quantity,
            available_gross_weight=pallet.gross_weight,
            available_net_weight=pallet.net_weight,
            available_total_boxes=available_total_boxes)
    else:        
        if warehouse_location != None:
            WarehouseInventory.objects.create(
                warehouse_location=warehouse_location,
                product=confirmation.product,
                client=entrance.customer,
                total_kg= gross_weight,
                total_boxes=boxes,
                exp_date=pallet.exp_date,
                rack=pallet.rack_number.index,
                warehouse_entrance_pallet=pallet,
                retained_boxes=pallet.retained_quantity,
                available_gross_weight=pallet.gross_weight,
                available_net_weight=pallet.net_weight,
                is_locked = False,
                available_total_boxes=available_total_boxes)
    if warehouse_location != None:
        warehouse_location.total_stored_kg = sum(warehouse_location.warehouseinventory_set.all().values_list('available_gross_weight',flat=True))
        warehouse_location.total_stored_boxes = sum(warehouse_location.warehouseinventory_set.all().values_list('total_boxes', flat=True))
        warehouse_location.total_retained_boxes = sum(warehouse_location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
        warehouse_location.available_weight = (warehouse_location.available_weight - (confirmation.product.get_available_weight * boxes))
        warehouse_location.available_volume = (warehouse_location.available_volume - (confirmation.product.get_available_volume * boxes))
        if warehouse_location.available_weight < 0:
            warehouse_location.available_weight = 0
        if warehouse_location.available_volume < 0:
            warehouse_location.available_volume = 0
        warehouse_location.save()




def clear_cache_entrance_pallet(sender, instance, created, **kwargs):
    from django.core.cache import cache
    from sga.celery import updateCache
    cache.clear()
    if sender == WarehouseEntrancePallet:
        
        entrance_id = instance.werehouse_entrance_confirmation.werehouse_entrance.id
    elif sender == WarehouseEntrance:
        entrance_id = instance.id
    elif sender == WarehouseEntranceConfirmation:
        entrance_id = instance.werehouse_entrance.id
    updateCache.delay(reverse_lazy('confirm-entrance-pallets',kwargs={"pk":entrance_id}))
    updateCache.delay(reverse_lazy('update-entrance',kwargs={"pk":entrance_id}))


post_save.connect(clear_cache_entrance_pallet, sender=WarehouseEntrancePallet)
post_save.connect(clear_cache_entrance_pallet, sender=WarehouseEntrance)
post_save.connect(clear_cache_entrance_pallet, sender=WarehouseEntranceConfirmation)

from django.dispatch import receiver


@receiver(pre_save, sender=WarehouseEntrance)
def on_change(sender, instance, **kwargs):
    if not instance.id is None:
        previous = WarehouseEntrance.objects.get(id=instance.id)
        if previous.entrance_hour != instance.entrance_hour:
            from sga.celery import delete_bays
            delete_bays.delay('entrance', instance.id)


"""
If user make any changes in pallet enven after confirming warehouse entrance
"""
def auto_retain_boxes(sender, instance, **Kwargs):
    entrance = instance.werehouse_entrance_confirmation.werehouse_entrance
    if instance.retained_quantity >0 and entrance.status == WarehouseEntrance.FINISH:
        if instance.warehouseinventory_set.exists():
            inventory = instance.warehouseinventory_set.first()
            from ..reserve_inventory.models import ReserveInventory

            reserved = ReserveInventory(inventory=inventory,palet_lot=instance.palet_lot,motive_to_reserve=ReserveInventory.OTRO)
            reserved.boxes = instance.boxes
            reserved.reserve_boxes = instance.retained_quantity
            reserved.notes = "Retenido por Entrada Folio :%s"%entrance.id
            reserved.save()


post_save.connect(auto_retain_boxes, sender=WarehouseEntrancePallet)
