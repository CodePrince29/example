# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .forms import  AFQFormSet, AFQFormSetNoExtra, AdvancedFilterFormSet
from django.views.generic import View
import json
from django.http import JsonResponse
from .serializers import WarehouseExitSerializer
import time,os
import urllib
from django.http import HttpResponse
from warehouses.warehouse_exit.models import *
from django.conf import settings
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.db.models.signals import pre_save
from catalogs.warehouse.models import Warehouse
import datetime
from warehouses.utils import render_to_pdf

class ExitResumidoList(LoginRequiredMixin, ListView):
    template_name = 'reportes/exit_resumido/index.html'
    model = WarehouseExit
    queryset = WarehouseExit.objects.none()
    def get_context_data(self, **kwargs):
        context = super(ExitResumidoList, self).get_context_data(**kwargs)
        context['formset'] = AFQFormSet
        return context

class ExitResumidoReportView(LoginRequiredMixin, View):
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

            queryset = WarehouseExit.objects.filter(**query_list).extra(order_by=ordering_val)
            if len(queryset)>0:
                new_data = WarehouseExitSerializer(data=queryset, many=True)
                new_data.is_valid()
            else:
                queryset = WarehouseExit.objects.none()
                new_data = WarehouseExitSerializer(data=queryset)
                new_data.is_valid()
        except:
            queryset = WarehouseExit.objects.none()
            new_data = WarehouseExitSerializer(data=queryset)
            new_data.is_valid()
        return JsonResponse(new_data.data, safe=False)

class FilterExitResumidoChoicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_data = ()#list(WarehouseExit.objects.all().values_list(kwargs['field'], flat=True).distinct())
        foreign_data = kwargs['field'].split('__')

        if foreign_data[0] == "customer":
            field_type = Client._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "wexitproductmeasurement":
            field_type = WExitProductMeasurement._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "wexitconfirmation":
            field_type = WExitConfirmation._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
                
        elif foreign_data[0] == "wexitproductvehicleinspection":
            field_type = WExitProductVehicleInspection._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        
        elif foreign_data[0] == "carrier":
            field_type = Carrier._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "vehicle":
            field_type = Vehicle._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        
        
        else:
            field_type = WarehouseExit._meta.get_field(kwargs['field']).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        


class DownloadExitResumidoReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[
            
            (u"CLIENTE", 20),
            (u"FECHA DE SALIDA", 15),
            (u"NUMERO DE SALIDA", 15),
            (u"NUM REF", 20),
            (u"Código",20),
            (u"DESCRIPCION PRODUCTO", 20),
            (u"CANTIDAD", 20),
            (u"PESO BRUTO", 20),
            (u"PESO NETO", 20)
            ]

            total_boxes = 0
            total_net_weight = 0
            total_gross_weight = 0
            reportData = []
            for obj in WarehouseExit.objects.filter(id__in=qids):
                exists = True            
                if obj.wexitconfirmation_set.exists():
                    conf_id = obj.wexitconfirmation_set.all().values_list('id',flat=True)
                    conf_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=conf_id)
                    
                    for pallet in conf_pallets:
                        total_boxes += float(pallet.boxes)
                        total_net_weight +=float(pallet.net_weight)
                        total_gross_weight +=float(pallet.gross_weight)
                        if exists:
                            reportData.append([
                            obj.customer.client_code,
                            obj.exit_date.strftime("%d-%m-%y"),
                            obj.pk,                        
                            obj.cust_reference,
                            pallet.werehouse_exit_confirmation.product.product_code,
                            pallet.werehouse_exit_confirmation.product.product_description,
                            pallet.boxes,
                            float(pallet.gross_weight),
                            float(pallet.net_weight)])
                            # exists = False
                        else:
                            reportData.append(["","","","",
                                pallet.werehouse_exit_confirmation.product.product_code,
                                pallet.werehouse_exit_confirmation.product.product_description,
                                pallet.boxes,
                                float(pallet.gross_weight),
                                float(pallet.net_weight)])
                else:
                    reportData.append([
                        obj.customer.client_code,
                        obj.exit_date.strftime("%d-%m-%y"),
                        obj.pk,                        
                        obj.cust_reference,
                        "N/A","N/A","N/A","N/A","N/A"])
            if len(reportData) != 0:
                reportData.append(["","","","","","","","",""])
                reportData.append(["","","","","","","","",""])
                reportData.append(["","","","","","","TOTAL:%s"%(total_boxes),"TOTAL:%s"%(total_gross_weight),"TOTAL:%s"%(total_net_weight)])
            
            report_name = "Salidas_resumido_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
            call = GenerateXlsxReport(report_name, column, reportData,'SALIDAS RESUMIDO')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "Salidas_resumido_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "exit_resume_reports", filename)
            with open(filename, "w") as file:
                file.write(response.content)
            # content = "attachment; filename=%s" %(report_name)
            # response['Content-Disposition'] = content
            return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)
       

class DownloadExitResumidoPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
            qids = ast.literal_eval(request.POST['pdf_ids_list'])        
            exitData = []
            total_boxes=0
            total_net_weight=0
            total_gross_weight=0
            for obj in WarehouseExit.objects.filter(id__in=qids):
                exists = True            
                if obj.wexitconfirmation_set.all().exists():
                    conf_id = obj.wexitconfirmation_set.all().values_list('id',flat=True)
                    conf_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=conf_id)
                    for pallet in conf_pallets:
                        total_boxes += float(pallet.boxes)
                        total_net_weight +=float(pallet.net_weight)
                        total_gross_weight +=float(pallet.gross_weight)
                        if exists:
                            data = {
                                'client_data': True,
                                'client_code': obj.customer.client_code,
                                'exit_date':obj.exit_date.strftime("%d-%m-%y"),
                                'exit_id': obj.pk, 
                                'cust_reference': obj.cust_reference,
                                'product_code': pallet.werehouse_exit_confirmation.product.product_code,
                                'product_description': pallet.werehouse_exit_confirmation.product.product_description,
                                'boxes':  pallet.boxes,
                                'gross_weight': float(pallet.gross_weight),
                                'net_weight': float(pallet.net_weight)

                                }
                            exitData.append(data)
                            exists = False
                        else:

                            data = {
                                'client_data': False,
                                'client_code': "",
                                'exit_date':"",
                                'exit_id': "", 
                                'cust_reference': "",
                                'product_code': pallet.werehouse_exit_confirmation.product.product_code,
                                'product_description': pallet.werehouse_exit_confirmation.product.product_description,
                                'boxes':  pallet.boxes,
                                'gross_weight': float(pallet.gross_weight),
                                'net_weight': float(pallet.net_weight)
                                }

                            exitData.append(data)
                            
                else:
                    data = {
                    'client_data': True,
                    'client_code': obj.customer.client_code,
                    'exit_date':obj.exit_date.strftime("%d-%m-%y"),
                    'exit_id': obj.pk, 
                    'cust_reference': obj.cust_reference,

                    'product_code': "",
                    'product_description': "",
                    'boxes':  "",
                    'gross_weight': "",
                    'net_weight': ""
                    }
                    exitData.append(data)       


            exit_detail = {'exit_data': exitData,"print_date": datetime.datetime.now().strftime("%Y/%m/%d"),"total_boxes":total_boxes,"total_gross_weight":total_gross_weight,"total_net_weight":total_net_weight}
            pdf = render_to_pdf('pdf/exit_summary_pdf.html', exit_detail)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Salidas_resumido_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(filename):
                    os.system('touch %s'%filename)
                filename = os.path.join(settings.MEDIA_ROOT, "exit_resume_reports", filename)
                with open(filename, "w") as file:
                    file.write(response.content)
                return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)

def checkAsciCode(field):
    if field is not None and field!='':
        try:
             field = field.encode('ascii', 'ignore').decode('ascii')
        except:
             field = field

        return field