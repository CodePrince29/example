# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from warehouses.warehouse_exit.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from rest_framework.response import Response
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from  .serializers import WarehouseExitSerializer
from warehouses.warehouse_entrance.models import *
from warehouses.warehouse_exit.models import *
from warehouses.warehouse_exit.models import *
from django.conf import settings
from catalogs.clients.models import Client
from catalogs.product.models import Product
from catalogs.warehouse.models import Warehouse,WarehouseInventory
from django.db.models import Q
from django.db.models import Sum
from warehouses.utils import render_to_pdf
from django.views.generic import View
import json, pdb
from django.http import JsonResponse
import time, os
import datetime, base64
import urllib
from io import StringIO
from django.http import HttpResponse
from django.views.generic import View
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

class InventarioResumidoList(LoginRequiredMixin, ListView):   
    template_name = 'reportes/inventario_resumido/index.html'
    model = WarehouseExit
    fields = ['entrance_date','entrance_hour']
    def get_context_data(self, **kwargs):
	    context = super(InventarioResumidoList, self).get_context_data(**kwargs)
	    context['warehouses'] = Warehouse.objects.all()	
	    context['products'] = Product.objects.all().order_by('product_code')
	    context['customers'] = Client.objects.all().order_by('name')
	    return context

class DownloadInventorySummeryPdfView(LoginRequiredMixin, View):
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(DownloadInventorySummeryPdfView, self).dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		from reportes.utility import GenerateXlsxReport
		from django.core.files import File
		import ast
		if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
			qids = eval(base64.b64decode(request.POST['pdf_ids_list']).decode('ascii', 'ignore'))
			data_html = ""
			summery_html = u"""
			        <tr>
			        	<td style="width:150px; border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{0}</td>
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{1}</td>
			        	<td style="width:230px; border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{2}</td>
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{3}</td>
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{4}</td>
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{5}</td>
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{6}</td>
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{7}</td>                  
			        	<td style="border-bottom: 1px solid #000; padding:20px 5px 5px 0; margin-left:15px;">{8}</td>                  
			        </tr>
			        
			        """
			total_inprocessed_entrance_boxes=0.0
			total_inprocessed_exit_boxes=0.0
			total_inventory_avail_retained_boxes=0
			total_available_quantity=0
			total_quantity=0.0
			total_gross_weight=0
			total_net_weight=0
			for qid in qids:
				for k,i in enumerate(qid):
					if qid[k] =='N/A':
						qid[k] = 0
					if k == 3:
						total_inprocessed_entrance_boxes += qid[k]
					if k == 4:
						total_inprocessed_exit_boxes += qid[k]
					if k == 5:
						total_inventory_avail_retained_boxes += qid[k]
					if k == 6:
						total_available_quantity += qid[k]
					if k == 7:
						total_quantity += qid[k]
					if k == 8:
						total_gross_weight += qid[k]
					if k == 9:
						total_net_weight += qid[k]


				data_html = data_html + summery_html.format(
					checkAsciCode(qid[0]),
					checkAsciCode(qid[1]),
					checkAsciCode(qid[2]),
					qid[3],qid[4],qid[5],
					qid[6],qid[7],qid[8])

			data_html = {'summery_data': data_html,
			'total_inprocessed_entrance_boxes':total_inprocessed_entrance_boxes,
			'total_inprocessed_exit_boxes':total_inprocessed_exit_boxes,
			'total_inventory_avail_retained_boxes':total_inventory_avail_retained_boxes,
			'total_available_quantity':total_available_quantity,
			'total_quantity':total_quantity,
			'total_gross_weight':total_gross_weight,
			'total_net_weight':total_net_weight,
			"print_date": datetime.datetime.now().strftime("%Y/%m/%d")}

			pdf = render_to_pdf('pdf/inventory_summery_pdf.html', data_html)
			if pdf:
				response = HttpResponse(pdf, content_type='application/pdf', status=200)
				filename = "Inventario_Resumido_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
				content = "attachment; filename=%s" %(filename)
				response['Content-Disposition'] = content
				return response
			else:
				return HttpResponse(status=302)
		else:
			return HttpResponse(status=302)

