from __future__ import unicode_literals
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.clients.models import Client
from catalogs.product.models import Product
from catalogs.warehouse.models import Warehouse,WarehouseInventory
from catalogs.consignee.models import Consignee
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from decimal import Decimal
from django.db.models.functions import Cast, Coalesce
from django.contrib.postgres.fields import ArrayField,JSONField
from catalogs.general_params.models import GeneralParams
from django.db.models import Sum, Count
from catalogs.warehouse.models import Warehouse,WarehouseDepthLevel, WarehouseInventory,WarehouseLocation,WarehouseSection
from users.models import UserProfile
from warehouses.warehouse_entrance.models import WarehouseEntrance
from catalogs.notifications.models import Notification
from django.contrib.contenttypes.fields import GenericRelation
from catalogs.warehouse.models import WarehouseTruckBays
from django.utils import timezone
from django.urls import reverse_lazy
from catalogs.utilities import WarehouseLocationPrams
from django.utils.functional import cached_property

class WarehouseExit(models.Model):
    PENDING = 'control'
    FINISH = 'finish'
    IN_MANEUVERS = "InManeuvers"
    MANEUVER_COMPLETE = "ManeuverComplete"

    STATUS = (
        (PENDING, _('Control')), 
        (IN_MANEUVERS, _('In Maneuvers')),
        (MANEUVER_COMPLETE,_("Maneuver Complete")),
        (FINISH, _('Finish')))

    exit_date = models.DateField(verbose_name=_('Exit Date'))
    exit_hour = models.TimeField(verbose_name=_('Exit Hour'),blank=True)
    carrier = models.ForeignKey(Carrier, null=True,verbose_name=_('Carrier'))
    vehicle = models.ForeignKey(Vehicle, null=True,verbose_name=_('Vehicle'))
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
    exit_match_invoice = models.BooleanField(default= False)
    status = models.CharField(verbose_name=_('Warehouse Exit Status'), max_length=20, default=PENDING, null=False, blank=False, choices=STATUS)

    cargo_sender = models.CharField(verbose_name=_('Cargo Sender'), max_length=50, blank=True, default="")
    # new driver info
    driver_name = models.CharField(verbose_name=_('Name Of The Driver'), max_length=100, blank=True, default="")
    temp_front = models.FloatField(verbose_name=_('Temprature Front'), default=0)
    temp_middle = models.FloatField(verbose_name=_('Temprature Middel'), default=0)
    temp_back = models.FloatField(verbose_name=_('Temprature Back'), default=0)

    cust_reference = models.CharField(verbose_name=_('Referencia'), max_length=255, blank=True, default="")
    seal1 = models.CharField(verbose_name=_('Fleje/Sello 1'), max_length=255, blank=True, default="")
    seal2 = models.CharField(verbose_name=_('Fleje/Sello 2'), max_length=255, blank=True, default="")
    consignee = models.ForeignKey(Consignee, null=False,verbose_name=_('Consignatario'))
    created_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Created By'))
    print_picking = models.BooleanField(verbose_name=_('Print picking report generated'), default=False)
    notifications = GenericRelation(Notification)
    bays = GenericRelation(WarehouseTruckBays)
    sent_to_maniobras_at = models.DateTimeField(verbose_name=_('Sent to Maniobras At'),auto_now_add=False, null=True, blank=True)
    confirmed_at = models.DateTimeField(verbose_name=_('Confirmed At'),auto_now_add=False, null=True, blank=True)

    sent_to_maniobras_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Sent To Maniobras by'), related_name='exit_maniobras_by')
    confirmed_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Confirmed by'), related_name='exit_confirmed_by')


    def __str__(self):
        return str(self.id)+"---#-"+str(self.exit_date)

    def __unicode__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse('warehouse-exit-list')

    
    @cached_property
    def get_picking_value(self):
        from catalogs.general_params.models import GeneralParams
        gp = GeneralParams.objects.filter(key='AutomaticPicking')
        if len(gp)>0 and int(gp.first().value) == 1:
            return True
        else:
            return False

    @property
    def get_total_gross_weight(self):
        result = self.wexitconfirmation_set.values('gross_weight').aggregate(total_gross_weight=Coalesce(Sum('gross_weight'), 0))
        return result.get('total_gross_weight')

    @property
    def get_total_pallet_gross_weight(self):
        exit_confim_ids = self.wexitconfirmation_set.all().values_list('id',flat=True)
        result = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=exit_confim_ids).values('gross_weight').aggregate(total_gross_weight=Coalesce(Sum('gross_weight'), 0) )
        return result.get('total_gross_weight')

    @property
    def get_total_net_weight(self):
        result = self.wexitconfirmation_set.values('net_weight').aggregate(total_net_weight=Coalesce(Sum('net_weight'), 0) )
        return result.get('total_net_weight')

    @property
    def get_total_pallet_net_weight(self):
        exit_confim_ids = self.wexitconfirmation_set.all().values_list('id',flat=True)
        result = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=exit_confim_ids).values('net_weight').aggregate(total_net_weight=Coalesce(Sum('net_weight'), 0))
        return result.get('total_net_weight')

    @property
    def get_total_boxes(self):
        result = sum([float(confirm.get_total_quantity) for confirm in self.wexitconfirmation_set.all()])
        return result

    @property
    def get_total_pallet_boxes(self):
        exit_confim_ids = self.wexitconfirmation_set.all().values_list('id',flat=True)
        result = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=exit_confim_ids).values('boxes').aggregate(total_boxes=Coalesce(Sum('boxes'), 0))
        return result.get('total_boxes')

    @property
    def get_total_kgs(self):
        result = sum([float(confirm.get_total_kgs or 0) for confirm in self.wexitconfirmation_set.all()])
        return result

    @property
    def get_pallet_total_kgs(self):
        exit_confim_ids = self.wexitconfirmation_set.all().values_list('id',flat=True)
        result = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=exit_confim_ids).values('box_kg').aggregate(total_box_kg=Coalesce(Sum('box_kg'), 0) )
        return result.get('total_box_kg')

    @property
    def list_product(self):
        return self.wexitproductmeasurement_set.all().order_by('id')

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
        return reverse_lazy('confirm-exit-pallets', args=[self.id])

    @property
    def absolute_maneobras_url(self):
        return reverse_lazy('maniobras-exit-update', args=[self.id])


    @property
    def get_total_pallet_boxes(self):
        result = sum([float(confirm.boxes) for confirm in WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=self.wexitconfirmation_set.all().values_list('id',flat=True))])
        return int(result)

    @property
    def get_total_pallet_boxes_kgs(self):
        result = sum([float(confirm.box_kg) for confirm in WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=self.wexitconfirmation_set.all().values_list('id',flat=True))])
        return result

    @property
    def get_exit_total_kg(self):
        if self.total_kg == None:
            measurements = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.id)
            result = measurements.values('total_kg').aggregate(total_kg=Coalesce(Sum('total_kg'), 0))
            return result.get('total_kg')
        else:
            return self.total_kg

    @property
    def get_exit_total_boxes(self):
        if self.boxes == None:
            measurements = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.id)
            result = measurements.values('boxes').aggregate(boxes=Coalesce(Sum('boxes'), 0))
            return result.get('boxes')
        else:
            return self.boxes    

    @property
    def get_measurement_total_boxes(self):
        measurements = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.id)
        result = measurements.values('boxes').aggregate(boxes=Coalesce(Sum('boxes'), 0))
        return result.get('boxes')

    def get_licence_place(self):
        if self.license_plate == 'None' or self.license_plate == None:
            return ""            
        else:
            return self.license_plate
        

    

