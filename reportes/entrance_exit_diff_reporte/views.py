# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
import datetime
# from warehouses.warehouse_entrance.models import WarehouseEntrance, WarehouseEntranceConfirmation
from .forms import  AFQFormSet, AFQFormSetNoExtra, AdvancedFilterFormSet
from django.views.generic import View
import json
from django.http import JsonResponse
from .serializers import WarehouseEntranceSerializer
import time, os, sys
import urllib
from django.http import HttpResponse
from django.conf import settings
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.db.models.signals import pre_save
from catalogs.warehouse.models import Warehouse
import logging
from warehouses.utils import render_to_pdf
from warehouses.warehouse_entrance.models import *
from warehouses.warehouse_exit.models import *
from catalogs.general_params.models import GeneralParams
from django.db.models import Sum, Q
from django.db.models.functions import Cast, Coalesce
from textwrap import wrap
from catalogs.warehouse.models import Warehouse,WarehouseInventory

class EntrancesList(LoginRequiredMixin, ListView):
    template_name = 'reportes/entrance_exit_diff/index.html'
    model = WarehouseEntrance
    queryset = WarehouseEntrance.objects.none()
    def get_context_data(self, **kwargs):
    	context = super(EntrancesList, self).get_context_data(**kwargs)
    	context['formset'] = AFQFormSet
    	return context

class EntranceReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.POST.get('data'))

        data = dict(dd.split("=") for dd in request_data.split("&"))
        query_list = {}
        ordering_val = []
        try:
            for i in range(int(data["form-TOTAL_FORMS"])):
                
                if data["form-{0}-operator".format(i)] == "daterange":
                    qfield = "range"
                    qvalue = urllib.unquote(data["form-{0}-value_from".format(i)]).split("+-+")
                    
                elif data["form-{0}-operator".format(i)] == "timerange":
                    qfield = "icontains"
                    qvalue = urllib.unquote(data["form-{0}-value_from".format(i)])
                elif data["form-{0}-operator".format(i)] in ["istrue","isfalse"]:
                    qfield = ""
                    value = urllib.unquote(data["form-{0}-value".format(i)])
                    
                    if int(value) == 1:
                        qvalue = True
                    elif int(value) == 0:
                        qvalue = False
                    else:
                        qvalue = None

                else:                    
                    qfield = urllib.unquote(data["form-{0}-operator".format(i)])
                    qvalue = urllib.unquote(data["form-{0}-value".format(i)]).replace('+'," ")
                    
                if qfield != "":
                    query_list.update({"{0}__{1}".format(data["form-{0}-field".format(i)], qfield): qvalue })
                else:
                    query_list.update({data["form-{0}-field".format(i)]:qvalue})

                if data["form-{0}-ordering_data".format(i)] == "ascending":
                    q_order = data["form-{0}-field".format(i)]
                    ordering_val.append(q_order)
                elif data["form-{0}-ordering_data".format(i)] == "descending":
                    q_order = data["form-{0}-field".format(i)]
                    ordering_val.append("-"+ q_order)
                               
            queryset = WarehouseEntrance.objects.filter(**query_list).extra(order_by=ordering_val)
            if len(queryset)>0:
                new_data = WarehouseEntranceSerializer(data=queryset, many=True)
                new_data.is_valid()
            else:
                queryset = WarehouseEntrance.objects.none()
                new_data = WarehouseEntranceSerializer(data=queryset)
                new_data.is_valid()
        except:
            queryset = WarehouseEntrance.objects.none()
            new_data = WarehouseEntranceSerializer(data=queryset)
            new_data.is_valid()
        return JsonResponse(new_data.data, safe=False)

class FilterChoicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_data = ()
        foreign_data = kwargs['field'].split('__')
        if foreign_data[0] == "customer":
            field_type = Client._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "wproductmeasurement":
            field_type = WProductMeasurement._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        elif len(foreign_data) > 1 and foreign_data[1] == "warehouseentrancepallet":
            # For palet lot searching
            field_type = WarehouseEntrancePallet._meta.get_field(foreign_data[2]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
            
        elif foreign_data[0] == "warehouseentranceconfirmation":
            field_type = WarehouseEntranceConfirmation._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        elif foreign_data[0] == "wincidenceproduct":
            field_type = WIncidenceProduct._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        elif foreign_data[0] == "carrier":
            field_type = Carrier._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "vehicle":
            field_type = Vehicle._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        
        else:
            field_type = WarehouseEntrance._meta.get_field(kwargs['field']).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

class DownloadEntrancePdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        
        if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
            qids = ast.literal_eval(request.POST['pdf_ids_list'])
            
            warehouses = WarehouseEntrance.objects.filter(id__in=qids)
            entrance_data = [] 
            total_boxes = 0
            total_gross_weight = 0
            total_net_weight = 0 

            html_template_entrance  = """  <tr style="border-top:1px solid #000; padding: 5px 0;">
                    <td valign="top">{client_code}</td>
                    <td valign="top">{product_code}</td>
                    <td valign="top" style="width: 200px;">{product_desc}</td>
                    <td valign="top" >{exp_date}</td>
                    <td valign="top">{cust_lot}</td>
                    <td valign="top">{pallet_lot}</td>
                    <td valign="top">{entrance_kg}</td>
                    <td valign="top">{exit_kg}</td>
                    <td valign="top">{difference}</td>
                    </tr>
                    """
            html_template_entrance_data = ''
            conf_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__w_product_measurement__werehouse_entrance_id__in=qids)
            total_gross_weight = 0
            total_exit_gross_weight = 0
            total_difference = 0
            for pallet in conf_pallets:

                total_exit_weight = WarehouseExitPallet.objects.filter(palet_lot=pallet.palet_lot).values('gross_weight').aggregate(gross_weight=Sum('gross_weight'))['gross_weight']
                if total_exit_weight:
                    difference = pallet.gross_weight - total_exit_weight
                else:
                    total_exit_weight= 0
                    difference = pallet.gross_weight

                total_gross_weight+=pallet.gross_weight
                total_exit_gross_weight+=total_exit_weight
                total_difference+=difference
                measurement = pallet.werehouse_entrance_confirmation.w_product_measurement
                entrance = measurement.werehouse_entrance
                product = measurement.product
                html_template_entrance_data += html_template_entrance.format(
                    client_code= '\n'.join(wrap(checkAsciCode(entrance.customer.name),7)),           
                    product_code= checkAsciCode(product.product_code),
                    product_desc= '\n'.join(wrap(checkAsciCode(product.product_description),7)),
                    exp_date= checkAsciCode(pallet.exp_date),
                    cust_lot= checkAsciCode(pallet.cost_lot),
                    pallet_lot= checkAsciCode(pallet.palet_lot),
                    entrance_kg= checkAsciCode(float(pallet.gross_weight)),
                    exit_kg= checkAsciCode(float(total_exit_weight)),
                    difference= checkAsciCode(float(difference))
                )
            entrance_data_data = {'entrance_data': html_template_entrance_data, "print_date": datetime.datetime.now().strftime("%Y/%m/%d")}
            
            entrance_data_data = {'entrance_data': html_template_entrance_data}
            pdf = render_to_pdf('pdf/entrance_exit_diff_pdf.html', entrance_data_data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Diferencias_Detallado_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(filename):
                    os.system('touch %s'%filename)
                filename = os.path.join(settings.MEDIA_ROOT, "entrance_reports", filename)
                with open(filename, "w") as file:
                    file.write(response.content)
                return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)

class DownloadEntranceReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[
            (u"CLIENTE", 20),
            (u"Código",20),
            (u"DESCRIPCION PRODUCTO", 20),
            (u"CADUCIDAD", 20),
            (u"LOTE CLIENTE", 20),
            (u"LOTE TARIMA", 20),
            (u"CAJAS TOTALES", 20),
            (u"CAJAS DISPONIBLES", 20),
            (u"CAJAS RETENIDAS", 20),
            (u"KILOS DE ENTRADA",20),
            (u"KILOS DE SALIDA",20),
            (u"Diferencia",20)]
            reportData = []
            conf_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__w_product_measurement__werehouse_entrance_id__in=qids)
            total_gross_weight = 0
            total_exit_gross_weight = 0
            total_difference = 0

            for pallet in conf_pallets:
                total_exit_weight = WarehouseExitPallet.objects.filter(palet_lot=pallet.palet_lot).values('gross_weight').aggregate(gross_weight=Sum('gross_weight'))['gross_weight']
                inventory = WarehouseInventory.objects.filter(warehouse_entrance_pallet_id=pallet.id).values('total_boxes', 'retained_boxes', 'available_total_boxes').aggregate(total_boxes=Sum('total_boxes'), retained_boxes=Sum('retained_boxes'), available_total_boxes=Sum('available_total_boxes'))
                if total_exit_weight:
                    difference = pallet.gross_weight - total_exit_weight
                else:
                    total_exit_weight= 0
                    difference = pallet.gross_weight

                total_gross_weight+=pallet.gross_weight
                total_exit_gross_weight+=total_exit_weight
                total_difference+=difference
                measurement = pallet.werehouse_entrance_confirmation.w_product_measurement
                entrance = measurement.werehouse_entrance
                product = measurement.product
                reportData.append([entrance.customer.name,
                product.product_code,
                product.product_description,
                pallet.exp_date,
                pallet.cost_lot,
                pallet.palet_lot,
                inventory["total_boxes"],
                inventory["available_total_boxes"],
                inventory["retained_boxes"],
                pallet.gross_weight,
                total_exit_weight,
                difference
                ])
                           
            reportData.append(["","","","","","",""])
            reportData.append([ "", "","", "", "", "", "", "","Total",total_gross_weight,total_exit_gross_weight,total_difference])
            report_name = "Diferencias_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
            call = GenerateXlsxReport(report_name, column, reportData,'Diferencias Detallado')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            filename = "Diferencias_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "entrance_reports", filename)
            with open(filename, "w") as file:
                file.write(response.content)
            # content = "attachment; filename=%s" %(report_name)
            # response['Content-Disposition'] = content
            return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)
       
        

def checkAsciCode(field):
    if field is not None and field!='':
        try: 
            return str(field)
        except UnicodeEncodeError:
            return unicode(field).encode('utf-8')
        except: 
            return ""