class DownloadInventoryResumidoReportView(LoginRequiredMixin, View):
	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return super(DownloadInventoryResumidoReportView, self).dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		from reportes.utility import GenerateXlsxReport
		from django.core.files import File
		import ast
		if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
			qids = ast.literal_eval(base64.b64decode(request.POST['ids_list']).decode('ascii', 'ignore'))
			column =[

			(u"CLIENTE", 20),
			(u"Código", 15),
			(u"DESCRIPCION DE PRODUCTO", 30),
			(u"EN PREPARACION",20),        
			(u"CANTIDAD RETENIDA", 20),
			(u"CANTIDAD DISPONIBLE", 20),
			(u"CANTIDAD TOTAL", 20),
			(u"Kg Brutos", 20),
			(u"Kg Netos", 20),

			]

			total_inprocessed_entrance_boxes=0.0
			total_inprocessed_exit_boxes=0.0
			total_inventory_avail_retained_boxes=0
			total_available_quantity=0
			total_quantity=0.0
			total_gross_weight=0
			total_net_weight=0

			for qid in qids:
				for k,i in enumerate(qid):
					if qid[k] =='N/A':
						qid[k] = 0
					if k == 3:
						total_inprocessed_entrance_boxes += qid[k]
					if k == 4:
						total_inprocessed_exit_boxes += qid[k]
					if k == 5:
						total_inventory_avail_retained_boxes += qid[k]
					if k == 6:
						total_available_quantity += qid[k]
					if k == 7:
						total_quantity += qid[k]
					if k == 8:
						total_gross_weight += qid[k]
					if k == 9:
						total_net_weight += qid[k]

			reportData = qids
			reportData.append(["","","","","","","","",""])
			reportData.append(["","","Total",total_inprocessed_entrance_boxes,total_inprocessed_exit_boxes,
				total_inventory_avail_retained_boxes,total_available_quantity,total_quantity,total_gross_weight])
			report_name = "Inventario_resumido_%s.xlsx"%datetime.datetime.now().strftime("%Y_%m_%d")
			call = GenerateXlsxReport(report_name, column, reportData,'INVENTARIO RESUMIDO')
			filepath = call.generate()
			with open(filepath, "r") as excel:
				data = excel.read()
			response = HttpResponse(data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', status=200)
			content = "attachment; filename=%s" %(report_name)
			response['Content-Disposition'] = content
			return response
		else:
			return HttpResponse(status=302)

class InventryResumidoFilter(CreateAPIView):
	queryset = WarehouseExit.objects.all()
	serializer_class = WarehouseExitSerializer
	permission_classes = (IsAuthenticated,)
	def post(self, request, *args, **kwargs):
		request_data = self.request.POST
		if request_data.get('client') == 'ALL' or request_data.get('client') == '':
			customers = Client.objects.all()
		else:
			customers = Client.objects.filter(id = request_data.get('client'))

		if request_data.get('warehouse') == 'ALL' or request_data.get('warehouse') == '':
			warehouses = Warehouse.objects.all().values_list('id', flat=True)
		else:
			warehouses = [request_data.get('warehouse')]

		entrance_measurements = WProductMeasurement.objects.filter(werehouse_entrance__status__in=[WarehouseEntrance.PENDING, WarehouseEntrance.IN_RECEIPT, WarehouseEntrance.IN_MANEUVERS,  WarehouseEntrance.MANEUVER_COMPLETE])
		inventries_data = WarehouseInventory.objects.filter(Q(warehouse_location__warehouse_id__in=warehouses))
		exit_measurements = WExitProductMeasurement.objects.filter(werehouse_exit__status__in=[WarehouseExit.IN_MANEUVERS, WarehouseExit.MANEUVER_COMPLETE])
		
		queryset_list = []

		for customer in customers.iterator():
			if request_data.get('product') == 'ALL' or request_data.get('product') == '':
				products = Product.objects.filter(customer_id__in=[customer])
			else:
				products = Product.objects.filter(id =request_data.get('product'))
			for product in products.iterator():
				data = []
				data.append("%s (%s)"%(customer.name, customer.client_code))
				data.append(product.product_code)
				data.append(product.product_description)
				
				entrance_measurement_list = entrance_measurements.filter(product=product, werehouse_entrance__customer=customer)
				exit_measurements_list = exit_measurements.filter(product=product, werehouse_exit__customer=customer)
				entrance_boxes = entrance_measurement_list.values('boxes').aggregate(entrance_boxes=Coalesce(Sum('boxes'), 0))
				exit_boxes = exit_measurements_list.values('boxes').aggregate(exit_boxes=Coalesce(Sum('boxes'), 0))
				exit_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation__exit_product_measurement__in=exit_measurements_list)
				available_weights = 0
				if len(exit_pallets) > 0:
					pallet = exit_pallets.values('gross_weight').aggregate(total_gross_weight=Coalesce(Sum('gross_weight'), 0))
					available_weights = float(pallet['total_gross_weight'])
				else:
					available_weights = 0

				inventries = inventries_data.filter(product=product, client=customer)
				inventory_available_boxes = inventries.values('available_total_boxes').aggregate(available_boxes=Coalesce(Sum('available_total_boxes'), 0))
				inventory_retained_boxes = inventries.values('warehouse_entrance_pallet__retained_quantity').aggregate(retained_boxes=Coalesce(Sum('warehouse_entrance_pallet__retained_quantity'), 0))
				inventory_gross_weight = inventries.values('available_gross_weight').aggregate(total_gross_weight=Coalesce(Sum('available_gross_weight'), 0))
				inventory_net_weight = inventries.values('available_net_weight').aggregate(total_net_weight=Coalesce(Sum('available_net_weight'), 0))
				disposible_boxes = int(inventory_available_boxes.get('available_boxes'))
				
				if (int(exit_boxes.get('exit_boxes')) ==0 and int(disposible_boxes) ==0 and int(inventory_retained_boxes.get('retained_boxes')) ==0):
					pass
				else:
					#EN PREPARACION
					data.append(exit_boxes.get('exit_boxes'))

					#CANTIDAD RETENIDA
					data.append(inventory_retained_boxes.get('retained_boxes'))

					#CANTIDAD DISPONIBLE
					data.append(disposible_boxes)

					#CANTIDAD TOTAL
					inventory_total_boxes = int(disposible_boxes)+int(inventory_retained_boxes.get('retained_boxes')) + int(exit_boxes.get('exit_boxes'))
					data.append(inventory_total_boxes)
					
					#Kg Brutos
					if float(exit_boxes.get('exit_boxes')) > 0:
						data.append(float(inventory_gross_weight.get('total_gross_weight')) + available_weights)
						data.append(float(inventory_net_weight.get('total_net_weight')) + available_weights)
						
					else:
						data.append(inventory_gross_weight.get('total_gross_weight'))
						data.append(inventory_net_weight.get('total_net_weight'))
					
					queryset_list.append(data)
		return Response(queryset_list)

def checkAsciCode(field):
    if field is not None and field!='':
        try: 
            return str(field)
        except UnicodeEncodeError:
            return unicode(field).encode('utf-8')
        except: 
            return ""