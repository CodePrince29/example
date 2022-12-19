
from __future__ import unicode_literals

from django.db import models
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.dispatch import receiver
from decimal import Decimal
from warehouses.warehouse_entrance.models import WarehouseEntrancePallet
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save


class TakingInventory(models.Model):

	PENDING = 'pending'
	FINISH = 'finish'

	STATUS = (
		(PENDING, _('Pending')),
		(FINISH, _('Finish')))
	taking_date = models.DateField(verbose_name=_('Taking Inventory Date'),auto_now_add=True)
	taking_hour = models.TimeField(verbose_name=_('Taking Inventory Hour'),blank=True,auto_now_add=True)
	customer = models.ForeignKey(Client, null=False,verbose_name=_('Customer'))
	product = models.ManyToManyField(Product,verbose_name=_('Product'))
	warehouseentrancepallet = models.ManyToManyField(WarehouseEntrancePallet,verbose_name=_('WarehouseEntrancePallet'))
	total_kg = models.FloatField(verbose_name=_('Total Kg'), null=True, blank=True,default=0)
	status = models.CharField(verbose_name=_('Warehouse Entrance Status'), max_length=20, default=PENDING, null=False, blank=False, choices=STATUS)
	created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
	updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)

	def get_absolute_url(self):
		return reverse('inventory-taking-list')
	def __str__(self):
		return str(self.customer.name)
	@property
	def product_name(self):
		return ",".join(list(self.product.all().values_list('product_code', flat=True)))

	@property
	def get_total_pallets_count(self):
		return len(self.warehouseentrancepallet.all())

	@property
	def get_total_price(self):
		sum_data = self.warehouseentrancepallet.aggregate(total_price=Sum('warehouseinventory__available_gross_weight'))
		return sum_data['total_price']
	@property
	def get_product_ids(self):
		return [i for i in self.product.all().values_list('id',flat=True)]
	@property
	def get_pallet_ids(self):
		return [i for i in self.warehouseentrancepallet.all().values_list('id',flat=True)]


class InventoryPesoVariable(models.Model):
    peso_variable_quantity = models.FloatField(verbose_name=_('Peso Variable Quantity'), null=True, blank=True,default=0)
    werehouse_entrance_pallet = models.ForeignKey(WarehouseEntrancePallet, null=False,verbose_name=_('Warehouse Entrance Pallet'))
    created_at = models.DateTimeField(verbose_name=_('Created At'),auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated At'),auto_now=True)    

    def __str__(self):
        return "%s-%s"%(str(self.werehouse_entrance_pallet), str(self.peso_variable_quantity)) 
    def __unicode__(self):
        return str(self.peso_variable_quantity)