class WExitProductMeasurement(models.Model):
    total_kg = models.FloatField(verbose_name=_('Total Kg'), null=True, blank=True,default=0)
    price = models.FloatField(verbose_name=_('Total Price'), null=True, blank=True,default=0)
    kg_per_price = models.FloatField(verbose_name=_('Kg Per Price'), null=True, blank=True,default=0)
    boxes = models.IntegerField(verbose_name=_('Boxes'), null=True, blank=True,default=0)
    kg_per_boxes = models.FloatField(verbose_name=_('Kg Per Box'), null=True, blank=True,default=0)
    werehouse_exit = models.ForeignKey(WarehouseExit, null=False,verbose_name=_('Exit'))
    product = models.ForeignKey(Product, null=False,verbose_name=_('Product'))
    product_description = models.CharField(verbose_name=_('Description'), max_length=60)
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
    palet_lot = models.CharField(verbose_name=_('Palet Lot'), max_length=255, blank=True, null=True, default="")
    cost_lot = models.CharField(verbose_name=_('Cust Lot'), max_length=255, blank=True, null=True, default="")
    exp_date = models.CharField(verbose_name=_('Expiration Date'), max_length=255, blank=True, null=True, default="")
    werehouse_entrance_id = models.IntegerField( blank=True, null=True, verbose_name=_('Warehouse Entrance'))

    # def delete(self, *args, **kwargs):
    #    WExitConfirmation.objects.filter(product=self.product, werehouse_exit=self.werehouse_exit).delete()

    #    super(WExitProductMeasurement, self).delete(*args, **kwargs)
       
    def __str__(self):
        return self.product_description

    def __unicode__(self):
        return self.product_description

    def get_absolute_url(self):
        return reverse('warehouse-exit-list')

    def get_total_palet_boxes(self):
        total_palet = self.wexitconfirmation.warehouseexitpallet_set.all()
        if len(total_palet) > 0:
            pallet = total_palet.values('boxes').aggregate(total_boxes=Coalesce(Sum('boxes'), 0))
            return int(pallet['total_boxes'])
        else:
            return 0

    def get_total_palet_gross_weight(self):
        total_palet = self.wexitconfirmation.warehouseexitpallet_set.all()
        if len(total_palet) > 0:
            pallet = total_palet.values('gross_weight').aggregate(total_gross_weight=Coalesce(Sum('gross_weight'), 0))
            return pallet['total_gross_weight']
        else:
            return 0
