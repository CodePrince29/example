from django.shortcuts import render
import datetime
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from django.views.generic.list import ListView
from catalogs.warehouse.models import Warehouse, WarehouseLocation ,WarehouseSection, WarehouseTruckBays
from catalogs.clients.models import Client
from catalogs.product.models import Product
from .models import WarehouseEntrance, WarehouseEntranceConfirmation,WarehouseEntrancePallet, WProductMeasurement
from .forms import (WarehouseEntranceForm,
  WProductMeasurementFormSet,
  WWIncidenceProductFormSet,
  WWIncidenceImageFormset,
  WWIncidenceImageEditFormset,
  WarehouseEntranceConfirmationForm,
  WarehouseEntranceConfirmationFormSet,
  WarehouseEntrancePalletFormSet,
  WarehouseEntrancePalletFonfirmForm,
  NewWarehouseEntranceConfirmationForm,
  ConfirmationPMeasurementEditFormSet)
from .forms import (WarehouseEntranceEditForm, WProductMeasurementEditFormSet)


from django.forms import inlineformset_factory
from warehouses.utils import render_to_pdf, render_entrance_pdf
from django.core.urlresolvers import reverse
from catalogs.notifications.models import Notification
from django.utils import timezone
from catalogs.general_params.models import GeneralParams
import pdb
from multiprocessing import Process, Pool
from django.db.models.functions import Cast, Coalesce
from ast import literal_eval
from django.db.models import Sum, Q
class WarehouseEntranceList(LoginRequiredMixin, ListView):
	template_name = 'entrance-list.html'
	model = WarehouseEntrance

	def get_queryset(self):
		queryset = WarehouseEntrance.objects.none()
		if  not self.request.user.get_client:
			queryset = WarehouseEntrance.objects.exclude(status=WarehouseEntrance.FINISH).order_by('-entrance_date')
			return queryset
		else:

			if self.request.user.client_set.exists():

				queryset= self.request.user.client_set.first().warehouseentrance_set.exclude(status=WarehouseEntrance.FINISH).order_by('-entrance_date')
				return queryset	

		return queryset

