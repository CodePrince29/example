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
import time, os
import urllib
from django.http import HttpResponse
from warehouses.warehouse_entrance.models import *
from django.conf import settings
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.db.models.signals import pre_save
from catalogs.warehouse.models import Warehouse
import logging
from warehouses.utils import render_to_pdf


class EntrancesResumidoList(LoginRequiredMixin, ListView):
    template_name = 'reportes/entradas_resumido/index.html'
    model = WarehouseEntrance
    queryset = WarehouseEntrance.objects.none()
    def get_context_data(self, **kwargs):
        context = super(EntrancesResumidoList, self).get_context_data(**kwargs)
        context['formset'] = AFQFormSet
        return context

class EntranceResumidoReportView(LoginRequiredMixin, View):
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

class FilterResumidoChoicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_data = ()
        foreign_data = kwargs['field'].split('__')

        if foreign_data[0] == "customer":
            field_type = Client._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "wproductmeasurement":
            field_type = WProductMeasurement._meta.get_field(foreign_data[1]).get_internal_type()
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
        
class DownloadEntranceResumidoReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[

            (u"CLIENTE", 20),
            (u"FECHA DE RECIBO", 15),
            (u"NUMERO DE RECIBO", 15),
            (u"NUM DOCTO CLIENTE", 20),
            (u"Código",20),
            (u"DESCRIPCION PRODUCTO", 20),
            (u"CANTIDAD RECIBIDA", 20),
            (u"PESO BRUTO", 20),
            (u"PESO NETO", 20)
            ]
            reportData = []
            total_boxes=0
            total_net_weight=0
            total_gross_weight=0
            for obj in WarehouseEntrance.objects.filter(id__in=qids):
                exists = True
                if obj.warehouseentranceconfirmation_set.all().exists():
                    conf_id = obj.warehouseentranceconfirmation_set.all().values_list('id',flat=True)
                    conf_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=conf_id)
                    for pallet in conf_pallets:
                        total_boxes += float(pallet.boxes)
                        total_net_weight +=float(pallet.net_weight)
                        total_gross_weight +=float(pallet.gross_weight)
                        if exists:                        
                            reportData.append([                        
                            obj.customer.client_code,
                            obj.entrance_date.strftime("%d-%m-%y"),
                            obj.pk,                        
                            obj.cust_reference,
                            pallet.werehouse_entrance_confirmation.code,
                            pallet.werehouse_entrance_confirmation.product.product_description,
                            pallet.boxes,
                            float(pallet.gross_weight),
                            float(pallet.net_weight)])
                            # exists = False
                        else:
                            reportData.append(["","","","",
                                pallet.werehouse_entrance_confirmation.code,
                                pallet.werehouse_entrance_confirmation.product.product_description,
                                pallet.boxes,
                                float(pallet.gross_weight),
                                float(pallet.net_weight)])
                else:
                    reportData.append([
                            obj.customer.client_code,
                            obj.entrance_date.strftime("%d-%m-%y"),
                            obj.pk,                        
                            obj.cust_reference,
                            "N/A","N/A","N/A","N/A","N/A"])
            if len(reportData) != 0:
                reportData.append(["","","","","","","","",""])
                reportData.append(["","","","","","","","",""])
                reportData.append(["","","","","","","TOTAL:%s"%(total_boxes),"TOTAL:%s"%(total_gross_weight),"TOTAL:%s"%(total_net_weight)])
            report_name = "Entradas_resumido_%s.xlsx"%datetime.datetime.now().strftime("%Y_%m_%d")
            call = GenerateXlsxReport(report_name, column, reportData,'ENTRADAS RESUMIDO')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "Entradas_resumido_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "entrance_resume_reports", filename)
            with open(filename, "w") as file:
                file.write(response.content)
            # content = "attachment; filename=%s" %(report_name)
            # response['Content-Disposition'] = content
            return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)

class DownloadEntranceResumidoPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
            qids = ast.literal_eval(request.POST['pdf_ids_list'])
            entranceData = []
            total_boxes=0
            total_net_weight=0
            total_gross_weight=0
            for obj in WarehouseEntrance.objects.filter(id__in=qids):
                exists = True
                if obj.warehouseentranceconfirmation_set.all().exists():
                    conf_id = obj.warehouseentranceconfirmation_set.all().values_list('id',flat=True)
                    conf_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=conf_id)
                    for pallet in conf_pallets:
                        total_boxes += float(pallet.boxes)
                        total_net_weight +=float(pallet.net_weight)
                        total_gross_weight +=float(pallet.gross_weight)
                        if exists:
                            data = {
                                'client_data': True,
                                'client_code': obj.customer.client_code,
                                'entrance_date':obj.entrance_date.strftime("%d-%m-%y"),
                                'entrance_id': obj.pk, 
                                'cust_reference': obj.cust_reference,
                                'product_code': pallet.werehouse_entrance_confirmation.code,
                                'product_description': pallet.werehouse_entrance_confirmation.product.product_description,
                                'boxes':  pallet.boxes,
                                'gross_weight': float(pallet.gross_weight),
                                'net_weight': float(pallet.net_weight)

                                }
                            entranceData.append(data)
                            exists = False
                        else:

                            data = {
                                'client_data': False,
                                'client_code': "",
                                'entrance_date':"",
                                'entrance_id': "", 
                                'cust_reference': "",
                                'product_code': pallet.werehouse_entrance_confirmation.code,
                                'product_description': pallet.werehouse_entrance_confirmation.product.product_description,
                                'boxes':  pallet.boxes,
                                'gross_weight': float(pallet.gross_weight),
                                'net_weight': float(pallet.net_weight)
                                }

                            entranceData.append(data)
                            
                else:
                    data = {
                    'client_data': True,
                    'client_code': obj.customer.client_code,
                    'entrance_date':obj.entrance_date.strftime("%d-%m-%y"),
                    'entrance_id': obj.pk, 
                    'cust_reference': obj.cust_reference,

                    'product_code': "",
                    'product_description': "",
                    'boxes':  0,
                    'gross_weight': 0.0,
                    'net_weight': 0.0
                    }
                    entranceData.append(data)   

            entrance_detail = {'entrance_data': entranceData,"print_date": datetime.datetime.now().strftime("%Y/%m/%d"),"total_boxes":total_boxes,"total_gross_weight":total_gross_weight,"total_net_weight":total_net_weight}
            pdf = render_to_pdf('pdf/entrance_summary_pdf.html', entrance_detail)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Entradas_resumido_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(filename):
                    os.system('touch %s'%filename)
                filename = os.path.join(settings.MEDIA_ROOT, "entrance_resume_reports", filename)
                with open(filename, "w") as file:
                    file.write(response.content)
                return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)