class WExitProductVehicleInspection(models.Model):
    vehicle_temograph = models.IntegerField(verbose_name=_('Vehicle has Termograph'),default=0)
    temprature_cel = models.IntegerField(verbose_name=_('Temperature celcious'),default=0)
    cont_flr_sta = models.IntegerField(verbose_name=_('Container Floor Status'),default=0)
    fasteners = models.IntegerField(verbose_name=_('Fasteners'),default=0)
    container_clean = models.IntegerField(verbose_name=_('Container Clean'),default=0)
    inside_container_good = models.IntegerField(verbose_name=_('Inside The Container is in Good Condition'),default=0)
    loading_availity = models.BooleanField(verbose_name=_('ContainVehicle able for loading/unloading'),default=0)
    notes = models.CharField(verbose_name=_('Notes'), max_length=255, blank=True)
    werehouse_exit = models.ForeignKey(WarehouseExit, null=False,verbose_name=_('Warehouse Exit'))
    def __str__(self):
        return self.notes

    def __unicode__(self):
        return self.notes

    def get_absolute_url(self):
        return reverse('warehouse-exit-list')


class WExitConfirmation(models.Model):
    exit_product_measurement = models.OneToOneField(WExitProductMeasurement, null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, null=False,verbose_name=_('Product'))
    cost_lot = models.CharField(verbose_name=_('Cust Lot'), max_length=255, blank=False,default= 0)
    exp_date = models.CharField(verbose_name=_('Expiration Date'), max_length=255, blank=True)
    gross_weight = models.DecimalField(verbose_name=_('Gross Weight'), decimal_places=3, max_digits=20, blank=False,default= 0)
    net_weight = models.DecimalField(verbose_name=_('Net Weight'), decimal_places=3, max_digits=20, blank=False,default= 0)
    invoice_weight = models.DecimalField(verbose_name=_('Invoice Weight'), decimal_places=3, max_digits=20, blank=True,null=True,default= 0)
    retained_quantity = models.IntegerField(verbose_name=_('Retained Qty'), blank=True,null=True,default= 0)
    retained_reason = models.CharField(verbose_name=_('Retainment Reason'), max_length=255, blank=True,null=True,default= "")
    werehouse_exit = models.ForeignKey(WarehouseExit, null=False,verbose_name=_('Warehouse Exit'))
    removed_boxes = ArrayField(models.CharField( max_length=15), verbose_name=_('Auto Pick Removed Boxes'), null=True, blank=True)
    removed_kgs = ArrayField(models.CharField( max_length=15), verbose_name=_('Auto Pick Removed Kg'), null=True, blank=True)
    auto_pick_data = JSONField(verbose_name=_('Auto Pick json'),default={},null=True,blank=True)

    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
    
    def __str__(self):
        return self.product.product_code

    def __unicode__(self):
        return self.product.product_code

    def get_absolute_url(self):
        return reverse('warehouse-exit-list')

    @cached_property
    def get_total_quantity(self):
        result = self.werehouse_exit.wexitproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().boxes
        else:
            return 0

    @cached_property
    def get_total_kgs(self):
        result = self.werehouse_exit.wexitproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().total_kg
        else:
            return 0

    @cached_property
    def get_total_weight(self):
        result = self.werehouse_exit.wexitproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().total_kg
        else:
            return 0

    @cached_property
    def kg_per_boxes(self):
        result = self.werehouse_exit.wexitproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().kg_per_boxes
        else:
            return 0

    @cached_property
    def get_total_boxes(self):
        result = self.werehouse_exit.wexitproductmeasurement_set.filter(product=self.product)
        if result.exists():
            return result.first().boxes
        else:
            return 0