class NewEntranceView(LoginRequiredMixin,CreateView):
	model = WarehouseEntrance
	form_class = WarehouseEntranceForm

	def get_template_names(self):
		if self.request.user.get_client:
			return "customer_entrance_new.html"
		return "entrance_new.html"

	def reserve_bay(self, data):
		try:
			bay = data.get('bay')
			if bay:
				from django.utils.timezone import get_current_timezone
				from datetime import datetime
				tz = get_current_timezone()
				time_slot = data.get('entrance_date')+" "+data.get('entrance_hour')
				time_slot = tz.localize(datetime.strptime(time_slot, '%Y-%m-%d %I:%M %p'))
				branch = data.get('branch')
				WarehouseTruckBays.objects.create(branch_id=branch,time_slot=time_slot,bay=bay,content_object=self.object)
		except Exception as ex:
			print(ex)

	def get_context_data(self, **kwargs):
		context = super(NewEntranceView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()  

		if self.request.POST:
			context['w_product_measurment_form'] = WProductMeasurementFormSet(self.request.POST, instance=self.object)
			context['w_incidence_product_form'] = WWIncidenceProductFormSet(self.request.POST, instance=self.object)
			context['w_incidence_image_form'] = WWIncidenceImageFormset(self.request.POST,self.request.FILES, instance=self.object)
		else:
			context['w_product_measurment_form'] = WProductMeasurementFormSet(instance=self.object)
			context['w_incidence_product_form'] = WWIncidenceProductFormSet(instance=self.object)
			context['w_incidence_image_form'] = WWIncidenceImageFormset(instance=self.object)
		return context

	def form_valid(self, form):      
		self.object = form.save(commit=False)
		self.object.created_by = self.request.user
		
		context = self.get_context_data()
		w_product_measurment_form = context['w_product_measurment_form']
		w_incidence_product_form = context['w_incidence_product_form']
		w_incidence_image_form = context['w_incidence_image_form']

		if form.is_valid():
			self.object = form.save()
			if self.object.status in ['pending']:
				instance = self.object
				entrance_create_notification_customer(instance)
			w_product_measurment_form.instance = self.object
			w_incidence_product_form.instance = self.object
			w_incidence_image_form.instance = self.object
			if w_product_measurment_form.is_valid():
				try:
					w_product_measurment_form.save()
				except:
					pass
			if w_incidence_product_form.is_valid():
				try:
					w_incidence_product_form.save()
				except:
					pass
			if w_incidence_image_form.is_valid():
				try:
					w_incidence_image_form.save()
				except:
					pass
			self.reserve_bay(self.request.POST)
			if int(self.request.POST.get('save_continue', 0)) == 1:
				return HttpResponseRedirect("confirm-entrance-pallets/%s"%self.object.id )
			# return super(NewEntranceView, self).form_valid(form)
			return HttpResponseRedirect("/warehouse_entrance/warehouse-entrances-list")
		else:
			return HttpResponseRedirect("/warehouse_entrance/warehouse-entrances-list")
			
			# return self.render_to_response(self.get_context_data(form=form))



class UpdateEntranceView(LoginRequiredMixin, UpdateView):
	model = WarehouseEntrance
	template_name = "edit-entrance.html"
	form_class = WarehouseEntranceForm
	
	def get_context_data(self, **kwargs):
		context = super(UpdateEntranceView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()      
		if self.request.POST:
			context['w_product_measurment_form'] = WProductMeasurementFormSet(self.request.POST, instance=self.object)
			context['w_incidence_product_form'] = WWIncidenceProductFormSet(self.request.POST, instance=self.object)
			context['w_incidence_image_form'] = WWIncidenceImageFormset(self.request.POST,self.request.FILES, instance=self.object)
		else:
			context['w_product_measurment_form'] = WProductMeasurementFormSet(instance=self.object)
			context['w_incidence_product_form'] = WWIncidenceProductFormSet(instance=self.object)
			context['w_incidence_image_form'] = WWIncidenceImageEditFormset(instance=self.object)
			context['w_incidence_images'] = self.object.wincidenceimage_set.all()
			context['warehouses'] = Warehouse.objects.all()
			context['locations'] = WarehouseLocation.objects.all()
			context['sections'] = WarehouseSection.objects.all()
		context['warehouse_location'] = [[i.pk, str(i.code)] for i in Warehouse.objects.all()]
		return context

	def form_valid(self, form):      
		self.object = form.save(commit=False)
		# self.object.created_by = self.request.user
		context = self.get_context_data()
		w_product_measurment_form = context['w_product_measurment_form']
		w_incidence_product_form = context['w_incidence_product_form']
		w_incidence_image_form = context['w_incidence_image_form']

		if form.is_valid():
			self.object = form.save()
			
			w_product_measurment_form.instance = self.object
			w_incidence_product_form.instance = self.object
			w_incidence_image_form.instance = self.object
			if w_product_measurment_form.is_valid():
				try:
					p1 = Process(target=self.save_nested_form, args=(w_product_measurment_form,))
				except:
					pass
			if w_incidence_product_form.is_valid():
				try:
					p2 = Process(target=self.save_nested_form, args=(w_incidence_product_form,))
				except:
					pass
			if w_incidence_image_form.is_valid():
				try:
					p3 = Process(target=self.save_nested_form, args=(w_incidence_image_form,))
				except:
					pass

			p1.start()
			p2.start()
			p3.start()
			p1.join()
			p2.join()
			p3.join()
			print("We're done")
			if int(self.request.POST.get('save_continue', 0)) == 1:
				return HttpResponseRedirect("/warehouse_entrance/confirm-entrance-pallets/%s"%self.object.id )
			return HttpResponseRedirect("/warehouse_entrance/warehouse-entrances-list" )
		else:
			return HttpResponseRedirect("/warehouse_entrance/warehouse-entrances-list" )

	
	def save_nested_form(self, form):
		form.save()

class ConfirmSingleEntrancePalletView(LoginRequiredMixin,UpdateView):
	model = WarehouseEntrance
	template_name = "entrance_single_pallet_confirmation.html"
	form_class = WarehouseEntrancePalletFonfirmForm
	def get_context_data(self, **kwargs):
		context = super(ConfirmSingleEntrancePalletView, self).get_context_data(**kwargs)
		warehouse_location = Warehouse.objects.values('id', 'code')
		if self.request.POST:
			context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(self.request.POST, instance=self.object)
		else:
			context['warehouses'] = warehouse_location
			context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(instance=self.object)
			entrance_pallet = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__w_product_measurement_id= int(self.request.GET.get('measurement_id')))
			total_pallet_ids = entrance_pallet.values_list('id', flat=True)
			context['measurement_pallet_ids'] = list(total_pallet_ids)
			context['measurement_id'] = int(self.request.GET.get('measurement_id'))
			product_id = int(self.request.GET.get('product_id', 0))
			product = Product.objects.get(id=product_id)
			measurement_boxes = entrance_pallet.values('boxes').aggregate(total_boxes=Coalesce(Sum('boxes'), 0))
			context['measurement_boxes'] = measurement_boxes["total_boxes"]
			context['product'] = product
		return context

class ConfirmEntrancePalletView(LoginRequiredMixin,UpdateView):
	model = WarehouseEntrance
	template_name = "entrance_pallet_confirmation.html"
	form_class = WarehouseEntrancePalletFonfirmForm
	def get_context_data(self, **kwargs):
		context = super(ConfirmEntrancePalletView, self).get_context_data(**kwargs)
		warehouse_location = Warehouse.objects.values('id', 'code')
		if self.request.POST:
			context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(self.request.POST, instance=self.object)
		else:
			context['warehouses'] = warehouse_location
			context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(instance=self.object)
		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		context = self.get_context_data()
		w_entrance_confirmation_pallet = context['w_entrance_confirmation_pallet']
		w_entrance_confirmation_pallet.instance = self.object
		if w_entrance_confirmation_pallet.is_valid():
			w_entrance_confirmation_pallet.save()
			
		self.object = form.save()
		if self .object.status in ['InManeuvers']:
			instance = self.object
			entrance_create_notification_inmaniobras(instance)
		if self.object.status == "finish":
			ent_conf = self.object.warehouseentranceconfirmation_set.values_list('id',flat=True)
			pallet = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=ent_conf)
			
			data = {
			'object': self.object,
			'print_datetime': self.object.entrance_date, 
			'entrans_id': self.object.id,
			'customer_name': self.object.customer,
			'client_code': self.object.customer.client_code,
			'transportistas': self.object.carrier,
			'transporte': self.object.vehicle,
			'placas': self.object.license_plate,
			'entrance_confirmation': pallet,
			'total_boxe_kgs': self.object.get_total_pallet_boxes_kgs,
			'total_boxes': self.object.get_total_pallet_boxes,
			'total_gross_weight': self.object.get_total_pallet_gross_weight,
			'total_net_weight': self.object.get_total_pallet_net_weight
			}

			pdf = render_to_pdf('pdf/invoice_entrance.html', data)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Entrada_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
				content = "attachment; filename=%s" %(filename)
				response['Content-Disposition'] = content
				return response
		if self.object.status == "pending":
			return HttpResponseRedirect(reverse_lazy('confirm-entrance-pallets', kwargs={'pk': self.object.id}) )
		return HttpResponseRedirect(reverse_lazy('warehouse-entrances-list'))
