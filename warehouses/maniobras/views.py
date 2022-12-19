# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from warehouses.warehouse_entrance.models import WarehouseEntrance, WarehouseEntrancePallet, PalletConsolidate
from warehouses.warehouse_exit.models import WarehouseExit, WarehouseExitPallet
from .entrance_forms import WarehouseEntrancePalletFormSet,WarehouseEntrance1FormSet
from .exit_forms import WarehouseExitPalletFormSet,WarehouseExitFormSet1
from catalogs.warehouse.models import Warehouse, WarehouseLocation,WarehouseInventory
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView,CreateAPIView
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from .models import *
import time,os
import urllib, ast
from django.http import HttpResponse
import datetime, pdb
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from warehouses.warehouse_exit.api.serializers import ExitPalletMenuoverSerializer,WarehouseExitConfirmationPalletSerializer
from warehouses.warehouse_entrance.api.serializers import EntrancePalletSerializer,EntrancePalletMenuoverSerializer,WarehouseEntranceConfirmation1Serializer, WarehouseEntrancePalletSerializer
from catalogs.notifications.models import Notification
from django.utils import timezone
from warehouses.utils import render_to_pdf
from django.conf import settings
import json
from catalogs.general_params.models import GeneralParams

class EntrancesList(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/entrance_list.html'
	model = WarehouseEntrance
	def get_queryset(self):
		queryset = WarehouseEntrance.objects.filter(status__in=[WarehouseEntrance.IN_MANEUVERS, WarehouseEntrance.MANEUVER_COMPLETE])
		return queryset

class ExitList(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/exit_list.html'
	model = WarehouseExit
	def get_queryset(self):
		queryset = WarehouseExit.objects.filter(status__in=[WarehouseExit.IN_MANEUVERS, WarehouseEntrance.MANEUVER_COMPLETE])
		return queryset


class EntrancesUpdateView(LoginRequiredMixin, UpdateView):
	template_name = 'warehouse/maniobras/entrance_update.html'
	model = WarehouseEntrance
	form_class = WarehouseEntrance1FormSet
	def get_context_data(self, **kwargs):
		context = super(EntrancesUpdateView, self).get_context_data(**kwargs)
		if self.request.POST:
			confirmations = self.object.warehouseentranceconfirmation_set.all().order_by('id')
			pallets = WarehouseEntranceConfirmation1Serializer(confirmations,many=True).data
			context['w_entrance'] = WarehouseEntrance1FormSet(instance=self.object)
			context['confirmations'] = pallets
			# context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(self.request.POST, instance=self.object)
		else:
			confirmations = self.object.warehouseentranceconfirmation_set.all().order_by('id')
			pallets = WarehouseEntranceConfirmation1Serializer(confirmations,many=True).data
			context['w_entrance'] = WarehouseEntrance1FormSet(instance=self.object)
			context['confirmations'] = pallets

			# context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(instance=self.object)
		return context

	def form_valid(self, form):      
		self.object = WarehouseEntrance.objects.filter(pk=self.kwargs['pk'])
		if self.object.exists():
			object1 = self.object.first()
			object1.status = form.data['status']
			object1.save()
			if object1.status in ['ManeuverComplete']:
				entrance_create_notification_maniobras_complete(object1)
		return HttpResponseRedirect(reverse('maniobras-entrance-list'))

def entrance_create_notification_maniobras_complete(instance):
	if instance.created_by is not None:
		notification_param_status = 0
		notification_param = GeneralParams.objects.filter(key="EnableInternalNotifications")

		if notification_param.exists():
			notification_param_status = notification_param.first().value

		if notification_param_status == "1":
			if instance.status == 'ManeuverComplete' :
				
				message = "La maniobra de Entrada con folio: " + str(instance.id) +" ha concluido."
				print("exit")
				Notification.objects.create(content_object=instance,occurred_dt=timezone.now(),created_by=instance.created_by.id,message=message)
		


class InventoryTakingView(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/inventory_taking_list.html'
	model = TakingInventory
	def get_queryset(self):
		queryset = TakingInventory.objects.all()
		return queryset

class CreateInventoryTakingView(LoginRequiredMixin, CreateView):
	template_name = 'warehouse/maniobras/add-inventory-taking.html'
	model = TakingInventory
	fields='__all__'
	def get_context_data(self, **kwargs):
		context = super(CreateInventoryTakingView, self).get_context_data(**kwargs)
		context['pallet_lists']  = WarehouseEntrancePallet.objects.all()
		return context

class UpdateInventoryTakingView(LoginRequiredMixin, UpdateView):
	template_name = 'warehouse/maniobras/update-inventory-taking.html'
	model = TakingInventory
	fields='__all__'
	def get_context_data(self, **kwargs):
		context = super(UpdateInventoryTakingView, self).get_context_data(**kwargs)
		context['pallet_lists']  = WarehouseEntrancePallet.objects.values('id', 'palet_lot')
		return context

class ShowInventoryTakingView(LoginRequiredMixin, UpdateView):
	template_name = 'warehouse/maniobras/show-inventory-taking.html'
	model = TakingInventory
	fields='__all__'	

class PalletConsultView(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/pallet_consult_list.html'
	model = WarehouseInventory
	def get_queryset(self):
		queryset = WarehouseInventory.objects.all()
		return queryset
 
class PalletReprintView(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/pallet_reprint.html'
	model = WarehouseInventory

class WarehousePaletListQrcode(ListView):
    model = WarehouseEntrancePallet
    queryset = WarehouseEntrancePallet.objects.all()    
    template_name = 'pdf/warehouse_qrcode_pdf.html'
    
    def get(self, request):
        from sga.render import Render
        printed_data = self.request.GET['printed_data'].encode('utf-8')
	printed_data = printed_data.split(',')
        query_set = WarehouseEntrancePallet.objects.filter(id__in=printed_data)
        params = {
        'object_list': query_set            
        }
        return Render.render('pdf/entrance_qrcode_pdf.html',
       params)

@csrf_exempt
def pallet_information_list(request):
	try:
		customer = request.POST.get('customer',False)
		lote_tarima = request.POST.get('lote_tarima', False)
		entrance = request.POST.get('entrance', False)

		query_list = {}
		if customer:
			query_list.update({"werehouse_entrance_confirmation__werehouse_entrance__customer_id": customer})  	
		if lote_tarima:
			query_list.update({"palet_lot__iexact": lote_tarima})
		if entrance:
			query_list.update({"werehouse_entrance_confirmation__werehouse_entrance_id": entrance})

		entrance_pallet = WarehouseEntrancePallet.objects.filter(**query_list)
		pallets = EntrancePalletSerializer(entrance_pallet,many=True)  
		pallet_data = {'pallet_info': pallets.data, 'code': 200}
		return JsonResponse(pallet_data, safe=True)
	except:
		pallet_data = {'pallet_info': [], 'code': 500}
		return JsonResponse(pallet_data, safe=True)

@csrf_exempt
def update_pallet_note(request):
	try:
		pallet = WarehouseEntrancePallet.objects.get(pk=request.POST.get('pallet'))
		# GGV Add the physical inventory taking found in the notes kg and total boxes found in physical
		pallet.note = request.POST.get('note') + "\n Cajas Fisico:" + str(request.POST.get('total_boxes')) + "\n Kg Fisico:" + str(request.POST.get('total_kg'))
		pallet.save()
		inv = pallet.warehouseinventory_set.first()
		# GGV We will not update inventory here 
                # inv.total_boxes = request.POST.get('total_boxes')
		# inv.total_kg = request.POST.get('total_kg') 
		inv.save()
		return JsonResponse({'code': 200, 'message': 'Success'}, safe=True)
	except Exception as ex:
		return JsonResponse({'code': 500, 'message': str(ex)}, safe=True)

		
class ReportInventoryTakingView(LoginRequiredMixin, View):
	def get(self, request, *args, **kwargs):
		from reportes.utility import GenerateXlsxReport
		from django.core.files import File
		import ast
		qids = kwargs['pk']
		column =[
			(u"LOTE TARIMA", 20),
			(u"CLIENTE", 40),
			(u"CODIGO", 20),
			(u"PRODUCTO",20),
			(u"CADUCIDAD", 20),
			(u"LOTE CLIENTE", 15),
			(u"ALMACEN", 15),
			(u"RACK", 15),
			(u"NIVEL", 15),# + Rack level Location of pallet
			(u"UBICACION", 20),
			(u"KILOS NETOS SISTEMA", 20), # + Net weight in system
			(u"KILOS NETOS FISICO", 20), # + Physical Kg entered in inventory taking option
			(u"CAJAS SISTEMA", 20), # + Boxes in system
			(u"CAJAS FISICO", 20), #+ Physical entered in inventory taking option
			(u"CAJAS DIFERENCIA", 20), #+ net weight in boxes (cM-cN)
			(u"KILOS DIFERENCIA", 20), # + net weight in boxes (cK-cL)
			(u"KILOS BRUTOS", 20),
			(u"OBSERVACION REGISTRADA", 20),
		]


		total_boxes = 0
		total_net_weight = 0
		reportData = []
		obj = TakingInventory.objects.get(id=qids)
		pallets = obj.warehouseentrancepallet.all()
		print(pallets)
		if pallets.exists():
			for pallet in pallets.iterator():
				inventories = pallet.warehouseinventory_set.all()
				height_level=0
				if pallet.location and pallet.location.warehousedepthlevel_set.exists():
					height_level = pallet.location.warehousedepthlevel_set.first().height.description


				inv_net_weight = 0
				inv_total_boxes = 0
				inv_total_kg = 0
				available_total_boxes = 0
				defference = 0

				if inventories.exists():
					#GGV
					inv = inventories.first()
					inv_net_weight = inv.available_net_weight
					inv_total_boxes = inv.total_boxes
					available_total_boxes=inv.available_total_boxes
					#defference=inv.available_total_boxes-inv.total_boxes
					defference=inv.total_boxes - inv.available_total_boxes
					inv_total_kg = float(inv.total_kg)
					total_boxes+= inv.total_boxes
					total_net_weight+= inv.available_net_weight
					#net_weight_kg = float(pallet.net_weight) - inv_total_kg
					net_weight_kg = inv_total_kg - float(pallet.net_weight)
	
				reportData.append([
					pallet.palet_lot,
					obj.customer.name,
					pallet.werehouse_entrance_confirmation.product.product_code,
					pallet.werehouse_entrance_confirmation.product.product_description,
					pallet.exp_date,
					pallet.cost_lot,
					pallet.warehouse.code,
					pallet.rack_number.index,
					height_level,
					pallet.location.location_number,
					pallet.net_weight,
					inv_total_kg,
					available_total_boxes,
					inv_total_boxes,
					defference,
					net_weight_kg,
					inv_net_weight,
					pallet.note,
				])
				print("------------")

		if len(reportData) != 0:
			reportData.append(["","","","","","","","","","","","","","","","","",""])
			reportData.append(["","","","","","","","","","","","","","","","","",""])
			reportData.append(["","","","","","","","","","","","","",total_boxes,"","",total_net_weight])

		report_name = "Toma_inventario_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
		call = GenerateXlsxReport(report_name, column, reportData,'TOMA INVENTARIO')
		filename = call.generate()
		f = open(filename, 'rb')
		excelfile = File(f)

		response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
		content = "attachment; filename=%s" %(report_name)
		response['Content-Disposition'] = content
		return response
				
class ExitUpdateView(LoginRequiredMixin, UpdateView):
	template_name = 'warehouse/maniobras/exit_update.html'
	model = WarehouseExit
	form_class = WarehouseExitFormSet1
	def get_context_data(self, **kwargs):
		context = super(ExitUpdateView, self).get_context_data(**kwargs)
		if self.request.POST:
			confirmations = self.object.wexitconfirmation_set.all().order_by('id')
			pallets = WarehouseExitConfirmationPalletSerializer(confirmations,many=True).data
			context['w_exit'] = WarehouseExitFormSet1(instance=self.object)
			context['exit_confirmations'] = pallets
		else:
			confirmations = self.object.wexitconfirmation_set.all().order_by('id')
			
			pallets = WarehouseExitConfirmationPalletSerializer(confirmations,many=True).data
			context['w_exit'] = WarehouseExitFormSet1(instance=self.object)
			context['exit_confirmations'] = pallets
		return context

	def form_valid(self, form):      
		self.object = WarehouseExit.objects.filter(pk=self.kwargs['pk'])
		if self.object.exists():
			object1 = self.object.first()
			object1.status = form.data['status']
			object1.save()
			if object1.status in ['ManeuverComplete']:
				exit_create_notification_maniobras_complete(object1)
		return HttpResponseRedirect(reverse('maniobras-exit-list'))

def exit_create_notification_maniobras_complete(instance):
	if instance.created_by is not None:
		
		notification_param_status = 0
		notification_param = GeneralParams.objects.filter(key="EnableInternalNotifications")

		if notification_param.exists():
			notification_param_status = notification_param.first().value
		if notification_param_status == "1":

			if instance.status == 'ManeuverComplete' :
				
				message = "La maniobra de Salida con folio: " + str(instance.id) +" ha concluido."
				print("exit")
				Notification.objects.create(content_object=instance,occurred_dt=timezone.now(),created_by=instance.created_by.id,message=message)
		

class ConfirmEntrancePallet(LoginRequiredMixin, View):
	def get(self, request, *args, **kwargs):
		print(kwargs.get('pk'))
		pallet = WarehouseEntrancePallet.objects.get(pk=kwargs.get('pk'))
		pallet.confirmed = True
		pallet.save()
		werehouse_entrance = pallet.werehouse_entrance_confirmation.werehouse_entrance
		if werehouse_entrance.status == "InManeuvers":
			pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance_id= werehouse_entrance.id)
			confirmed_pallet = pallets.filter(confirmed=True)
			if len(pallets) == len(confirmed_pallet):
				werehouse_entrance.status = "ManeuverComplete"
				werehouse_entrance.save()
		return JsonResponse({"message":"Confirmed" , "code": 200}, status=200)


class ConfirmExitPallet(LoginRequiredMixin, View):
	def get(self, request, *args, **kwargs):
		pallet = WarehouseExitPallet.objects.get(pk=kwargs.get('pk'))
		pallet.confirmed = True
		pallet.save()
		return JsonResponse({"message":"Confirmed" , "code": 200},status=200)

class DownloadComparisonPdfView(LoginRequiredMixin, View):
	def post(self, request, *args, **kwargs):
		qids = json.loads(request.POST.get('inv_id'))
		inventories = []
		results  = TakingInventory.objects.filter(id=qids)
		if results.exists():
			obj = results.first()
			customer_name = obj.customer.name
			taking_inventory_date = obj.taking_date
			taking_inventory_time = obj.taking_hour
			for pallet in obj.warehouseentrancepallet.all():
				inventory = pallet.warehouseinventory_set.first()
				total_boxes=0
				available_total_boxes=0
				defference=0
				if inventory:
					total_boxes=inventory.total_boxes
					available_total_boxes=inventory.available_total_boxes
					defference=inventory.available_total_boxes-inventory.total_boxes
				        #defference=inventory.total_boxes-inventory.available_total_boxes
			        data= {
				'product_code':pallet.werehouse_entrance_confirmation.product.product_code,
				'product_description':pallet.werehouse_entrance_confirmation.product.product_description,
				'cost_lot':pallet.cost_lot,
				'pallet_id':pallet.palet_lot,
				'exp_date':pallet.exp_date,
				'total_boxes':total_boxes,
				'available_total_boxes':available_total_boxes,
				'defference':defference,
				}
				inventories.append(data)
			TakingInventory.objects.filter(id=qids)
		inventory_data = {'inventory_data': inventories,'customer_name':customer_name,'taking_inventory_date':taking_inventory_date,
			'taking_inventory_time':taking_inventory_time,
			"print_date": datetime.datetime.now().strftime("%Y/%m/%d")}
			
		pdf = render_to_pdf('pdf/inventory_comparison_pdf.html', inventory_data)
		if pdf:
			response = HttpResponse(pdf, content_type='application/pdf')
			filename = "ReporteComparativo_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
			
			file_path = os.path.join(settings.MEDIA_ROOT, "inventory_comparison_reports", filename)
			if not os.path.exists(file_path):
				os.system('touch %s'%file_path)
				
			with open(file_path, "w") as file:
				file.write(response.content)
			return JsonResponse({"message": "success","code":200, "file":file_path.split('/media')[-1]}, safe=False)
		else:
			return JsonResponse({"message": "fail","code":500}, safe=False)



class InventoryPesoVariableSerializer(serializers.ModelSerializer):
	class Meta:
		model = InventoryPesoVariable
		fields = ('id', 'peso_variable_quantity','werehouse_entrance_pallet',)


def get_pallet_peso_variable(request,pk):
  pallet_peso_variable = InventoryPesoVariable.objects.filter(werehouse_entrance_pallet_id=pk).order_by('-id')
  if pallet_peso_variable.exists():
    peso_variable = InventoryPesoVariableSerializer(pallet_peso_variable,many=True)  
    return JsonResponse({'data': peso_variable.data, 'code': 200}, safe=True)
  else:
    return JsonResponse({'data': [], 'code':500}, safe=True)

@csrf_exempt
def save_inventory_romaneo_peso_variables(request, pk):
	try:
		request_data = ast.literal_eval(request.POST.get('data'))
		pallet_peso_variable = WarehouseEntrancePallet.objects.get(id=pk).inventorypesovariable_set.values_list('id', flat=True)
		new_peso_variable = [{"werehouse_entrance_pallet":item.get('werehouse_entrance_pallet'), "peso_variable_quantity": item.get('peso_variable_quantity')} for item in request_data if item.get('id') == '']
		request_ids = [int(item.get('id')) for item in request_data if item.get('id') != '']
		if len(request_ids) > 0:
		  deletable_ids = list(set(pallet_peso_variable)-set(request_ids))
		  InventoryPesoVariable.objects.filter(id__in=deletable_ids).delete()

		queryset = InventoryPesoVariable.objects.filter(id__in=request_ids)
		# Update existing peso variable
		for obj in queryset:
		  obj.peso_variable_quantity = [item.get('peso_variable_quantity') for item in request_data if str(obj.id) == item.get('id')][0]
		  obj.save()

		# Create new peso variable
		serializer = InventoryPesoVariableSerializer(data=new_peso_variable, many=True)
		serializer.is_valid()
		serializer.save()

		return JsonResponse({'code': 200, 'message': 'Detalles variables de peso de pallet actualizados.'}, safe=True)
	except Exception as ex:
		print(ex)
		return JsonResponse({'code': 500, 'message': 'Error al actualizar los detalles de la variable de peso de paleta.'}, safe=True)

class MeoverasEntrancesList(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/new_entrance_list.html'
	model = WarehouseEntrance
	def get_queryset(self):
		queryset = WarehouseEntrance.objects.filter(status__in=[WarehouseEntrance.IN_RECEIPT, WarehouseEntrance.IN_MANEUVERS, WarehouseEntrance.MANEUVER_COMPLETE])
		return queryset

class NewEntrancesUpdateView(LoginRequiredMixin, UpdateView):
	template_name = 'warehouse/maniobras/entrance_edit.html'
	model = WarehouseEntrance
	form_class = WarehouseEntrance1FormSet
	def get_context_data(self, **kwargs):
		context = super(NewEntrancesUpdateView, self).get_context_data(**kwargs)
		warehouses = Warehouse.objects.all()
		from catalogs.general_params.models import GeneralParams
		qr_enables = GeneralParams.objects.filter(key="QR_Read", value=1).exists()
		context["warehouses"] = warehouses
		context["qr_enables"] = qr_enables
		return context

class MeoverasExitList(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/new_exit_list.html'
	model = WarehouseExit
	def get_queryset(self):
		queryset = WarehouseExit.objects.filter(status__in=[WarehouseExit.IN_MANEUVERS, WarehouseExit.MANEUVER_COMPLETE])
		return queryset

class NewExitUpdateView(LoginRequiredMixin, UpdateView):
	template_name = 'warehouse/maniobras/exit_edit.html'
	model = WarehouseExit
	form_class = WarehouseEntrance1FormSet
	def get_context_data(self, **kwargs):
		context = super(NewExitUpdateView, self).get_context_data(**kwargs)
		warehouses = Warehouse.objects.all()
		from catalogs.general_params.models import GeneralParams
		qr_enables = GeneralParams.objects.filter(key="QR_Read", value=1).exists()
		context["warehouses"] = warehouses
		context["qr_enables"] = qr_enables
		return context

class NewPallletConsilated(LoginRequiredMixin, ListView):
	template_name = 'warehouse/maniobras/new_pallet_consilated.html'
	model = PalletConsolidate
	def get_context_data(self, **kwargs):
		context = super(NewPallletConsilated, self).get_context_data(**kwargs)
		return context


@csrf_exempt
def get_inventory_detail(request):
	try:
		pallets = WarehouseEntrancePallet.objects.filter(palet_lot=request.GET.get('pallet'))
		if pallets.exists():
			pallet = pallets.first()
			pallet_data = WarehouseEntrancePalletSerializer(pallet, many=False)
			return JsonResponse({'code': 200, 'message': 'Success', 'pallet': pallet_data.data }, safe=True)
		else:
			return JsonResponse({'code': 500, 'message': 'Success', 'pallet': []}, safe=True)
	except Exception as ex:
		return JsonResponse({'code': 500, 'message': str(ex), 'pallet': []}, safe=True)

@csrf_exempt
def save_consolidate(request):
	try:
		remarks = request.POST.get('remarks', "")
		destination_inv_id = request.POST.get('destination_inv_id', "")
		source_inv_id = request.POST.get('source_inv_id', "")
		destination_inv = WarehouseInventory.objects.get(id= destination_inv_id)
		source_inv = WarehouseInventory.objects.get(id= source_inv_id)
		source_pallet = source_inv.warehouse_entrance_pallet.palet_lot
		destination_pallet = destination_inv.warehouse_entrance_pallet.palet_lot
		source_boxes = source_inv.total_boxes
		destination_boxes = destination_inv.total_boxes
		destination_total_kg = destination_inv.total_kg	
		source_total_kg = source_inv.total_kg		
		available_total_boxes = source_inv.available_total_boxes
		source_weight = source_inv.available_gross_weight
		source_net_weight = source_inv.available_net_weight
		destination_weight = destination_inv.available_gross_weight
		destination_net_weight = destination_inv.available_net_weight
		source_inv.total_boxes -= source_boxes
		source_inv.available_gross_weight -= source_weight
		source_inv.available_net_weight -= source_net_weight
		source_inv.total_kg -= source_total_kg	
		source_inv.available_total_boxes -= available_total_boxes
		source_inv.save()
		destination_inv.total_boxes += source_boxes
		destination_inv.available_gross_weight += source_weight
		destination_inv.available_net_weight += source_net_weight
		destination_inv.total_kg += source_total_kg
		destination_inv.available_total_boxes += available_total_boxes
		destination_inv.save()
		PalletConsolidate.objects.create(
			source_pallet = source_pallet,
			destination_pallet = destination_pallet,
			source_inventory_id = source_inv_id,
			destination_inventory_id = destination_inv_id,
			source_boxes = source_boxes,
			source_weight = source_weight,
			destination_boxes = destination_boxes,
			destination_weight = destination_weight,
			reason = remarks
			)
		return JsonResponse({'code': 200, 'message': "success"}, safe=True)

	except Exception as ex:
		return JsonResponse({'code': 500, 'message': str(ex)}, safe=True)

