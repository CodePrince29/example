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
from warehouses.warehouse_entrance.models import *
from textwrap import wrap

class EntrancesList(LoginRequiredMixin, ListView):
    template_name = 'reportes/warehouse_entrance/index.html'
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

        elif foreign_data[1] == "warehouseentrancepallet":
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
                    <td valign="top">{entrans_id}</td>
                    <td valign="top">{entrance_date}</td>
                    <td valign="top" style="width: 200px;">{client_code}</td>
                    <td valign="top" >{cust_reference}</td>
                    <td valign="top">{boxes}</td>
                    <td valign="top">{total_kg}</td>
                    <td valign="top"></td>
                    <td valign="top"></td>
                    <td valign="top"></td>
                    <td valign="top"></td>
                    </tr>
                    """
            html_template_entrance_data = ''
            for warehouse in warehouses:
                
                html_template_entrance_data += html_template_entrance.format(
                # 'object': warehouse,            
                entrans_id= checkAsciCode(warehouse.id),
                entrance_date= checkAsciCode(warehouse.entrance_date),
                client_code= '\n'.join(wrap(checkAsciCode(warehouse.customer.client_code),7)),
                cust_reference= checkAsciCode(warehouse.cust_reference),
                boxes= checkAsciCode(float(warehouse.boxes)),
                total_kg= checkAsciCode(float(warehouse.total_kg)),
                )
                

                confirmation_data=[]
                conf_id = warehouse.warehouseentranceconfirmation_set.all().values_list('id',flat=True)
                conf_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=conf_id)
                
                
                html_template_confirmation = """ <tr style="padding: 5px 0;">
                            <td valign="top" style="width: 150px;">{code}</td>
                            <td valign="top" style="width: 150px;">{product_description}</td>
                            <td valign="top">{exp_date}</td>
                            <td valign="top">{cost_lot}</td>
                            <td valign="top">{palet_lot}</td>
                            <td valign="top">{warehouse}</td>
                            <td valign="top">{rack_number}</td>
                            <td valign="top">{location}</td>
                            <td valign="top">{product_boxes}</td>
                        </tr> """
                html_template_confirmation_data = ''
                total_boxes_per_entanace = 0
                total_gross_per_entanace = 0
                per_entrnace_row = """<tr><td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" ></td>
                                        <td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" ></td>
                                        <td valign="top" >Total:{total_boxes_per_entanace}</td>
                                        </tr>"""

                for pallet in conf_pallets:
                    
                    total_boxes+= pallet.boxes
                    total_gross_weight+=pallet.gross_weight
                    total_net_weight+=pallet.net_weight
                    total_boxes_per_entanace += pallet.boxes
                    total_gross_per_entanace += pallet.boxes
                    p_desc = pallet.werehouse_entrance_confirmation.product.product_description 

                    html_template_confirmation_data += html_template_confirmation.format(
                            code= checkAsciCode(pallet.werehouse_entrance_confirmation.code),
                            product_description= checkAsciCode(p_desc),
                            exp_date= checkAsciCode(pallet.exp_date),
                            cost_lot= checkAsciCode(pallet.cost_lot),
                            palet_lot= checkAsciCode(pallet.palet_lot),
                            warehouse= checkAsciCode(pallet.warehouse.code),
                            rack_number=checkAsciCode(pallet.rack_number),
                            location= checkAsciCode(pallet.location.location_number),
                            product_boxes= checkAsciCode(float(pallet.boxes))
                            )

                    
                html_template_entrance_data +=html_template_confirmation_data
                html_template_entrance_data += per_entrnace_row.format(total_boxes_per_entanace=str(float(total_boxes_per_entanace)))
                 

            entrance_data_data = {'entrance_data': html_template_entrance_data,'total_boxes':total_boxes,'total_gross_weight':total_gross_weight,'total_net_weight':total_net_weight,"print_date": datetime.datetime.now().strftime("%Y/%m/%d")}
            pdf = render_to_pdf('pdf/entrance_list_pdf.html', entrance_data_data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Entradas_Detalle_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
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
            (u"FOLIO", 15),
            (u"CLIENTE", 20),
            (u"FECHA DE ENTRADA", 20),
            (u"HORA DE ENTRADA", 20),
            (u"REMITENTE", 20),
            (u"REFERENCIA", 20),
            (u"FLEJE/SELLO1", 20),
            (u"FLEJE/SELLO2", 20),

            (u"Código",20),
            (u"DESCRIPCION PRODUCTO", 20),
            (u"CADUCIDAD", 20),
            (u"LOTE CLIENTE", 20),
            (u"LOTE TARIMA", 20),
            (u"CANTIDAD RETENIDA",20),
            (u"MOTIVO RETENCION",20),
            (u"CAJAS",20),
            (u"PESO BRUTO", 20),
            (u"PESO NETO", 20)
        	]
            reportData = []
            total_boxes = 0
            total_gross_weight = 0
            total_net_weight = 0
            for obj in WarehouseEntrance.objects.filter(id__in=qids):
                exists = True
                if obj.warehouseentranceconfirmation_set.all().exists():
                    conf_id = obj.warehouseentranceconfirmation_set.all().values_list('id',flat=True)
                    conf_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=conf_id)
                    for pallet in conf_pallets:
                        total_boxes+= pallet.boxes
                        total_gross_weight+=pallet.gross_weight
                        total_net_weight+=pallet.net_weight
                        if exists:
                            reportData.append([obj.pk,
                            obj.customer.name,
                            obj.entrance_date.strftime("%d-%m-%y"),
                            obj.entrance_hour.strftime("%H:%M"),
                            obj.cargo_sender,
                            obj.cust_reference,
                            obj.seal1,
                            obj.seal2,
                            pallet.werehouse_entrance_confirmation.code,
                            pallet.werehouse_entrance_confirmation.product.product_description,
                            pallet.exp_date,
                            pallet.cost_lot,
                            pallet.palet_lot,
                            pallet.retained_quantity,
                            pallet.retained_reason,
                            pallet.boxes,
                            float(pallet.gross_weight),
                            float(pallet.net_weight)])
                            # exists = False
                        else:
                            reportData.append(["","","","","","","","",
                                pallet.werehouse_entrance_confirmation.code,
                                pallet.werehouse_entrance_confirmation.product.product_description,
                            
                                pallet.exp_date,
                                pallet.cost_lot,
                                pallet.palet_lot,
                                pallet.retained_quantity,
                                pallet.retained_reason,
                                pallet.boxes,
                                float(pallet.gross_weight),
                                float(pallet.net_weight)])
                else:
                    reportData.append([
                            obj.pk,
                            obj.customer.name,
                            obj.entrance_date.strftime("%d-%m-%y"),
                            obj.entrance_hour.strftime("%H:%M"),
                            obj.cargo_sender,
                            obj.cust_reference,
                            obj.seal1,
                            obj.seal2,
                            "N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"])
            
            reportData.append(["","","","","","","","","","","","","","","","","",""])
            reportData.append(["","","","","","","","","","","","","","","total",total_boxes,total_gross_weight,total_net_weight])
            report_name = "Reporte_Entrada_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
            call = GenerateXlsxReport(report_name, column, reportData,'REPORTE DE ENTRADA DETALLADO')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            filename = "Reporte_Entrada_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
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