class NewConfirmEntrancePalletView(LoginRequiredMixin,UpdateView):
	model = WarehouseEntrance
	template_name = "new_entrance_pallet_confirmation.html"
	form_class = WarehouseEntrancePalletFonfirmForm
	def get_context_data(self, **kwargs):
		context = super(NewConfirmEntrancePalletView, self).get_context_data(**kwargs)
		warehouse_location = Warehouse.objects.values('id', 'code')
		product_lists = Product.objects.filter(customer_id=self.object.customer.pk)
		context['product_lists'] = product_lists
		if self.request.POST:
			context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(self.request.POST, instance=self.object)
		else:
			context['warehouses'] = warehouse_location
			context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(instance=self.object)
			entrance_pallet = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance_id= self.object.id)
			pallet_peso_variable = entrance_pallet.values('entrancepalletpesovariable__peso_variable_quantity').aggregate(total_quantity=Coalesce(Sum('entrancepalletpesovariable__peso_variable_quantity'), 0))
			measurement_total_kg = WProductMeasurement.objects.filter(werehouse_entrance_id= self.object.id).values('total_kg').aggregate(measurement_total_kg=Coalesce(Sum('total_kg'), 0))
			total_pallet_ids = entrance_pallet.values_list('id', flat=True)
			context['pallet_peso_variable'] = pallet_peso_variable["total_quantity"]
			context['active_total_kg'] = measurement_total_kg["measurement_total_kg"]
			context['total_pallet_ids'] = list(total_pallet_ids)
			pallet_saved_total_kg = entrance_pallet.values('boxes').aggregate(total_boxes=Coalesce(Sum('boxes'), 0))
			context['total_pallet_boxes'] = pallet_saved_total_kg["total_boxes"]
			context['selected_product'] = self.request.GET.get('selected_product', "")
			context['selected_pallet'] = self.request.GET.get('selected_pallet', "")


			
		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		context = self.get_context_data()
		self.request.POST
		if self.request.POST.get("entrance_button_click") != "true":
			w_entrance_confirmation_pallet = context['w_entrance_confirmation_pallet']
			w_entrance_confirmation_pallet.instance = self.object
			if w_entrance_confirmation_pallet.is_valid():
				w_entrance_confirmation_pallet.save()

		self.object = form.save()
		if self .object.status in ['InManeuvers']:
			instance = self.object
			self.object.sent_to_maniobras_by = self.request.user

			self.object.sent_to_maniobras_at = datetime.datetime.today()
			self.object.save()
			entrance_create_notification_inmaniobras(instance)
			update_measurement_control_detail(instance)
		if self.object.status == "finish":
			ent_conf = self.object.warehouseentranceconfirmation_set.values_list('id',flat=True)
			pallet = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=ent_conf)
			
			data = {
			'object': self.object,
			'print_datetime': self.object.entrance_date, 
			'entrans_id': self.object.id,
			'customer_name': self.object.customer,
			'client_code': self.object.customer.client_code,
			'transportistas': self.object.carrier,
			'transporte': self.object.vehicle,
			'placas': self.object.license_plate,
			'entrance_confirmation': pallet,
			'total_boxe_kgs': self.object.get_total_pallet_boxes_kgs,
			'total_boxes': self.object.get_total_pallet_boxes,
			'total_gross_weight': self.object.get_total_pallet_gross_weight,
			'total_net_weight': self.object.get_total_pallet_net_weight
			}

			pdf = render_to_pdf('pdf/invoice_entrance.html', data)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf')
				filename = "Entrada_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
				content = "attachment; filename=%s" %(filename)
				response['Content-Disposition'] = content
				return response
		return HttpResponseRedirect(reverse_lazy('entrances-list'))

