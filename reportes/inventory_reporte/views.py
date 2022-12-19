# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .forms import  AFQFormSet, AFQFormSetNoExtra, AdvancedFilterFormSet
from django.views.generic import View, CreateView
from rest_framework.generics import ListCreateAPIView, CreateAPIView
import json, pdb
from django.http import JsonResponse
from .serializers import InventorySerializer,InventoryLogSerializer, WarehouseEntranceSerializer
import time, os
from django.db.models import Q
import urllib
from django.http import HttpResponse
from warehouses.warehouse_entrance.models import *
from django.conf import settings
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.db.models.signals import pre_save
from catalogs.warehouse.models import Warehouse,WarehouseInventory,WarehouseInventoryLog
import datetime
from warehouses.utils import render_to_pdf
from rest_framework.permissions import IsAuthenticated, BasePermission
from warehouses.warehouse_history.filters import EntranceFilter, ExitFilter
class InventoryList(LoginRequiredMixin, ListView):
    template_name = 'reportes/warehouse_inventory/index.html'
    model = WarehouseInventory
    queryset = WarehouseInventory.objects.none()
    def get_context_data(self, **kwargs):
    	context = super(InventoryList, self).get_context_data(**kwargs)
    	context['formset'] = AFQFormSet
    	return context


class InventoryLogList(LoginRequiredMixin, ListView):
    template_name = 'reportes/warehouse_inventory/inventory_logs.html'
    model = WarehouseInventory
    queryset = WarehouseInventoryLog.objects.none()
    def get_context_data(self, **kwargs):
        context = super(InventoryLogList, self).get_context_data(**kwargs)
        context['locations'] = WarehouseLocation.objects.all()
        context['warehouses'] = Warehouse.objects.all()
        return context
    

class InventoryLogsFilterView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        location = data['warehouse_location']
        warehouse = data['warehouse']
        start_date = data['start_date']
        end_date = data['end_date']
        try:
            if start_date !="" and end_date != "" and warehouse != "" and location !="":
                queryset = WarehouseInventoryLog.objects.filter(warehouse_inventory__warehouse_entrance_pallet__warehouse=warehouse,warehouse_inventory__warehouse_location=location,created_at__gte=start_date,created_at__lte=end_date)
            elif start_date !="" and end_date != "" and warehouse != "":
                queryset = WarehouseInventoryLog.objects.filter(warehouse_inventory__warehouse_entrance_pallet__warehouse=warehouse,created_at__gte=start_date,created_at__lte=end_date)
            elif start_date !="" and end_date != "" and location != "":
                queryset = WarehouseInventoryLog.objects.filter(warehouse_inventory__warehouse_location=location,created_at__gte=start_date,created_at__lte=end_date)
            elif location != "" and warehouse != "":
                queryset = WarehouseInventoryLog.objects.filter(warehouse_inventory__warehouse_location=location,warehouse_inventory__warehouse_entrance_pallet__warehouse=warehouse)
            elif location !="":
                queryset = WarehouseInventoryLog.objects.filter(warehouse_inventory__warehouse_location=location)
            elif warehouse !="":
                queryset = WarehouseInventoryLog.objects.filter(warehouse_inventory__warehouse_entrance_pallet__warehouse=warehouse)
            elif start_date !="" and end_date != "":
                queryset = WarehouseInventoryLog.objects.filter(created_at__gte=start_date,created_at__lte=end_date)
            else:
                queryset = WarehouseInventoryLog.objects.all()
            if len(queryset)>0:
                new_data = InventoryLogSerializer(data=queryset, many=True)
                new_data.is_valid()
            else:
                queryset = WarehouseInventoryLog.objects.all()
                new_data = InventoryLogSerializer(data=queryset)
                new_data.is_valid()
        except Exception as ex:
            print(ex)
            queryset = WarehouseInventoryLog.objects.none()
            new_data = InventoryLogSerializer(data=queryset)
            new_data.is_valid()
        return JsonResponse(new_data.data, safe=False)


class InventoryReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST
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
            queryset = WarehouseInventory.objects.filter(**query_list).extra(order_by=ordering_val)
            if len(queryset)>0:
                new_data = InventorySerializer(queryset, many=True)
            else:
                queryset = WarehouseInventory.objects.none()
                new_data = InventorySerializer(queryset, many=True)
        except Exception as ex:
            print(ex)
            queryset = WarehouseInventory.objects.none()
            new_data = InventorySerializer(queryset, many=True)
        return JsonResponse(new_data.data, safe=False)

class FilterInventoryChoicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_data = ()
        foreign_data = kwargs['field'].split('__')
        if foreign_data[0] == "client":
            field_type = Client._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        if foreign_data[0] == "product":
            field_type = Product._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        elif foreign_data[0] == "warehouse_entrance_pallet":
            field_type = WarehouseEntrancePallet._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)        
        else:
            field_type = WarehouseEntrance._meta.get_field(kwargs['field']).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        
class DownloadInventoryPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        counter=1
        try:
            if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
                qids = ast.literal_eval(request.POST['pdf_ids_list'])
                warehouse_inventory = WarehouseInventory.objects.filter(Q(id__in=qids) & (Q(available_total_boxes__gt=0) | Q(retained_boxes__gt=0)) & Q(available_gross_weight__gt=0.0))
                warehouse_inventory = warehouse_inventory.values('pk', 'total_kg',
                                'total_boxes',
                                'rack',
                                'exp_date',
                                'available_gross_weight',
                                'available_net_weight',
                                'client__name',
                                'product__product_code',
                                'product__product_description',
                                'warehouse_entrance_pallet__warehouse__code' ,
                                'warehouse_entrance_pallet__cost_lot',
                                'warehouse_entrance_pallet__palet_lot',
                                'warehouse_entrance_pallet__invoice_weight',
                                'warehouse_entrance_pallet__retained_quantity',
                                'warehouse_entrance_pallet__retained_reason',
                                'warehouse_entrance_pallet__werehouse_entrance_confirmation__werehouse_entrance__id',
                                'warehouse_entrance_pallet__location__shortcode',
                                'warehouse_entrance_pallet__location__warehousedepthlevel__height__description',
                                'warehouse_entrance_pallet__werehouse_entrance_confirmation__werehouse_entrance__cust_reference')

                
                inventory_data = []  
                count_total_kg = 0
                count_total_boxes = 0
                count_peso_bruto = 0
                count_peso_neto = 0
                count_invoice_weight = 0
                count_retained_quantity = 0
                    
                html_templates = """
                        <tr style="border-top:1px solid #000;">
                            <td style="padding: 5px 3px 10px 3px;width: 12%" valign="top">{warehouse_code}</td>                
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top">{location}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top">{product_code}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top" >{product_description}</td>                
                            <td style="width: 11.5%;" valign="top" > </td>
                            <td style="width: 11.5%;" valign="top" > </td>
                            <td style="width: 11.5%;" valign="top" > </td>
                        </tr>

                        <tr>                
                            <td style="padding: 5px 3px 10px 3px;width: 12%" valign="top"> <br>{cost_lot}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 12%" valign="top"> <br>{palet_lot}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"> <br>{retained_reason}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"> <br>{cust_reference}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"> <br>{entrance}</td>
                            <td style="width: 11.5%;" valign="top" > </td>
                            <td style="width: 11.5%;" valign="top" > </td>
                            <td style="width: 11.5%;" valign="top" > </td>
                            <td style="width: 11.5%;" valign="top" > </td>

                        </tr> 
                        <tr>
                            <td style="padding: 5px 3px 10px 3px;width: 12%" valign="top"><br>{exp_date}</td>
                            <td style="width: 12%" valign="top" > </td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"> <br>{existing_boxes_diff}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"> <br>{retained_quantity}</td>
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"><br>{cliente_name}</td> 
                            <td style="width: 11.5%;" valign="top" > </td>
                            <td style="padding: 12px 3px 0 3px;width: 11.5%" valign="top">{boxes}</td>               
                            <td style="padding: 5px 3px 10px 3px;width: 11.5%" valign="top"> <br>{existing_boxes}</td>
                            <td style="width: 11.5%;" valign="top" > </td>


                        </tr>               
                """
                html_templates_str = ""
                for inventory in warehouse_inventory.iterator():
                    counter = counter+1

                    if not inventory.get('total_kg') in [None, '']:
                        count_total_kg+=  inventory.get('total_kg')

                    if not inventory.get('total_boxes') in [None, '']:
                        count_total_boxes+=  inventory.get('total_boxes')

                    if not inventory.get('warehouse_entrance_pallet__invoice_weight') in [None, '']:
                        count_invoice_weight+= inventory.get('warehouse_entrance_pallet__invoice_weight')

                    if not inventory.get('warehouse_entrance_pallet__retained_quantity') in [None, '']:
                        count_retained_quantity+= inventory.get('warehouse_entrance_pallet__retained_quantity')

                    count_peso_bruto+= inventory.get('available_gross_weight')
                    count_peso_neto+= inventory.get('available_net_weight')
                    height_level=0
                    try:
                        height_level = inventory.get('warehouse_entrance_pallet__location__warehousedepthlevel__height__description')
                    except:
                        pass
                    inv = WarehouseInventory.objects.get(pk=inventory.get('pk'))
                    exit_total_boxes = inv.get_exit_total_boxes
                    inventory_boxes = exit_total_boxes - inv.warehouse_entrance_pallet.retained_quantity
                    html_templates_str += html_templates.format(
                    warehouse_code=str(checkAsciCode(inventory.get('warehouse_entrance_pallet__warehouse__code'))),
                    location=str(checkAsciCode(inventory.get('warehouse_entrance_pallet__location__shortcode'))),
                    cliente_name=str(checkAsciCode(inventory.get('client__name'))),
                    product_code=str(checkAsciCode(inventory.get('product__product_code'))),
                    product_description=str(checkAsciCode(inventory.get('product__product_description'))),
                    exp_date= str(checkAsciCode(inventory.get('exp_date'))),
                    cost_lot= str(checkAsciCode(inventory.get('warehouse_entrance_pallet__cost_lot', ''))),
                    palet_lot= str(checkAsciCode(inventory.get('warehouse_entrance_pallet__palet_lot', ''))),
                    entrance= str(checkAsciCode(inventory.get('warehouse_entrance_pallet__werehouse_entrance_confirmation__werehouse_entrance__id'))),
                    # boxes= str(checkAsciCode(checkAsciCode(warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.boxes),
                    # total_kg= str(checkAsciCode(checkAsciCode(warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.total_kg),
                    boxes= str(checkAsciCode(inventory.get('total_boxes', ''))),
                    total_kg= str(checkAsciCode(inventory.get('total_kg', ''))),
                    retained_quantity= str(checkAsciCode(inventory.get('warehouse_entrance_pallet__retained_quantity', ""))),
                    retained_reason= str(checkAsciCode(inventory.get('warehouse_entrance_pallet__retained_reason', ""))),
                    cust_reference= str(checkAsciCode(inventory.get('warehouse_entrance_pallet__werehouse_entrance_confirmation__werehouse_entrance__cust_reference'))),
                    existing_boxes= str(checkAsciCode(exit_total_boxes)),
                    existing_boxes_diff= str(checkAsciCode(inventory_boxes)),

                    )
                    
                context_dict = {'inventory_data': html_templates_str,'count_peso_neto':count_peso_neto,'count_peso_bruto':count_peso_bruto,'count_total_boxes':count_total_boxes,'count_invoice_weight':count_invoice_weight,'count_retained_quantity':count_retained_quantity,"print_date": datetime.datetime.now().strftime("%Y/%m/%d")}
                template_src = "pdf/inventory_list_pdf.html"
                from django.template.loader import get_template
                template = get_template(template_src)
                html  = template.render(context_dict)
                
                try:
                    from pyvirtualdisplay import Display
                    import pdfkit
                    display = Display(visible=0, size=(1024, 768))
                    display.start()
                    filename = "Inventario_detalle_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
                    filename_path = os.path.join(settings.MEDIA_ROOT, "inventory_reports", filename)
                    options = { 'orientation': 'Landscape', 'encoding': 'utf-8', 'dpi': 400}
                    pdfkit.from_string(html, filename_path, options=options)
                    display.stop()
                    return JsonResponse({"message": "success","code":200, "file":filename_path.split('/media')[-1]}, safe=False)
                except Exception as ex:
                    return JsonResponse({"message": "fail","code":500, "error": str(ex)}, safe=False)
                
                
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        except Exception as ers:
            return JsonResponse({"message": "fail","code":500, "error": str(ers)}, safe=False)
            
                      

class DownloadInventoryReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[
            (u"Almacén", 20),
            (u"Ubicación", 20),
        	(u"Cliente", 20),
            (u"Código", 20),
            (u"Descripción Producto", 20),
        	(u"Caducidad", 20),
            (u"Lote Cliente", 20),
            (u"Lote Tarima", 20),
            (u"Cajas en Proceso Salida", 20),
            (u"Cantidad Retenida",20),
            (u"Cajas Disponibles", 20),
            (u"Cajas en Existencia", 20),           
            (u"Motivo de Retencion",20),
            (u"Referencia en Recibo",20),
            (u"Folio Entrada", 20),
            (u"Fecha de Entrada", 20)
        	]
            count_total_kg = 0
            count_available_total_boxes = 0
            count_peso_bruto = 0
            count_peso_neto = 0
            count_invoice_weight = 0
            count_retained_quantity = 0
            reportData = []
            count_exit_total_boxes = 0
            count_available_boxes = 0

            inventories = WarehouseInventory.objects.filter(Q(id__in=qids))
            for obj in inventories:
                height_level=0
                # exit_pallet_weight = obj.get_total_exit_pallet_weight()
                #first
                exit_total_boxes = obj.get_exit_total_boxes
                count_exit_total_boxes += exit_total_boxes
                available_boxes = obj.available_total_boxes
                if available_boxes < 0:
                    available_boxes = 0
                count_available_boxes += available_boxes
                if obj.warehouse_entrance_pallet.location:
                    if obj.warehouse_entrance_pallet.location.warehousedepthlevel_set.exists():
                        height_level = obj.warehouse_entrance_pallet.location.warehousedepthlevel_set.first().height.description
                if obj.warehouse_entrance_pallet != None:
                    rack = obj.rack
                    retained_quantity = obj.warehouse_entrance_pallet.retained_quantity
                    if obj.total_kg != None:
                        count_total_kg+=  obj.total_kg
                    # if obj.available_total_boxes != None:
                    #     count_available_total_boxes+=  obj.available_total_boxes
                    if obj.warehouse_entrance_pallet.invoice_weight != None:
                        count_invoice_weight+= obj.warehouse_entrance_pallet.invoice_weight
                    if obj.warehouse_entrance_pallet.retained_quantity != None:
                        count_retained_quantity+= obj.warehouse_entrance_pallet.retained_quantity
                    count_peso_bruto+= obj.available_gross_weight
                    count_peso_neto+= obj.available_net_weight
                    if obj.warehouse_location != None:
                        short_code = obj.warehouse_location.shortcode
                    else:
                        short_code = ""
                    inventory_boxes = exit_total_boxes + retained_quantity + available_boxes
                    count_available_total_boxes +=inventory_boxes
                    if (exit_total_boxes ==0 and retained_quantity ==0 and available_boxes == 0 and inventory_boxes ==0):
                        pass
                    else:
                        retained_reason = obj.warehouse_entrance_pallet.retained_reason
                        if retained_quantity == 0:
                            retained_reason = ""
                        reportData.append(
                            [obj.warehouse_entrance_pallet.warehouse.code,
                            short_code,
                            obj.client.name,
                            obj.product.product_code,
                            obj.product.product_description,
                            obj.exp_date, 
                            obj.warehouse_entrance_pallet.cost_lot,
                            obj.warehouse_entrance_pallet.palet_lot,
                            exit_total_boxes,
                            retained_quantity,
                            available_boxes,
                            inventory_boxes,
                            retained_reason,
                            obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.cust_reference,
                            obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.id,
                            obj.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance.entrance_date,
                           ]
                            )

                else:
                    count_total_kg+=  obj.total_kg
                    # count_available_total_boxes+=  obj.available_total_boxes
                    if (exit_total_boxes ==0 ==0 and obj.available_total_boxes == 0 and inventory_boxes ==0):
                        pass
                    else:
                        reportData.append(
                            [
                            "N/A",
                            short_code,
                            obj.client.name,
                            obj.product.product_code,
                            obj.product.product_description,
                            obj.exp_date,
                            "N/A",
                            "N/A" ,
                            exit_total_boxes, 
                            "N/A" ,
                            obj.available_total_boxes,
                            inventory_boxes,
                            "N/A",
                            "N/A",
                            "N/A",
                            "N/A"])
            reportData.append(["","","","","","","","","","","","","","","",""])
            reportData.append(["","","","","", "", "","Total",count_exit_total_boxes, count_retained_quantity,count_available_boxes,count_available_total_boxes,"","","", "", "", "", ""])
            report_name = "Inventario_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
            call = GenerateXlsxReport(report_name, column, reportData,'REPORTE DE INVENTARIO DETALLADO')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            
            # response['Content-Disposition'] = content
            # return response
            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            filename = "Inventario_Detallado_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "inventory_reports", filename)
            with open(filename, "w") as file:
                file.write(response.content)
            
            return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)



