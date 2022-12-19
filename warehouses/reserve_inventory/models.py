from __future__ import unicode_literals
from django.db.models.signals import pre_save, post_save
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from users.models import UserProfile
from catalogs.warehouse.models import Warehouse, WarehouseInventory,WarehouseLocation,WarehouseSection
import pdb

class ReserveInventory(models.Model):
	CADU = 'CADU'
	DAOP = 'DAOP'
	MUES = 'MUES'
	CAIN = 'CAIN'
	DAOC = 'DAOC'
	CLIE = 'CLIE'
	DEVO = 'DEVO'
	FADO = 'FADO'
	NOID = 'NOID'
	OTRO = 'OTRO'
	DEST = 'DEST'
	CUAR = 'CUAR'
	PorInventario = 'Por Inventario'
	MotiveToReserveLIST = (
		(CADU, _('Caducado')),
		(DAOP, _('dano de operacion')),
		(MUES, _('muestras')),
		(CAIN, _('caja incompleta')),
		(DAOC, _('dano oculto')),
		(CLIE, _('cliente')),
		(DEVO, _('devolucion')),
		(FADO, _('falta de documentos TIF')),
		(NOID, _('producto no identificado')),
		(OTRO, _('otro')),
		(DEST, _('destruccion')),
		(CUAR, _('cuarentena')),
		(PorInventario, _('Por Inventario'))
		)

	palet_lot = models.CharField(verbose_name=_('Palet Lot'), max_length=255, null=False, blank=False)
	boxes = models.FloatField(verbose_name=_('Boxes'), null=True, blank=True,default=0)
	reserve_boxes = models.FloatField(verbose_name=_('Reserve Boxes'), null=True, blank=True,default=0)
	motive_to_reserve = models.CharField(verbose_name=_('Motive to reserve'), max_length=255, choices=MotiveToReserveLIST)
	notes = models.CharField(verbose_name=_('Notes'), null=True, blank=True,max_length=255,)
	released_store_box = models.FloatField(verbose_name=_('Reserve Stored Boxes'), null=True, blank=True,default=0)
	# user = models.ForeignKey(UserProfile, null=True,verbose_name=_('Usuario'))
	created_by =  models.ForeignKey(UserProfile, null=True,verbose_name=_('Created By'))
	
	inventory = models.ForeignKey(WarehouseInventory, null=True,verbose_name=_('Inventario de almacen'))
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	original_reserve_boxes = None
	original_released_store_box = None
	def __str__(self):
		return self.palet_lot

	def __unicode__(self):
		return self.palet_lot

	def get_absolute_url(self):
		return reverse('inventory-reserve-list')

	def __init__(self, *args, **kwargs):
		super(ReserveInventory, self).__init__(*args, **kwargs)
		self.original_reserve_boxes= self.reserve_boxes
		self.original_released_store_box= self.released_store_box

class ReserveInventoryLog(models.Model):
	release_boxes = models.FloatField(verbose_name=_('Reserve Boxes'), null=True, blank=True,default=0)
	
	notes = models.CharField(verbose_name=_('Notes'), null=True, blank=True,max_length=255,)
	inventory = models.ForeignKey(WarehouseInventory, null=True,verbose_name=_('Inventario de almacen'))
	user = models.ForeignKey(UserProfile, null=True,verbose_name=_('Usuario'))
	reserveinventory = models.ForeignKey(ReserveInventory, null=True,verbose_name=_('Inventario de almacen'))

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return "id="+ str(self.id) + ",  release_boxes=" + str(self.release_boxes)

	def __unicode__(self):
		return "id="+ str(self.id) + ",  release_boxes=" + str(self.release_boxes)