class WarehouseExitPallet(models.Model):

   warehouse = models.ForeignKey(Warehouse,null=False, blank=False,verbose_name=_('Warehouse'))
   location =  models.ForeignKey(WarehouseLocation, null=False, blank=False,verbose_name=_('Location'))
   palet_lot = models.CharField(verbose_name=_('Palet Lot'), max_length=255, blank=True)
   rack_number = models.ForeignKey(WarehouseSection,verbose_name=_('Rack Number'), null=False, blank=False)
   boxes = models.IntegerField(verbose_name=_('Boxes'), null=True, blank=True,default=0)
   werehouse_exit_confirmation = models.ForeignKey(WExitConfirmation, null=False,verbose_name=_('Warehouse Entrance'))
   cost_lot = models.CharField(verbose_name=_('Cust Lot'), max_length=255, blank=False,default="")
   exp_date = models.CharField(verbose_name=_('Expiration Date'), max_length=255, blank=True)
   gross_weight = models.DecimalField(verbose_name=_('Gross Weight'), decimal_places=3, max_digits=20, blank=False,default=0.0)
   net_weight = models.DecimalField(verbose_name=_('Net Weight'), decimal_places=3, max_digits=20, blank=False,default=0.0)
   invoice_weight = models.DecimalField(verbose_name=_('Entrance Invoice Weight'), decimal_places=3, max_digits=20, blank=False,null=False, default=0)
   retained_quantity = models.IntegerField(verbose_name=_('Retained Qty'), blank=False,null=False,default=0)
   retained_reason = models.CharField(verbose_name=_('Retainment Reason'), max_length=255, blank=True,null=True)
   inventory = models.ForeignKey(WarehouseInventory, null=True,verbose_name=_('Inventario de almacen'))
   box_kg = models.FloatField(verbose_name=_('Box Kg'), null=True, blank=True,default=0)
   confirmed = models.BooleanField(verbose_name=_('Pallet Confirmed'),default=False)

   created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
   updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)
   maniobras_completed_at = models.DateTimeField(verbose_name=_('Maniobras Completed At'),auto_now_add=False, null=True, blank=True)
   maniobras_completed_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Sent To Maniobras by'))
   


   def __str__(self):
       return str(self.palet_lot) + "--#--"+str(self.updated_at.strftime('%Y-%m-%d, %H:%M %p'))

   def __unicode__(self):
       return str(self.id) + "--#--"+str(self.updated_at.strftime('%Y-%m-%d, %H:%M %p'))

   
   def get_absolute_url(self):
       return reverse('warehouse-exit-list')

   @property
   def get_exit_pallet_location_height(self):
        try:
            depths = self.location.warehousedepthlevel_set.all()
            return self.rack_number.heights.filter(warehousedepthlevel__in=depths).first().description
        except:
            return ''

   @property
   def get_exit_pallet_information(self):
    return_value = {
    "Folio": self.werehouse_exit_confirmation.werehouse_exit.id,
    "LOTECte": self.cost_lot,
    "LOTETar": self.palet_lot,            
    "CLIENTE": self.werehouse_exit_confirmation.werehouse_exit.customer.name,
    "KGTotal": self.box_kg,
    "CJTotal": self.boxes,
    "FCad": self.exp_date
    }
    return str(return_value)

   @property
   def get_exit_warehouse_information(self):
        return_value = {
        str("warehouse_id"): self.warehouse.id,
        "warehouse_name": self.warehouse.code,
        "rack_id": self.rack_number.id,
        "rack_number": self.rack_number.index,
        "location_id": self.location.id,
        "location_number": self.location.location_number 
        }
        return str(return_value)

   @property
   def get_pallet_available_net_weight(self):
      if self.inventory:
        return self.inventory.available_net_weight
      return 0
   @property
   def get_pallet_available_gross_weight(self):
      if self.inventory:
          return self.inventory.available_gross_weight
      return 0

   @property
   def get_pallet_inventory_available_total_boxes(self):
      if self.inventory:
          return self.inventory.available_total_boxes
      return 0

   @property
   def get_pallet_inventory_total_boxes(self):
    if self.inventory:
        return self.inventory.total_boxes
    return 0

   @property
   def get_pallet_inventory_total_kg(self):
    if self.inventory:
        return self.inventory.total_kg
    return 0
    
   @property
   def get_pallet_retained_boxes(self):
    if self.inventory:
        return self.inventory.retained_boxes
    return 0