#-----------------------------


class DownloadInvLogReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[
            (u"ID", 20),
            (u"CLIENTE", 20),
            (u"Código", 20),
            (u"KG TOTALES", 20),
            (u"CAJAS", 20),
            (u"CAJAS RETENIDAS", 20),
            (u"MOTIVO DEL AJUSTE", 20),
            (u"USUARIO", 20),
            (u"CREADO", 20),
            ]
            reportData = []
            for obj in WarehouseInventoryLog.objects.filter(id__in=qids):
                
                email = "N/A"
                if obj.user:
                    email = obj.user.username
                reportData.append([
                obj.id,
                obj.warehouse_inventory.client.client_code,
                obj.warehouse_inventory.product.product_description,
                obj.total_kg,
                obj.total_boxes,
                obj.retained_boxes,
                obj.adjust_reason,
                email,
                obj.created_at.strftime("%Y/%m/%d"),
                ])
            report_name = "AjustesInventario%s.xlsx"%datetime.datetime.now().strftime("%Y_%m_%d")
            call = GenerateXlsxReport(report_name, column, reportData,'Ajustes a Inventario')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "AjustesInventario%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "inventory_log_reports", filename)
            with open(filename, "w") as file:
                file.write(response.content)
            # content = "attachment; filename=%s" %(report_name)
            # response['Content-Disposition'] = content
            return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)


class DownloadInvLogPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
            qids = ast.literal_eval(request.POST['pdf_ids_list'])
            pdfData = []        
            for obj in WarehouseInventoryLog.objects.filter(id__in=qids):
                    
                email = "N/A"
                if obj.user:
                    email = obj.user.username       
                    
                data = {
                'client_code': obj.warehouse_inventory.client.client_code,
                'product_description':obj.warehouse_inventory.product.product_description,
                'total_kg': obj.total_kg,
                'total_boxes': obj.total_boxes,
                'retained_boxes': obj.retained_boxes,
                'adjust_reason': obj.adjust_reason,
                'email': email,
                'created_date': (obj.created_at).strftime("%Y/%m/%d")
                
                }
                pdfData.append(data)       

            

            inventory_detail = {'inventory_log': pdfData,"print_date": datetime.datetime.now().strftime("%Y/%m/%d")}
            pdf = render_to_pdf('pdf/inventory_log_pdf.html', inventory_detail)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Ajustes_Inventario_%s.pdf"%(datetime.datetime.now().strftime("%Y/%m/%d"))
                if not os.path.exists(filename):
                    os.system('touch %s'%filename)
                filename = os.path.join(settings.MEDIA_ROOT, "inventory_log_reports", filename)
                with open(filename, "w") as file:
                    file.write(response.content)
                return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)


