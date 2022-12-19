from django.shortcuts import render
import datetime
import copy , time
# from IPython import embed; embed()
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import View
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from .models import *
from catalogs.warehouse.models import Warehouse, WarehouseInventory,WarehouseLocation,WarehouseSection, WarehouseTruckBays

from warehouses.warehouse_entrance.models import WarehouseEntrance,WarehouseEntranceConfirmation,WarehouseEntrancePallet, EntrancePalletPesoVariable
# from catalogs.warehouse.models import Warehouse
from .forms import (WarehouseExitForm,
  WExitProductMeasurementFormSet,
  WExitConfirmationFormSet,
  WExitConfirmationForm,
  WarehouseExitPalletFormSet,
  WarehouseExitPalletMFormset,WarehouseExitPalletFonfirmForm, 
  NewWarehouseExitForm, NewWExitProductMeasurementFormSet,
  ConfirmationMeasurementEditFormSet, WarehouseSingleExitPalletMForm,
  )
from django.utils.translation import ugettext_lazy as _
from .serializers import (WarehouseEntranceFilterSerializer, WarehouseSerializer,WarehouseEntranceConfirmationSerializer,)
from warehouses.utils import render_to_pdf, render_entrance_pdf
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.template import loader
from catalogs.clients.models import Client
from rest_framework.permissions import IsAuthenticated, BasePermission
from api.serializers import WarehouseExitConfirmationPalletConfSerializer, WarehouseExitPalletDetailSerializer
from catalogs.notifications.models import Notification
from django.utils import timezone
from catalogs.general_params.models import GeneralParams
from multiprocessing import Process, Pool
class WarehouseExitList(LoginRequiredMixin, ListView):
	template_name = 'exit-list.html'
	model = WarehouseExit

	def get_queryset(self):
		queryset = WarehouseExit.objects.none()
		if  not self.request.user.get_client:
			queryset = WarehouseExit.objects.exclude(status=WarehouseExit.FINISH).order_by('-exit_date')
			return queryset
		else:
			if self.request.user.client_set.exists():
				queryset= self.request.user.client_set.first().warehouseexit_set.all().order_by('-exit_date')
				return queryset
			
		return queryset

