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
from warehouses.warehouse_entrance.models import *
from textwrap import wrap
class ExitList(LoginRequiredMixin, ListView):
    template_name = 'reportes/warehouse_exit/index.html'
    model = WarehouseExit
    queryset = WarehouseExit.objects.none()
    def get_context_data(self, **kwargs):
    	context = super(ExitList, self).get_context_data(**kwargs)
    	context['formset'] = AFQFormSet
    	return context

class ExitReportView(LoginRequiredMixin, View):
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

class FilterExitChoicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_data = ()#list(WarehouseExit.objects.all().values_list(kwargs['field'], flat=True).distinct())
        foreign_data = kwargs['field'].split('__')

        if foreign_data[0] == "customer":
            field_type = Client._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        elif foreign_data[0] == "wexitproductmeasurement":
            field_type = WExitProductMeasurement._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        
        elif foreign_data[1] == "warehouseexitpallet":
            # For searching by pallet lot
            field_type = WarehouseExitPallet._meta.get_field(foreign_data[2]).get_internal_type()
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
        
        


class DownloadExitPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        
        from django.core.files import File
        import ast
        if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
            qids = ast.literal_eval(request.POST['pdf_ids_list'])
            warehouses = WarehouseExit.objects.filter(id__in=qids)
            exit_data = []
            total_boxes = 0
            total_gross_weight = 0
            total_net_weight = 0
            html_exit = """ <tr style="border-top:1px solid #000; padding: 5px 0;">
                    <td valign="top">{exit_id}</td>
                    <td valign="top">{exit_date}</td>
                    <td valign="top">{client_code}</td>
                    <td valign="top">{cust_reference}</td>
                    <td valign="top">{boxes}</td>
                    <td valign="top">&nbsp;</td>
                    <td valign="top">{total_kg}</td>
                    <td valign="top">{remitente}</td>
                    <td valign="top">{transportistas}</td>
                    <td valign="top">{consignatarios}</td>
                </tr>"""

            html_exit_data=''
            for warehouse in warehouses:
                html_exit_data += html_exit.format(
                exit_id= checkAsciCode(warehouse.id),
                exit_date= checkAsciCode(warehouse.exit_date),
                client_code= '\n'.join(wrap(checkAsciCode(warehouse.customer.client_code),7)),
                cust_reference= checkAsciCode(warehouse.cust_reference),
                transportistas= checkAsciCode(warehouse.carrier),
                remitente= checkAsciCode(warehouse.cargo_sender),
                consignatarios= checkAsciCode(warehouse.consignee),
                boxes= checkAsciCode(float(warehouse.boxes)),
                total_kg= checkAsciCode(warehouse.total_kg),
                )
                confirmation_data=[]
                conf_id = warehouse.wexitconfirmation_set.all().values_list('id',flat=True)
                conf_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=conf_id)
                
                html_exit_conf = """ <tr style="padding: 5px 0;">
                            <td valign="top" style="width: 150px;">{code}</td>
                            <td valign="top" style="width: 150px;">{product_description}</td>
                            <td valign="top">{exp_date}</td>
                            <td valign="top">{cost_lot}</td>
                            <td valign="top">{palet_lot}</td>
                            <td valign="top">{product_boxes}</td>                        
                 
                        </tr> """
                html_exit_conf_data=''
                total_boxes_per_entanace = 0
                per_exit_row = """<tr><td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" > </td>
                                        <td valign="top" >Total: </td>
                                        <td valign="top" >{total_boxes_per_entanace} </td>
                                        <td valign="top" > </td>
                                        <td valign="top" ></td>
                                        <td valign="top" ></td>
                                        </tr>"""    
                for pallet in conf_pallets:
                    total_boxes+= pallet.boxes
                    total_gross_weight+=pallet.gross_weight
                    total_net_weight+=pallet.net_weight
                    total_boxes_per_entanace += float(pallet.boxes)              
                    html_exit_conf_data += html_exit_conf.format(
                    code= checkAsciCode(pallet.werehouse_exit_confirmation.product.product_code),
                    product_description= checkAsciCode(pallet.werehouse_exit_confirmation.product.product_description),
                    exp_date= checkAsciCode(pallet.exp_date),
                    cost_lot= checkAsciCode(pallet.cost_lot),
                    palet_lot= checkAsciCode(pallet.palet_lot),                
                    product_boxes= checkAsciCode(pallet.boxes)
                    )
                    # confirmation_data.append(conf_data)
                html_exit_data += html_exit_conf_data
                html_exit_data += per_exit_row.format(total_boxes_per_entanace=str(float(total_boxes_per_entanace)))
               
                # exit_data.append(data)
            exit_data_data = {'exit_data': html_exit_data,'total_boxes':total_boxes,'total_gross_weight':total_gross_weight,'total_net_weight':total_net_weight,"print_date": datetime.datetime.now().strftime("%Y/%m/%d")}
            pdf = render_to_pdf('pdf/exit_list_pdf.html', exit_data_data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Salidas_Detalle_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(filename):
                    os.system('touch %s'%filename)
                filename = os.path.join(settings.MEDIA_ROOT, "exit_reports", filename)
                with open(filename, "w") as file:
                    file.write(response.content)
                return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)

class DownloadExitReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[

            (u"FOLIO", 15),
            (u"CLIENTE", 20),
            (u"FECHA SALIDA", 20),
            (u"HORA SALIDA", 20),
            (u"REMITENTE", 20),
            (u"REFERENCIA", 20),
            (u"TRANSPORTISTA", 20),
            (u"TRANSPORTE", 20),
            (u"CONSIGNATARIO", 20),
            (u"FLEJE/SELLO1", 20),
            (u"FLEJE/SELLO2", 20),

            (u"Código",20),
            (u"DESCRIPCION PRODUCTO", 20),
            (u"CADUCIDAD", 20),
            (u"LOTE CLIENTE", 20),
            (u"LOTE TARIMA", 20),
            (u"CAJAS",20),
            (u"PESO BRUTO", 20),
            (u"PESO NETO", 20)

        	]

            total_boxes = 0
            total_gross_weight = 0
            total_net_weight = 0
            reportData = []
            for obj in WarehouseExit.objects.filter(id__in=qids):
                exists = True 
                if obj.wexitconfirmation_set.all().exists():
                    conf_id = obj.wexitconfirmation_set.all().values_list('id',flat=True)
                    conf_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=conf_id)
                    if obj.carrier:
                        carrier_code = obj.carrier.code
                    else:
                        carrier_code = ""

                    if obj.consignee:
                        consignee_name = obj.consignee.name
                    else:
                        consignee_name = ""

                    if obj.vehicle:
                        vehicle_desc = obj.vehicle.description
                    else:
                        vehicle_desc = ""
                        
                    for pallet in conf_pallets:
                        # boxes = obj.wexitproductmeasurement_set.filter(product=confirmation.product).first().boxes
                        total_boxes+=pallet.boxes
                        total_gross_weight+= pallet.gross_weight
                        total_net_weight+= pallet.net_weight
                        if exists:
                            reportData.append([
                            obj.pk,
                            obj.customer.name,
                            obj.exit_date.strftime("%d-%m-%y"),
                            obj.exit_hour.strftime("%H:%M"),
                            obj.cargo_sender,
                            obj.cust_reference,
                            carrier_code,
                            vehicle_desc,
                            consignee_name,
                            obj.seal1,
                            obj.seal2,

                            pallet.werehouse_exit_confirmation.product.product_code,
                            pallet.werehouse_exit_confirmation.product.product_description,
                            pallet.exp_date,
                            pallet.cost_lot,
                            pallet.palet_lot,
                            pallet.boxes,
                            float(pallet.gross_weight),
                            float(pallet.net_weight)])
                            # exists = False
                        else:
                            reportData.append(["","","","","","","","","","",
                                pallet.werehouse_exit_confirmation.product.product_code,
                                pallet.werehouse_exit_confirmation.product.product_description,
                                pallet.exp_date,
                                pallet.cost_lot,
                                pallet.palet_lot,
                                pallet.boxes,
                                float(pallet.gross_weight),
                                float(pallet.net_weight)])
                else:
                    reportData.append([
                            obj.pk,
                            obj.customer.name,
                            obj.exit_date.strftime("%d-%m-%y"),
                            obj.exit_hour.strftime("%H:%M"),
                            obj.cargo_sender,
                            obj.cust_reference,
                            obj.carrier.code,
                            obj.vehicle.description,
                            obj.consignee.name,
                            obj.seal1,
                            obj.seal2,
                            "N/A","N/A","N/A","N/A","N/A","N/A","N/A","N/A"])

            reportData.append(["","","","","","","","","","","","","","","","","",""])
            reportData.append(["","","","","","","","","","","","","","","","total",total_boxes,total_gross_weight,total_net_weight])
        	# reportData = [[obj.pk,obj.customer.name,obj.exit_date,obj.exit_hour,obj.total_kg,obj.total_price,obj.kg_per_price,obj.boxes,obj.kg_per_boxes,obj.cargo_sender,obj.cust_reference,obj.carrier.name,obj.vehicle.description,obj.consignee.name,obj.seal1,obj.seal2,obj.license_plate] for obj in WarehouseExit.objects.filter(id__in=qids)]
            report_name = "Reporte_Salida_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
            call = GenerateXlsxReport(report_name, column, reportData,'REPORTE DE SALIDA DETALLADO')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            filename = "Reporte_Salida_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "exit_reports", filename)
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