def checkAsciCode(field):
    if field in [None,'']:
        return ""
    else:
        try: 
            return unicode(field).encode('utf-8')
        except: 
            return ""

class ResultRomaneoList(LoginRequiredMixin, CreateView):
    template_name = 'reportes/inventory_reporte/list.html'
    model = WarehouseEntrance
    fields = ['entrance_date','entrance_hour']
    def get_context_data(self, **kwargs):
        context = super(ResultRomaneoList, self).get_context_data(**kwargs)
        context['products'] = Product.objects.all().order_by("product_code")
        if self.request.user.is_staff:
            context['customers'] = Client.objects.all().order_by("name")
        else:
            context['customers'] = self.request.user.client_set.all().order_by("name")
        return context

class ResultRomaneoFilter(CreateAPIView):
    queryset = WarehouseEntrance.objects.all()
    serializer_class = WarehouseEntranceSerializer
    # permission_classes = (IsAuthenticated, IsCustomerInSGA)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        from rest_framework.response import Response
        queryset_entrance = ()
        queryset_exit = ()
        if self.request.POST.get('entrance') != None and self.request.POST.get('exit') != None:
            queryset_entrance = EntranceFilter(self.request.POST)
            queryset_exit = ExitFilter(self.request.POST)
        elif self.request.POST.get('entrance') != None:
            queryset_entrance = EntranceFilter(self.request.POST)
        elif self.request.POST.get('exit') != None:
            queryset_exit = ExitFilter(self.request.POST)

        if len(queryset_entrance) > 0:
            url1 = "<a role='button' href='/warehouse_entrance/{}/entrance-resultado-romaneo/' class='btn btn-info'><i class='fa fa-print'></i></a>"
            if self.request.user.is_staff:
                queryset_entrance = [[data.customer.name, [product.product.product_code for product in data.wproductmeasurement_set.all()] , "Entrada",data.id, data.entrance_date, data.total_kg, url1.format(data.id)] for data in queryset_entrance]
            else:
                queryset_entrance = [[data.customer.name, [product.product.product_code for product in data.wproductmeasurement_set.all()] , "Entrada",data.id, data.entrance_date, data.total_kg, url1.format(data.id)] for data in queryset_entrance]
                # queryset_entrance = [[data.customer.name, [product.product.product_code for product in data.wproductmeasurement_set.all()] , "Entrada",data.id, data.entrance_date, data.total_kg] for data in queryset_entrance]

            
        if len(queryset_exit) > 0:
            url1 = "<a role='button' href='/warehouse_exit/{}/exit-resultado-romaneo/' class='btn btn-info'><i class='fa fa-print'></i></a>"
            if self.request.user.is_staff:
                queryset_exit = [[data.customer.name, [product.product.product_code for product in data.wexitproductmeasurement_set.all()] , "Salida", data.id ,data.exit_date, (data.total_kg if data.total_kg != None else 0 ),  url1.format(data.id)] for data in queryset_exit]
            else:
                queryset_exit = [[data.customer.name, [product.product.product_code for product in data.wexitproductmeasurement_set.all()] , "Salida", data.id ,data.exit_date, (data.total_kg if data.total_kg != None else 0 ),  url1.format(data.id)] for data in queryset_exit]
                # queryset_exit = [[data.customer.name, [product.product.product_code for product in data.wexitproductmeasurement_set.all()] , "Salida", data.id ,data.exit_date, (data.total_kg if data.total_kg != None else 0 )] for data in queryset_exit]
        data = tuple(queryset_exit)+tuple(queryset_entrance)
        return Response(data)