class NewExitView(LoginRequiredMixin,CreateView):
	model = WarehouseExit
	form_class = WarehouseExitForm

	def get_template_names(self):
		if self.request.user.get_client:
			return "customer_new.html"
		return "new.html"

	def reserve_bay(self, data):
		try:
			bay = data.get('bay')
			if bay:
				from django.utils.timezone import get_current_timezone
				from datetime import datetime
				tz = get_current_timezone()
				time_slot = data.get('exit_date')+" "+data.get('exit_hour')
				time_slot = tz.localize(datetime.strptime(time_slot, '%Y-%m-%d %I:%M %p'))
				branch = data.get('branch')
				WarehouseTruckBays.objects.create(branch_id=branch,time_slot=time_slot,bay=bay,content_object=self.object)
		except Exception as ex:
			print(ex)

	def get_context_data(self, **kwargs):
		context = super(NewExitView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()

		if self.request.POST:
			context['w_exit_product_measurment_form'] = WExitProductMeasurementFormSet(self.request.POST, instance=self.object)
		else:
			context['w_exit_product_measurment_form'] = WExitProductMeasurementFormSet(instance=self.object)

		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.created_by = self.request.user
		context = self.get_context_data()
		w_exit_product_measurment_form = context['w_exit_product_measurment_form']
		if form.is_valid():
			self.object = form.save()
			if self.object.status in ['control']:
				instance = self.object
				exit_create_notification_customer(instance)
			w_exit_product_measurment_form.instance = self.object
			if w_exit_product_measurment_form.is_valid():
				w_exit_product_measurment_form.save()
				if int(self.request.POST.get('save_continue', 0)) == 1:
					return HttpResponseRedirect("confirm-exit-pallets/%s"%self.object.id )
				self.reserve_bay(self.request.POST)
				return super(NewExitView, self).form_valid(form)
			else:
				return self.render_to_response(self.get_context_data(form=form))
		else:
			return self.render_to_response(self.get_context_data(form=form))

		

class UpdateExitView(LoginRequiredMixin, UpdateView):
	model = WarehouseExit
	template_name = "edit-exit.html"
	form_class = WarehouseExitForm
	def get_context_data(self, **kwargs):
		context = super(UpdateExitView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()

		if self.request.POST:
			context['w_exit_product_measurment_form'] = WExitProductMeasurementFormSet(self.request.POST, instance=self.object)
		else:
			context['w_exit_product_measurment_form'] = WExitProductMeasurementFormSet(instance=self.object)

		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		context = self.get_context_data()
		w_exit_product_measurment_form = context['w_exit_product_measurment_form']
		if form.is_valid():
			self.object = form.save()
			w_exit_product_measurment_form.instance = self.object
			if w_exit_product_measurment_form.is_valid():
				w_exit_product_measurment_form.save()
				if int(self.request.POST.get('save_continue', 0)) == 1:
					url = reverse('confirm-exit-pallets', kwargs={'pk': self.object.id})
					return HttpResponseRedirect(url )
				return super(UpdateExitView, self).form_valid(form)
			else:
				return self.render_to_response(self.get_context_data(form=form))
		else:
			return self.render_to_response(self.get_context_data(form=form))

			


class ConfirmPalletView(LoginRequiredMixin,UpdateView):
	model = WarehouseExit
	template_name = "pallet_confirmation.html"
	form_class = WarehouseExitPalletFonfirmForm
	def get_context_data(self, **kwargs):
		context = super(ConfirmPalletView, self).get_context_data(**kwargs)
		context['warehouse_location'] = Warehouse.objects.values('id', 'code')
		confirmations = self.object.wexitconfirmation_set.prefetch_related('warehouseexitpallet_set', 'product').order_by('id')
		pallets = WarehouseExitConfirmationPalletConfSerializer(confirmations,many=True).data
		context['exit_confirmations'] = pallets

		if self.request.POST:
			context['w_exit_confirmation_pallet'] = WarehouseExitPalletFormSet(self.request.POST, instance=self.object)
		else:
			context['w_exit_confirmation_pallet'] = WarehouseExitPalletFormSet(instance=self.object)
			context['warehouses'] = context['warehouse_location']
			context['locations'] = WarehouseLocation.objects.filter(is_locked=False).values('id', 'location_number')
			context['sections'] = WarehouseSection.objects.values('id', 'index')
			context['inventories'] = WarehouseInventory.objects.values('id')
			
		return context

	def form_valid(self, form):
		existing_pal = form.instance.wexitconfirmation_set.order_by('id').values('warehouseexitpallet', 'warehouseexitpallet__inventory', 'warehouseexitpallet__boxes', 'warehouseexitpallet__gross_weight')
		existing_pallet =  copy.copy(existing_pal) 
		self.object = form.save(commit=False)
		context = self.get_context_data()
		w_exit_confirmation_pallet = context['w_exit_confirmation_pallet']
		w_exit_confirmation_pallet.instance = self.object
		if w_exit_confirmation_pallet.is_valid():
			w_exit_confirmation_pallet.save()
        	for pallet in self.object.wexitconfirmation_set.order_by('id').values('warehouseexitpallet', 'warehouseexitpallet__inventory', 'warehouseexitpallet__boxes'):
				old_pallet = filter(lambda x: x['warehouseexitpallet'] == pallet['warehouseexitpallet'], existing_pallet)
				new_pallet = [pallet for old_palt in existing_pallet if pallet['warehouseexitpallet'] != old_palt['warehouseexitpallet'] ]
				if pallet['warehouseexitpallet__inventory'] != None and len(old_pallet) > 0:
					old_pallet = old_pallet[0]                    
					old_inventories = WarehouseInventory.objects.filter(pk=old_pallet['warehouseexitpallet__inventory'])                    
					if old_inventories.exists() and old_pallet['warehouseexitpallet__inventory'] != pallet['warehouseexitpallet__inventory']:
						# it means pallet inventory has changed
						# revert boxes of last inventory
						# previous inventory reverted
						old_inventory = old_inventories.first()
						old_inventory_a_t_boxes = old_inventory.available_total_boxes + old_pallet['warehouseexitpallet__boxes']
						old_inventory_t_kg = old_inventory.total_kg + old_pallet['warehouseexitpallet__gross_weight']
						old_inventories.update(available_total_boxes=old_inventory_a_t_boxes, total_kg=old_inventory_t_kg) 
				if pallet['warehouseexitpallet'] not in [item.get('warehouseexitpallet') for item in existing_pallet]:
					# New pallet
					inventories = WarehouseInventory.objects.filter(pk=pallet['warehouseexitpallet__inventory'])
					if inventories.exists():
						inventory = inventories.first()
						inventory_a_t_boxes = inventory.available_total_boxes - pallet['warehouseexitpallet__boxes']
						inventories.update(available_total_boxes=inventory_a_t_boxes)

		self.object = form.save()
		update_exit_inventory_details(self.object)
		if self.object.status in ['InManeuvers']:
			instance = self.object
			exit_create_notification_inmaniobras(instance)

		conf = self.object.wexitconfirmation_set.all().values_list('id',flat=True)                 
		exit_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=conf)
		if int(self.request.POST.get('process_print_picking', 0)) == 1:
			
			data = {
			'object': self.object,
			'print_datetime': self.object.exit_date, 
			'entrans_id': self.object.id,
			'customer_name': self.object.customer,
			'client_code': self.object.customer.client_code,
			'transportistas': self.object.carrier,
			'transporte': self.object.vehicle,
			'placas': self.object.license_plate,
			'exit_pallets': exit_pallets,
			'total_boxes': self.object.get_total_pallet_boxes,
			'total_gross_weight': self.object.get_total_pallet_gross_weight,
			'total_net_weight': self.object.get_total_pallet_net_weight,
			'get_total_kgs': self.object.get_pallet_total_kgs,

			}

			pdf = render_to_pdf('pdf/print_picking.html', data)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Salida_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
				content = "attachment; filename=%s" %(filename)
				response['Content-Disposition'] = content
				return response

		if self.object.status == 'finish':
			data = {
			'object': self.object,
			'print_datetime': self.object.exit_date, 
			'entrans_id': self.object.id,
			'customer_name': self.object.customer,
			'client_code': self.object.customer.client_code,
			'transportistas': self.object.carrier,
			'transporte': self.object.vehicle,
			'placas': self.object.license_plate,
			'exit_pallets': exit_pallets,
			'total_boxes': self.object.get_total_pallet_boxes,
			'total_gross_weight': self.object.get_total_pallet_gross_weight,
			'total_net_weight': self.object.get_total_pallet_net_weight,
			'get_total_kgs': self.object.get_pallet_total_kgs,

			}
			pdf = render_to_pdf('pdf/invoice_exit.html', data)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Salida_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
				content = "attachment; filename=%s" %(filename)
				response['Content-Disposition'] = content
				return response
				
		if self.object.status == "control":
			return HttpResponseRedirect(reverse_lazy('confirm-exit-pallets', kwargs={'pk': self.object.id}))
		return super(ConfirmPalletView, self).form_valid(form)


def exit_create_notification_inmaniobras(instance):
	if instance.created_by is not None:

		notification_param_status = 0
		notification_param = GeneralParams.objects.filter(key="EnableInternalNotifications")
		if notification_param.exists():
			notification_param_status = notification_param.first().value

		if notification_param_status == "1":
			if instance.status == 'InManeuvers':
				if instance.created_by.client_set.all().exists():
					message = "Se ha registrado maniobra de Salida del cliente : " + instance.created_by.client_set.first().name +" con Folio: " + str(instance.id)
				else:
					message = "Se ha registrado maniobra de Salida del cliente : " + instance.created_by.username +" con Folio: " + str(instance.id)
				
				Notification.objects.create(content_object=instance,
					occurred_dt=timezone.now(),
					created_by=instance.created_by.id,
					message=message)

def exit_create_notification_customer(instance):
	if instance.created_by is not None:
		if instance.created_by.is_staff==False and instance.created_by.role_id== None and instance.status == 'control':
			if instance.created_by.client_set.all().exists():
				message = "El cliente: " + instance.created_by.client_set.first().name +" ha realizado un registro de Salida de Almacen."
			else:
				message = "El cliente: " + instance.created_by.username +" ha realizado un registro de Salida de Almacen."

			Notification.objects.create(
			content_object=instance,
			occurred_dt=timezone.now(),
			created_by=instance.created_by.id,
			message=message
			)
        

#new exit process logic
class NewWarehouseExitList(LoginRequiredMixin, ListView):
	template_name = 'new-exit-list.html'
	model = WarehouseExit

	def get_queryset(self):
		queryset = WarehouseExit.objects.none()
		if  not self.request.user.get_client:
			queryset = WarehouseExit.objects.exclude(status=WarehouseExit.FINISH).order_by('-exit_date')
			return queryset
		else:
			if self.request.user.client_set.exists():
				queryset= self.request.user.client_set.first().warehouseexit_set.all().order_by('-exit_date')
				return queryset
			
		return queryset

class NewWarehouseExitView(LoginRequiredMixin,CreateView):
	model = WarehouseExit
	form_class = NewWarehouseExitForm

	def get_template_names(self):
		return "new_exit.html"

	def reserve_bay(self, data):
		try:
			bay = data.get('bay')
			if bay:
				from django.utils.timezone import get_current_timezone
				from datetime import datetime
				tz = get_current_timezone()
				time_slot = data.get('exit_date')+" "+data.get('exit_hour')
				time_slot = tz.localize(datetime.strptime(time_slot, '%Y-%m-%d %I:%M %p'))
				branch = data.get('branch')
				WarehouseTruckBays.objects.create(branch_id=branch,time_slot=time_slot,bay=bay,content_object=self.object)
		except Exception as ex:
			print(ex)

	def get_context_data(self, **kwargs):
		context = super(NewWarehouseExitView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()

		if self.request.POST:
			context['w_exit_product_measurment_form'] = NewWExitProductMeasurementFormSet(self.request.POST, instance=self.object)
		else:
			context['w_exit_product_measurment_form'] = NewWExitProductMeasurementFormSet(instance=self.object)

		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.created_by = self.request.user
		context = self.get_context_data()
		w_exit_product_measurment_form = context['w_exit_product_measurment_form']
		if form.is_valid():
			self.object = form.save()
			if self.object.status in ['control']:
				instance = self.object
				exit_create_notification_customer(instance)
			w_exit_product_measurment_form.instance = self.object
			if w_exit_product_measurment_form.is_valid():
				w_exit_product_measurment_form.save()
				if self.object.status in ['InManeuvers']:
					self.object.sent_to_maniobras_at = datetime.datetime.now()
					self.object.sent_to_maniobras_by = self.request.user
					self.object.save()
					exit_create_pallets_customer(self.object, self.request)
					return get_print_picking_report(self.object)
				self.reserve_bay(self.request.POST)
				return HttpResponseRedirect("/warehouse_exit/new-warehouse-exit-list" )
				
				# return super(NewWarehouseExitView, self).form_valid(form)
			else:
				return self.render_to_response(self.get_context_data(form=form))
		else:
			return self.render_to_response(self.get_context_data(form=form))

		
class NewUpdateExitView(LoginRequiredMixin, UpdateView):
	model = WarehouseExit
	template_name = "new_wexit_exit.html"
	form_class = NewWarehouseExitForm
	def get_context_data(self, **kwargs):
		context = super(NewUpdateExitView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()

		if self.request.POST:
			context['w_exit_product_measurment_form'] = NewWExitProductMeasurementFormSet(self.request.POST, instance=self.object)
		else:
			context['w_exit_product_measurment_form'] = NewWExitProductMeasurementFormSet(instance=self.object)

		return context

	def form_valid(self, form):

		self.object = form.save(commit=False)
		context = self.get_context_data()
		w_exit_product_measurment_form = context['w_exit_product_measurment_form']
		if form.is_valid():
			self.object = form.save()
			w_exit_product_measurment_form.instance = self.object
			if w_exit_product_measurment_form.is_valid():
				w_exit_product_measurment_form.save()
				if self.object.status in ['InManeuvers']:
					self.object.sent_to_maniobras_at = datetime.datetime.now()
					self.object.save()
					exit_create_pallets_customer(self.object, self.request)
					return get_print_picking_report(self.object)
				return HttpResponseRedirect("/warehouse_exit/new-warehouse-exit-list" )
				
		else:
			return self.render_to_response(self.get_context_data(form=form))


class ConfirmWarehouseExitView(LoginRequiredMixin,UpdateView):
	model = WarehouseExit
	template_name = "new_exit_confirmation.html"
	form_class = WarehouseExitForm
	def get_context_data(self, **kwargs):
		context = super(ConfirmWarehouseExitView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()

		if self.request.POST:
			context['w_exit_product_measurment_form'] = ConfirmationMeasurementEditFormSet(self.request.POST, instance=self.object)
		else:
			context['w_exit_product_measurment_form'] = ConfirmationMeasurementEditFormSet(instance=self.object)

		return context
		

	def form_valid(self, form):
		self.object = form.save(commit=False)
		context = self.get_context_data()
		w_exit_product_measurment_form = context['w_exit_product_measurment_form']
		if form.is_valid():
			self.object = form.save()
			w_exit_product_measurment_form.instance = self.object
			if w_exit_product_measurment_form.is_valid():
				try:
					p1 = Process(target=self.save_nested_form, args=(w_exit_product_measurment_form,))
				except:
					pass
			p1.start()
			p1.join()
			print("We're done")
		if self.object.status in ['finish']:			
			from django.utils import timezone
			import pytz
			timezone.activate(pytz.timezone("America/Mexico_City"))
			confirmed_at = timezone.localtime(timezone.now())
			self.object.confirmed_by = self.request.user
			self.object.confirmed_at = confirmed_at
			self.object.save()
			ent_conf = self.object.wexitconfirmation_set.values_list('id',flat=True)
			measurement_query = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.object.id).order_by('product__product_code')
			measurement_products = measurement_query.values('product_id', 'product_description', 'product__product_code').annotate(total_boxes=Coalesce(Sum('wexitconfirmation__warehouseexitpallet__boxes'), 0),total_gross_weight=Coalesce(Sum('wexitconfirmation__warehouseexitpallet__gross_weight'), 0))
			# measurement_products = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.object.id)
			data = {
			'object': self.object,
			'print_datetime': confirmed_at, 
			'entrans_id': self.object.id,
			'customer_name': self.object.customer,
			'client_code': self.object.customer.client_code,
			'transportistas': self.object.carrier,
			'transporte': self.object.vehicle,
			'placas': self.object.license_plate,
			'measurement_products': measurement_products,
			'total_boxe_kgs': self.object.get_total_pallet_boxes_kgs,
			'total_boxes': self.object.get_total_pallet_boxes,
			'total_gross_weight': self.object.get_total_pallet_gross_weight,
			'total_net_weight': self.object.get_total_pallet_net_weight
			}


			pdf = render_entrance_pdf('pdf/new_invoice_exit.html', data)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Exit_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
				content = "attachment; filename=%s" %(filename)
				response['Content-Disposition'] = content
				return response
			return HttpResponseRedirect("/warehouse_exit/new-warehouse-exit-list" )
		return HttpResponseRedirect("/warehouse_exit/new-warehouse-exit-list" )

	def save_nested_form(self, form):
		form.save()
	def form_invalid(self, form):
		return HttpResponseRedirect("/warehouse_exit/new-warehouse-exit-list" )

def exit_create_pallets_customer(instance, request):
  measurements = instance.list_product
  for measurement in measurements:
    hash_data = {}
    if(measurement.werehouse_entrance_id not in [None, '']):
      hash_data.update({"werehouse_entrance_confirmation__werehouse_entrance_id": measurement.werehouse_entrance_id  })
    if(measurement.exp_date not in [None, '']):
      hash_data.update({"exp_date": measurement.exp_date })
    if(measurement.cost_lot not in [None, '']):
      hash_data.update({"cost_lot": measurement.cost_lot })
    if(measurement.palet_lot not in [None, '']):
      hash_data.update({"palet_lot": measurement.palet_lot })
    order_by = ['exp_date','warehouse_entrance_pallet_id']
    inventories_ids = WarehouseEntrancePallet.objects.filter(**hash_data).values_list('warehouseinventory', flat=True)
    inventories = WarehouseInventory.objects.filter(available_total_boxes__gt=0, id__in=inventories_ids).order_by(*order_by)
    inventories = inventories.filter(product__id=measurement.product_id,client=instance.customer_id)
    if len(hash_data) >0 and inventories.exists():
      create_confirmation_and_pallet(inventories, measurement, instance , request)
    else:
      order_by = ['exp_date','warehouse_entrance_pallet_id']
      inventories = WarehouseInventory.objects.filter(available_total_boxes__gt=0,product__id=measurement.product_id,client=instance.customer_id).order_by(*order_by)
      if inventories.exists():
        create_confirmation_and_pallet(inventories, measurement, instance , request)

def create_confirmation_and_pallet(inventories, measurement, instance, request ):
  request_boxes = measurement.boxes
  total_kg = measurement.total_kg
  current_user = request.user.id
  inventory_boxes = 0
  inventory_data = []
  for invt in inventories:
    request.session['%s-%s'%(invt.id, current_user)] = None
    if measurement.product.variable_weight:
        gross_weight = total_kg
        net_weight = total_kg
    else:
        gross_weight = round((float(invt.warehouse_entrance_pallet.gross_weight) / float(invt.warehouse_entrance_pallet.boxes)),2)
        net_weight = round((float(invt.warehouse_entrance_pallet.net_weight) / float(invt.warehouse_entrance_pallet.boxes)),2)
    if request.session.get('%s-%s'%(invt.id, current_user)) == None:
      inventory_boxes += invt.available_total_boxes
      if invt.available_total_boxes > 0:        
        inv_hash = get_warehouse_detail(invt,invt.available_total_boxes,gross_weight,net_weight)
        inventory_data.append(inv_hash)
    else:
      inventory_boxes += request.session.get('%s-%s'%(invt.id, current_user))
      if request.session.get('%s-%s'%(invt.id, current_user)) >0:        
        inv_hash = get_warehouse_detail(invt,request.session.get('%s-%s'%(invt.id, current_user)),gross_weight,net_weight)
        inventory_data.append(inv_hash)
  responce_data = []
  if inventory_boxes < request_boxes:
    return []
  else:

    for inventory in inventory_data:      
      palet = inventory['packages_per_pallet']
      available_box = request.session.get('%s-%s'%(inventory['id'], current_user))

      if not available_box:
        available_box = inventory['available_total_boxes']
        request.session['%s-%s'%(inventory['id'], current_user)] = available_box        
      if available_box and available_box < 0:
        request.session['%s-%s'%(inventory['id'], current_user)] = inventory['available_total_boxes']
        available_box = inventory['available_total_boxes']
      if(request_boxes >= available_box):
        data = responce_inventory_data(inventory,available_box, measurement)
        responce_data.append(data)
        if not inventory['available_total_boxes']==available_box:
          request.session['%s-%s'%(inventory['id'], current_user)] = request_boxes - available_box
        else:
          request.session['%s-%s'%(inventory['id'], current_user)]= inventory['available_total_boxes']-available_box
        if request_boxes == available_box:
          break
        else:
          request_boxes-= available_box
          continue  
            
      else:
        if request_boxes>0:            
          inv_kg = inventory['total_kg']
          
          total_boxes = inv_kg/palet
          data = responce_inventory_data(inventory,request_boxes, measurement)          
          responce_data.append(data)
            
          if request.session.get('%s-%s'%(inventory['id'], current_user)):
            if request.session.get('%s-%s'%(inventory['id'], current_user)) > request_boxes:
              request.session['%s-%s'%(inventory['id'], current_user)] = request.session.get('%s-%s'%(inventory['id'], current_user), 0) - request_boxes
            else:
              request.session['%s-%s'%(inventory['id'], current_user)] = request_boxes - request.session.get('%s-%s'%(inventory['id'], current_user), 0)
          break
        else:
          break
          pass
    taken_boxes = 0
    exit_conf = measurement.wexitconfirmation
    if not exit_conf.warehouseexitpallet_set.all().exists():
      for data in responce_data:
        if measurement.wexitconfirmation == None:
          exit_conf = WExitConfirmation.objects.create(exit_product_measurement_id=measurement.id, product_id= measurement.product.id,
          cost_lot= data['cost_lot'], exp_date= data['exp_date'], gross_weight= data['gross_weight'], net_weight= data['net_weight'] ,
          invoice_weight= data['invoice_weight'], retained_quantity=data['retained_quantity'], retained_reason=data['retained_reason'],
          werehouse_exit_id= instance.id, removed_boxes= [data['boxes']], removed_kgs=[data['gross_weight']], auto_pick_data= data )
        pallet = WarehouseExitPallet.objects.create(warehouse_id = data['warehouse'], location_id = data['location'], palet_lot = data['pallet'], rack_number_id = data['rack_number'], boxes= data['boxes'], werehouse_exit_confirmation_id = exit_conf.id, cost_lot=data['cost_lot'], exp_date=data['exp_date'], gross_weight=data['gross_weight'], net_weight=data['net_weight'], invoice_weight=data['invoice_weight'], retained_quantity=data['retained_quantity'], retained_reason=data['retained_reason'], inventory_id=data['inventory'], box_kg=data['box_kg'] )
        entrance_pallet = pallet.inventory.warehouse_entrance_pallet
        engtrance_pallets = EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet_id=entrance_pallet.id)
        index = 1
        total_weight = 0
        for data in engtrance_pallets:
          if index <= pallet.boxes:
          	ExitPalletPesoVariable.objects.create(peso_variable_quantity=data.peso_variable_quantity, werehouse_exit_pallet=pallet)
          	total_weight += data.peso_variable_quantity
          index +=1
          pallet.gross_weight = total_weight
          pallet.net_weight = total_weight
          pallet.save()
        set_pallet_details(pallet)

def responce_inventory_data(inventory,available_box, measurement):
  if measurement.product.variable_weight:
    weight = measurement.total_kg / measurement.boxes
    kg_per_box =round((weight * available_box), 2)
    gross_weight = kg_per_box
    net_weight = kg_per_box
  else:
  	gross_weight = round(inventory['gross_weight'] * available_box,2)
  	net_weight = round(inventory['net_weight'] * available_box,2)

  return {
  "inventory": inventory['id'],
  "boxes": available_box,
  "inventory_gross_weight": round(inventory['inventory_gross_weight']),
  "inventory_net_weight": round(inventory['inventory_net_weight']),
  "pallet": inventory['pallet_lot'],
  "warehouse":inventory['warehouse'],
  "location": inventory['location'],
  "rack_number": inventory['rack_number'],
  "cost_lot":  inventory['cost_lot'],
  "exp_date":  inventory['exp_date'],
  "gross_weight": round(gross_weight,2),
  "net_weight":  round(net_weight,2) ,
  "invoice_weight":  round(inventory['invoice_weight']),
  "retained_quantity":  inventory['retained_quantity'],
  "retained_reason":  inventory['retained_reason'],
  "box_kg": inventory['box_kg'],
  "warehouse_name": inventory['warehouse_name'],
  "location_name": inventory['location_name'],
  "rack_name": inventory['rack_name'],
  "pallet_id":inventory['pallet_id'],
  }

def get_warehouse_detail(invt,boxes,gross_weight,net_weight):
  return  {
  "id": invt.id,
  "inventory_gross_weight": invt.available_gross_weight,
  "inventory_net_weight": invt.available_net_weight,
  "available_total_boxes": boxes,
  "pallet_lot": invt.warehouse_entrance_pallet.palet_lot,
  "warehouse": invt.warehouse_entrance_pallet.warehouse.id,
  "location":invt.warehouse_entrance_pallet.location.id ,
  "rack_number":invt.warehouse_entrance_pallet.rack_number.id,
  "cost_lot": invt.warehouse_entrance_pallet.cost_lot ,
  "exp_date": invt.warehouse_entrance_pallet.exp_date ,
  "gross_weight": gross_weight,
  "net_weight": net_weight,
  "invoice_weight": invt.warehouse_entrance_pallet.invoice_weight,
  "retained_quantity": invt.warehouse_entrance_pallet.retained_quantity,
  "retained_reason": invt.warehouse_entrance_pallet.retained_reason,
  "box_kg": round(invt.total_kg,2),
  "total_kg": invt.total_kg,
  "packages_per_pallet": invt.product.packages_per_pallet ,
  "available_boxes": invt.available_total_boxes,

  "warehouse_name": invt.warehouse_entrance_pallet.warehouse.code,
  "location_name":invt.warehouse_entrance_pallet.location.location_number ,
  "rack_name":invt.warehouse_entrance_pallet.rack_number.index,
  "pallet_id":invt.warehouse_entrance_pallet.id,
  }


def get_print_picking_report(instance):
	from django.utils import timezone
	import pytz
	timezone.activate(pytz.timezone("America/Mexico_City"))
	document_picked_at = timezone.localtime(timezone.now())
	# instance.save()
	pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation__werehouse_exit_id = instance.id ).order_by('werehouse_exit_confirmation__exit_product_measurement__product__product_code')
	measurement_query = WExitProductMeasurement.objects.filter(werehouse_exit_id=instance.id).order_by('product__product_code')
	measurement_products = measurement_query.values('product_id', 'product_description', 'product__product_code').annotate(total_boxes=Coalesce(Sum('boxes'), 0))

	# measurement_products = WExitProductMeasurement.objects.filter(werehouse_exit_id=instance.id).order_by('product__product_code')
	data = {
	'object': instance,
	'print_datetime': document_picked_at, 
	'entrans_id': instance.id,
	'customer_name': instance.customer,
	'client_code': instance.customer.client_code,
	'transportistas': instance.carrier,
	'transporte': instance.vehicle,
	'placas': instance.license_plate,
	'measurement_products': measurement_products,
	'pallets': pallets,
	'total_boxe_kgs':instance.get_total_pallet_boxes_kgs,
	'total_boxes': instance.get_total_pallet_boxes,
	'total_gross_weight': instance.get_total_pallet_gross_weight,
	'total_net_weight': instance.get_total_pallet_net_weight
	}


	pdf = render_entrance_pdf('pdf/new_exit_print_picking.html', data)
	if pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		filename = "Picking_%s.pdf" %(instance.id)
		content = "attachment; filename=%s" %(filename)
		response['Content-Disposition'] = content
		return response

def set_pallet_details(pallet):
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

    # if available_net_weight < 0:
    #     available_net_weight = 0
    # if available_gross_weight < 0:
    #     available_gross_weight = 0
        
    new_total_boxes = inventory.total_boxes - total_boxes

    # if new_total_boxes <=0:
    #     new_total_boxes = 0
    #     available_net_weight  = 0.0
    #     available_gross_weight  = 0.0
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
    if inventory.total_boxes < 0:
        inventory.total_boxes = 0
    if inventory.available_total_boxes < 0:
        inventory.available_total_boxes = 0
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
            inv = entrance_pallet.warehouseinventory_set.first()
            available_total_boxes = 0
            if inv:
                available_total_boxes = inv.available_total_boxes
            if entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.status == 'finish' and available_total_boxes!=0:
                w_stored_weight += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_weight
                w_stored_volume += entrance_pallet.boxes * entrance_pallet.werehouse_entrance_confirmation.product.get_available_volume

    if exit_pallets.exists():
        for exit_pallet in exit_pallets:
            inv = exit_pallet.inventory
            available_total_boxes = 0
            if inv:
               available_total_boxes = inv.available_total_boxes
            if exit_pallet.werehouse_exit_confirmation.werehouse_exit.status == 'finish' and available_total_boxes!=0:
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


def exit_print_picking(request, pk):
	instance = WarehouseExit.objects.get(id=pk)
	return get_print_picking_report(instance)

def get_pallet_detail_for_relocation(request):
  
  pallet_code = request.GET["pallet_code"]
  pallets = WarehouseExitPallet.objects.filter(palet_lot= pallet_code )
  
  if pallets.exists():
    pallet = pallets.first()
    pallet_data = WarehouseExitPalletDetailSerializer(pallet,many=False)
    pallet_data = {'pallet_info': pallet_data.data, 'code': 200 }
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'pallet_info': [], 'code': 500, "pallet_url": "", 'pallet_location_url': ""}
    return JsonResponse(pallet_data, safe=False)