def update_exit_total_kg(sender,instance,**kwargs):
    w_exit_id = instance.werehouse_exit_id
    kg_per_boxes= WExitProductMeasurement.objects.filter(werehouse_exit_id=w_exit_id).aggregate(kgs_per_boxes=Coalesce(Sum('kg_per_boxes'),0))
    total_kg= WExitProductMeasurement.objects.filter(werehouse_exit_id=w_exit_id).aggregate(total_kgs=Coalesce(Sum('total_kg'),0))
    WarehouseExit.objects.filter(pk=w_exit_id).update(kg_per_boxes=kg_per_boxes.get('kgs_per_boxes'),total_kg=total_kg.get('total_kg'))



def update_exit_inventory_details(instance):
    if instance.status == 'finish':
        confirmations = instance.wexitconfirmation_set.all()
        for confirmation in confirmations.iterator():
            product =  confirmation.product
            pallets = confirmation.warehouseexitpallet_set.all()
            for pallet in pallets.iterator():
                total_kg = float(pallet.box_kg)*float(pallet.boxes)
                total_boxes = float(pallet.boxes)
                palet_gross_weight = float(pallet.gross_weight)
                palet_net_weight = float(pallet.net_weight)
                palet_retained_quantity = pallet.retained_quantity
                inventory = pallet.inventory
                
                
                available_gross_weight = inventory.available_gross_weight
                available_net_weight = inventory.available_net_weight
                available_gross_weight = available_gross_weight - palet_gross_weight

                available_net_weight = available_net_weight - palet_net_weight

                if available_net_weight < 0:
                    available_net_weight = 0
                if available_gross_weight < 0:
                    available_gross_weight = 0
                    
                new_total_boxes = inventory.total_boxes - total_boxes

                if new_total_boxes <=0:
                    new_total_boxes = 0
                    available_net_weight  = 0.0
                    available_gross_weight  = 0.0
                to_kg = inventory.total_kg - total_kg
                inventory.total_kg =  available_gross_weight#to_kg if to_kg >=0 else 0
                inventory.total_boxes = new_total_boxes
                if inventory.available_total_boxes > new_total_boxes:
                    inventory.available_total_boxes = new_total_boxes
                inventory.rack = pallet.rack_number.index
                inventory.exp_date = pallet.exp_date
                inventory.available_gross_weight = available_gross_weight
                inventory.available_net_weight = available_net_weight
                inventory.is_locked = False
                inventory.save()

                w_stored_weight=0
                w_excluded_weight = 0
                w_stored_volume = 0
                w_excluded_volume = 0
                warehouse_location = pallet.location
                entrance_pallets = warehouse_location.warehouseentrancepallet_set.all()
                exit_pallets =warehouse_location.warehouseexitpallet_set.all()  
                if entrance_pallets.exists():

                    for entrance_pallet in entrance_pallets:
                        
                        if entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.status == 'finish' and entrance_pallet.warehouseinventory_set.first().available_total_boxes!=0:
                            w_stored_weight += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_weight
                            w_stored_volume += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_volume

                if exit_pallets.exists():
                    for exit_pallet in exit_pallets:
                        if exit_pallet.werehouse_exit_confirmation.werehouse_exit.status == 'finish' and exit_pallet.inventory.available_total_boxes!=0:
                            w_excluded_weight += exit_pallet.boxes * exit_pallet.werehouse_exit_confirmation.product.get_available_weight
                            w_excluded_volume += exit_pallet.boxes * exit_pallet.werehouse_exit_confirmation.product.get_available_volume
                
                
                final_weight = w_stored_weight-w_excluded_weight
                final_volume = w_stored_volume-w_excluded_volume
                
                depths = warehouse_location.warehousedepthlevel_set.all()
                # update location boxes details
                total_stored_kg = warehouse_location.total_stored_kg - total_kg
                warehouse_location.total_stored_kg = total_stored_kg if total_stored_kg >=0 else 0
                total_stored_boxes = warehouse_location.total_stored_boxes - total_boxes
                warehouse_location.total_stored_boxes = total_stored_boxes if total_stored_boxes >=0 else 0

                # total_retained_boxes =  warehouse_location.total_retained_boxes - inventory.retained_boxes
                # warehouse_location.total_retained_boxes = total_retained_boxes if total_retained_boxes >=0 else 0

                if depths.exists():
                    for depth in depths.iterator():
                       warehouse_location.available_weight = depth.weight_kg-final_weight
                       warehouse_location.available_volume = depth.location_volume-final_volume
                warehouse_location.save()
                
                

                
                # for location in WarehouseLocation.objects.filter(id=location_numbers.id,warehouse_id=warehouse_numbers):
                #     location.total_stored_kg = sum(location.warehouseinventory_set.all().values_list('available_gross_weight', flat=True))
                #     location.total_stored_boxes = sum(location.warehouseinventory_set.all().values_list('total_boxes', flat=True))
                #     location.total_retained_boxes = sum(location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
                #     boxes = float(pallet.boxes)
                #     print(location.available_weight)
                #     location.available_weight = (location.available_weight + (confirmation.product.get_available_weight * boxes))
                #     location.available_volume = (location.available_volume + (confirmation.product.get_available_volume * boxes))
                #     print(location.available_weight)
                #     if location.available_weight < 0:
                #         location.available_weight = 0
                #     if location.available_volume < 0:
                #         location.available_volume = 0
                #     location.save()