def update_measurement_control_detail(instance):
	measurement_products = WProductMeasurement.objects.filter(werehouse_entrance_id=instance.id)
	for measurement in measurement_products:
		measurement.control_total_boxes = measurement.get_total_palet_boxes()
		measurement.control_total_kg = measurement.get_total_palet_gross_weight()
		measurement.save()

def entrance_create_notification_inmaniobras(instance):
	
	if instance.created_by is not None:
		notification_param_status = 0
		notification_param = GeneralParams.objects.filter(key="EnableInternalNotifications")
		
		if notification_param.exists():
			notification_param_status = notification_param.first().value
		

		if notification_param_status == "1":
			if instance.status == 'InManeuvers':
				if instance.created_by.client_set.all().exists():
					message = "Se ha registrado maniobra de Entrada del cliente : " + instance.created_by.client_set.first().name +" con Folio: " + str(instance.id)
				else:
					message = "Se ha registrado maniobra de Entrada del cliente : " + instance.created_by.username +" con Folio: " + str(instance.id)
				
				Notification.objects.create(content_object=instance,
					occurred_dt=timezone.now(),
					created_by=instance.created_by.id,
					message=message)

def entrance_create_notification_customer(instance):

    
	if instance.created_by is not None:
		
		if instance.created_by.is_staff==False and instance.created_by.role_id==None and instance.status == 'pending':
			if instance.created_by.client_set.all().exists():
				message = "El cliente: " + instance.created_by.client_set.first().name +" ha realizado un registro de Entrada a Almacen."
			else:
				message = "El cliente: " + instance.created_by.username +" ha realizado un registro de Entrada a Almacen."

			Notification.objects.create(
			content_object=instance,
			occurred_dt=timezone.now(),
			created_by=instance.created_by.id,
			message=message
			)


