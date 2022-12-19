from __future__ import unicode_literals
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from decimal import Decimal
from django.db import models
from catalogs.clients.models import Client
from catalogs.product.models import Product
from catalogs.warehouse.models import Warehouse,WarehouseLocation,WarehouseSection,WarehouseInventory,WarehouseDepthLevel
from warehouses.warehouse_entrance.models import WarehouseEntrancePallet,WarehouseEntrance,WarehouseEntranceConfirmation
from django.db.models.signals import pre_save, post_save
from catalogs.utilities import WarehouseLocationPrams
from users.models import UserProfile

class WarehouseRelocation(models.Model):
	customer = models.ForeignKey(Client, null=False, blank=False,verbose_name=_('Customer'))
	werehouse_entrance = models.ForeignKey(WarehouseEntrance, null=True, blank=True,verbose_name=_('Entrance'))
	product = models.ForeignKey(Product, null=False, blank=False,verbose_name=_('Product'))
	description = models.CharField(verbose_name=_('Reason for Relocation'), max_length=255, null=True, blank=True)
	source_warehouse = models.CharField(verbose_name=_('Source Warehouse'), max_length=255, null=True, blank=True,default='')
	source_location = models.CharField( verbose_name=_('Source Location'), max_length=255, null=True, blank=True,default='')
	destination_warehouse = models.ForeignKey(Warehouse, null=False,verbose_name=_('Destination Warehouse'))
	destination_location = models.ForeignKey(WarehouseLocation, null=False,verbose_name=_('Destination Location'))
	palet_lot = models.CharField(verbose_name=_('Palet Lot'), max_length=255, blank=True , null=True)
	created_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Created By'))

	created_at = models.DateField(auto_now=True)
	updated_at = models.DateField(auto_now=True)
	def __str__(self):
		return str(self.id)

	def __unicode__(self):
		return str(self.id)

	def get_absolute_url(self):
		return reverse('relocation-list')

    
@receiver(post_save,sender=WarehouseRelocation)
def update_inventory(sender,**kwargs):
	customer = kwargs['instance'].werehouse_entrance.customer
	entrance = kwargs['instance'].werehouse_entrance
	source_war = kwargs['instance'].source_warehouse
	source_loc = kwargs['instance'].source_location
	product = kwargs['instance'].product
	destin_war = kwargs['instance'].destination_warehouse
	destin_loc = kwargs['instance'].destination_location
	
	if source_loc == '':
		source_loc = 0
	if source_war == '':
		source_war = 0
	locations = WarehouseLocation.objects.filter(id=source_loc)
	if locations.exists():
		loc_num = locations.first()
	else:
		loc_num = ''
	destin_loc_number = kwargs['instance'].destination_location.location_number
	
	if kwargs['instance'].palet_lot:
		palet_lot = kwargs['instance'].palet_lot
		if source_war:
			entrance_conf = WarehouseEntrancePallet.objects.filter(warehouse= source_war, location=loc_num,werehouse_entrance_confirmation__product=product,werehouse_entrance_confirmation__werehouse_entrance=entrance.id,palet_lot=palet_lot)
		else:
			entrance_conf = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__product=product,werehouse_entrance_confirmation__werehouse_entrance=entrance.id,palet_lot=palet_lot)

		source_inventories = WarehouseInventory.objects.filter(product= product,warehouse_location= source_loc,client=customer,warehouse_entrance_pallet__palet_lot=palet_lot)
		destination_inventories = WarehouseInventory.objects.filter(product= product,warehouse_location=destin_loc,client=customer,warehouse_entrance_pallet__palet_lot=palet_lot)
		
	else:
		if source_war:
			entrance_conf = WarehouseEntrancePallet.objects.filter(warehouse= source_war, location=loc_num,werehouse_entrance_confirmation__product=product,werehouse_entrance_confirmation__werehouse_entrance=entrance.id,palet_lot=palet_lot)
		else:
			entrance_conf = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__product=product,werehouse_entrance_confirmation__werehouse_entrance=entrance.id,palet_lot=palet_lot)
		source_inventories = WarehouseInventory.objects.filter(product= product,warehouse_location= source_loc,client=customer)
		destination_inventories = WarehouseInventory.objects.filter(product= product,warehouse_location=destin_loc,client=customer)
	
	section_index = destin_war.get_warehouse_section(destin_loc.location_number)
	
	sections = WarehouseSection.objects.filter(index= section_index)
	if sections.exists():
		section = sections.first()
	
	retained_quantity = 0
	if entrance_conf.exists():
		for pallet in entrance_conf:
			pallet.warehouse = destin_war
			pallet.location = destin_loc
			pallet.rack_number = section
			pallet.save()
	if source_inventories.exists():
			
		for inventory in source_inventories:
			
			inventory.warehouse_location = destin_loc
			inventory.rack = section_index
			
			inventory.save()
			for exit in inventory.warehouseexitpallet_set.all():
				exit.warehouse = destin_war
				exit.location = destin_loc
				exit.rack_number = section
				exit.save()

			#update source location 
			source_location = WarehouseLocation.objects.get(id=source_loc)
			source_location.total_stored_kg = source_location.total_stored_kg-inventory.available_gross_weight
			source_location.total_stored_boxes = source_location.total_stored_boxes-inventory.available_total_boxes

			product = inventory.warehouse_entrance_pallet.werehouse_entrance_confirmation.product
			# source_box_weight = inventory.available_total_boxes*product.get_available_weight
			# source_box_volume = inventory.available_total_boxes*product.get_available_volume

			s_available_weight, s_available_volume = WarehouseLocationPrams().get_location_params(source_location)
			# source_location.available_weight = source_location.available_weight+source_box_weight
			# source_location.available_volume = source_location.available_volume+source_box_volume
			depths = WarehouseDepthLevel.objects.filter(warehouse_location_id = source_loc)
                if depths.exists():
                    for depth in depths:
                        source_location.available_weight = depth.weight_kg-s_available_weight
                        source_location.available_volume = depth.location_volume-s_available_volume
                        if(source_location.available_weight < 0):
                            source_location.available_weight = 0
                        if(source_location.available_volume < 0):
                            source_location.available_volume = 0
                        source_location.save()

			#update destination location data
			destination_location = WarehouseLocation.objects.get(id=destin_loc.id)
			destination_location.total_stored_kg = destination_location.total_stored_kg + inventory.available_gross_weight
			destination_location.total_stored_boxes = destination_location.total_stored_boxes + inventory.available_total_boxes
			product = inventory.warehouse_entrance_pallet.werehouse_entrance_confirmation.product
			# destination_box_weight = inventory.available_total_boxes*product.get_available_weight
			# destination_box_volume = inventory.available_total_boxes*product.get_available_volume
			
			d_available_weight, d_available_volume = WarehouseLocationPrams().get_location_params(destination_location)
			# destination_location.available_weight = destination_location.available_weight-destination_box_weight
			# destination_location.available_volume = destination_location.available_volume-source_box_volume
			depths = WarehouseDepthLevel.objects.filter(warehouse_location_id = destin_loc.id)
                if depths.exists():
                    for depth in depths:
                        destination_location.available_weight = depth.weight_kg-d_available_weight
                        destination_location.available_volume = depth.location_volume-d_available_volume
                        if(destination_location.available_weight < 0):
                            destination_location.available_weight = 0		
                        if(destination_location.available_volume < 0):
                            destination_location.available_volume = 0
                        destination_location.save()