class ExitPalletPesoVariable(models.Model):
    peso_variable_quantity = models.FloatField(verbose_name=_('Peso Variable Quantity'), null=True, blank=True,default=0)
    werehouse_exit_pallet = models.ForeignKey(WarehouseExitPallet, null=False,verbose_name=_('Warehouse Exit Pallet'))
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)    

    def __str__(self):
        return "exit_id--- " +str(self.werehouse_exit_pallet_id)+"____"+ str(self.werehouse_exit_pallet.werehouse_exit_confirmation.werehouse_exit_id ) + " pallet---- " + str(self.peso_variable_quantity)
    def __unicode__(self):
        return str(self.peso_variable_quantity)

def restore_boxes_on_pallet_delete(sender, instance, **kwargs):
    instance = WarehouseExitPallet.objects.get(pk=instance.id)
    inventory =  instance.inventory
    if instance.werehouse_exit_confirmation.werehouse_exit.status =='finish':
        inventory.available_total_boxes+=instance.boxes
        inventory.total_boxes+=instance.boxes
    else:
        inventory.available_total_boxes+=instance.boxes

        
    inventory.save()
    #set location space in warehouse
    warehouse_numbers = instance.warehouse.id
    location_numbers = instance.location
    for location in WarehouseLocation.objects.filter(id=location_numbers.id,warehouse_id=warehouse_numbers):
       location.total_stored_kg = sum(location.warehouseinventory_set.all().values_list('available_gross_weight', flat=True))
       location.total_stored_boxes = sum(location.warehouseinventory_set.all().values_list('total_boxes', flat=True))
       location.total_retained_boxes = sum(location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
       boxes = float(instance.boxes)
       location.available_weight = (location.available_weight + (instance.werehouse_exit_confirmation.product.get_available_weight * boxes))
       location.available_volume = (location.available_volume + (instance.werehouse_exit_confirmation.product.get_available_volume * boxes))
       if location.available_weight < 0:
           location.available_weight = 0
       if location.available_volume < 0:
           location.available_volume = 0
       location.save()





def create_production_confirmation(sender, instance, **kwargs):
    if not hasattr(instance,'wexitconfirmation'):
        WExitConfirmation.objects.create(product = instance.product,
                                        exp_date = instance.werehouse_exit.exit_date,
                                        werehouse_exit_id = int(instance.werehouse_exit.id),
                                        removed_boxes = [],
                                        removed_kgs = [],
                                        auto_pick_data = {} ,
                                        exit_product_measurement=instance)




def clear_cache_entrance(sender, instance, created, **kwargs):
    from django.core.cache import cache
    from sga.celery import updateCache
    cache.clear()
    if sender == WarehouseExitPallet:
        exit_id = instance.werehouse_exit_confirmation.werehouse_exit.id
    elif sender == WarehouseExit:
        exit_id = instance.id
    elif sender == WExitConfirmation:
        exit_id = instance.werehouse_exit.id
    updateCache.delay(reverse_lazy('confirm-exit-pallets',kwargs={"pk":exit_id}))
    updateCache.delay(reverse_lazy('update-exit',kwargs={"pk":exit_id}))

# post_save.connect(update_exit_total_kg, sender=WExitProductMeasurement)
# post_save.connect(update_exit_inventory_details, sender=WarehouseExit)
pre_delete.connect(restore_boxes_on_pallet_delete, sender=WarehouseExitPallet)
post_save.connect(clear_cache_entrance, sender=WarehouseExitPallet)
post_save.connect(clear_cache_entrance, sender=WarehouseExit)
post_save.connect(clear_cache_entrance, sender=WExitConfirmation)
post_save.connect(create_production_confirmation, sender=WExitProductMeasurement)


@receiver(pre_save, sender=WarehouseExit)
def on_change(sender, instance, **kwargs):
    if not instance.id is None:
        previous = WarehouseExit.objects.get(id=instance.id)
        if previous.exit_hour != instance.exit_hour:
            from sga.celery import delete_bays
            delete_bays.delay('exit', instance.id)

@receiver(pre_save,sender=WarehouseExit)
def update_status(sender,**kwargs):
    obj = kwargs['instance']
    if obj.status in ["CONFIRM EXIT", "CONFIRMAR SALIDA"]:
        obj.status = 'finish'
    elif obj.status in ["Grabar", "Guardar", "Save"]:
        obj.status = 'control'