class EntranceList(LoginRequiredMixin, ListView):
	template_name = 'new-entrance-list.html'
	model = WarehouseEntrance

	def get_queryset(self):
		queryset = WarehouseEntrance.objects.none()
		if  not self.request.user.get_client:
			queryset = WarehouseEntrance.objects.exclude(status=WarehouseEntrance.FINISH).order_by('-entrance_date')
			return queryset
		else:

			if self.request.user.client_set.exists():

				queryset= self.request.user.client_set.first().warehouseentrance_set.exclude(status=WarehouseEntrance.FINISH).order_by('-entrance_date')
				return queryset	

		return queryset

class EditEntranceView(LoginRequiredMixin, UpdateView):
	model = WarehouseEntrance
	template_name = "edit-entrance-page.html"
	form_class = WarehouseEntranceEditForm
	
	def get_context_data(self, **kwargs):
		context = super(EditEntranceView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()      
		if self.request.POST:
			context['w_product_measurment_form'] = WProductMeasurementEditFormSet(self.request.POST, instance=self.object)
		else:
			context['w_product_measurment_form'] = WProductMeasurementEditFormSet(instance=self.object)
		return context

	def form_valid(self, form):      
		self.object = form.save(commit=False)
		context = self.get_context_data()
		w_product_measurment_form = context['w_product_measurment_form']
		if form.is_valid():
			self.object = form.save()			
			w_product_measurment_form.instance = self.object

			if w_product_measurment_form.is_valid():
				try:
					w_product_measurment_form.save()
					# p1 = Process(target=self.save_nested_form, args=(w_product_measurment_form,))
				except:
					pass

			# p1.start()
			# p1.join()
			self.save_entrance_control_detail()

			return HttpResponseRedirect("/warehouse_entrance/entrances-list" )
		else:
			return HttpResponseRedirect("/warehouse_entrance/entrances-list" )

	
	def save_nested_form(self, form):
		form.save()

	def save_entrance_control_detail(self):
		entrance = self.object
		measurements = entrance.wproductmeasurement_set.all()
		for measurement in measurements:
			try:
				measurement.control_total_kg = float("{0:.3f}".format(float(measurement.total_kg)))
				measurement.control_total_boxes = measurement.boxes
				measurement.save()
			except:
				measurement.control_total_kg = 0
				measurement.control_total_boxes = 0
				measurement.save()
class EntranceNewView(LoginRequiredMixin,CreateView):
	model = WarehouseEntrance
	template_name = "new_entrance.html"
	form_class = WarehouseEntranceEditForm
	
	def get_context_data(self, **kwargs):
		context = super(EntranceNewView, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()      
		if self.request.POST:
			context['w_product_measurment_form'] = WProductMeasurementEditFormSet(self.request.POST, instance=self.object)
		else:
			context['w_product_measurment_form'] = WProductMeasurementEditFormSet(instance=self.object)
		return context

	def form_valid(self, form):      
		self.object = form.save(commit=False)
		self.object.created_by = self.request.user
		context = self.get_context_data()
		w_product_measurment_form = context['w_product_measurment_form']
		if form.is_valid():
			self.object = form.save()			
			w_product_measurment_form.instance = self.object

			if w_product_measurment_form.is_valid():
				try:
					w_product_measurment_form.save()
					# p1 = Process(target=self.save_nested_form, args=(w_product_measurment_form,))
				except:
					pass
			# p1.start()
			
			# p1.join()
			self.save_entrance_control_detail()

			return HttpResponseRedirect("/warehouse_entrance/entrances-list" )
		else:
			return HttpResponseRedirect("/warehouse_entrance/entrances-list" )

	
	def save_nested_form(self, form):
		form.save()
	def save_entrance_control_detail(self):
		entrance = self.object
		measurements = entrance.wproductmeasurement_set.all()
		for measurement in measurements:
			try:
				measurement.control_total_kg = float("{0:.3f}".format(float(measurement.total_kg)))
				measurement.control_total_boxes = measurement.boxes
				measurement.save()
			except:
				measurement.control_total_kg = 0
				measurement.control_total_boxes = 0
				measurement.save()

class NewEntranceConfirmation(LoginRequiredMixin, UpdateView):
	model = WarehouseEntrance
	template_name = "new-entrance-confirmation.html"
	form_class = NewWarehouseEntranceConfirmationForm
	
	def get_context_data(self, **kwargs):
		context = super(NewEntranceConfirmation, self).get_context_data(**kwargs)
		if self.request.user.is_staff:
			context['customers']  = Client.objects.all()
		else:
			context['customers']  = self.request.user.client_set.all()      
		if self.request.POST:
			context['w_product_measurment_form'] = ConfirmationPMeasurementEditFormSet(self.request.POST, instance=self.object)
			context['w_incidence_product_form'] = WWIncidenceProductFormSet(self.request.POST, instance=self.object)
			context['w_incidence_image_form'] = WWIncidenceImageFormset(self.request.POST,self.request.FILES, instance=self.object)
		else:
			context['w_product_measurment_form'] = ConfirmationPMeasurementEditFormSet(instance=self.object)
			context['w_incidence_product_form'] = WWIncidenceProductFormSet(instance=self.object)
			context['w_incidence_image_form'] = WWIncidenceImageEditFormset(instance=self.object)
			context['w_incidence_images'] = self.object.wincidenceimage_set.all()
			context['warehouses'] = Warehouse.objects.all()
			context['locations'] = WarehouseLocation.objects.all()
			context['sections'] = WarehouseSection.objects.all()
		context['warehouse_location'] = [[i.pk, str(i.code)] for i in Warehouse.objects.all()]
		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		# self.object.created_by = self.request.user
		context = self.get_context_data()
		w_product_measurment_form = context['w_product_measurment_form']
		w_incidence_product_form = context['w_incidence_product_form']
		w_incidence_image_form = context['w_incidence_image_form']

		if form.is_valid():
			self.object = form.save()
			
			w_product_measurment_form.instance = self.object
			w_incidence_product_form.instance = self.object
			w_incidence_image_form.instance = self.object
			if w_product_measurment_form.is_valid():
				try:
					p1 = Process(target=self.save_nested_form, args=(w_product_measurment_form,))
				except:
					pass
			if w_incidence_product_form.is_valid():
				try:
					p2 = Process(target=self.save_nested_form, args=(w_incidence_product_form,))
				except:
					pass
			if w_incidence_image_form.is_valid():
				try:
					p3 = Process(target=self.save_nested_form, args=(w_incidence_image_form,))
				except:
					pass

			p1.start()
			p2.start()
			p3.start()
			p1.join()
			p2.join()
			p3.join()
			print("We're done")
			if self.object.status == "InManeuvers":
				measurement_products = WProductMeasurement.objects.filter(werehouse_entrance_id=self.object.id)
				for measurement in measurement_products:
					measurement.control_total_boxes = measurement.get_total_palet_boxes()
					measurement.control_total_kg = measurement.get_total_palet_gross_weight()
					measurement.save()

			elif self.object.status == "finish":
				from django.utils import timezone
				import pytz
				timezone.activate(pytz.timezone("America/Mexico_City"))
				self.object.confirmed_at = timezone.localtime(timezone.now())
				self.object.confirmed_by = self.request.user
				
				self.object.save()
				ent_conf = self.object.warehouseentranceconfirmation_set.values_list('id',flat=True)
				measurement_products = WProductMeasurement.objects.filter(werehouse_entrance_id=self.object.id)
				
				data = {
				'object': self.object,
				'print_datetime': self.object.confirmed_at, 
				'print_entrance_hour': self.object.entrance_hour, 
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

				pdf = render_entrance_pdf('pdf/new_invoice_entrance.html', data)
				if pdf:
					response = HttpResponse(pdf, content_type='application/pdf')
					filename = "Entrada_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
					content = "attachment; filename=%s" %(filename)
					response['Content-Disposition'] = content
					return response
			return HttpResponseRedirect("/warehouse_entrance/entrances-list" )
		else:
			return HttpResponseRedirect("/warehouse_entrance/entrances-list" )

	
	def save_nested_form(self, form):
		form.save()

