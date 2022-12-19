# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from .forms import  AFQFormSet, AFQFormSetNoExtra, AdvancedFilterFormSet
from django.views.generic import View
import json
from django.http import JsonResponse
from .serializers import InventorySerializer
import time, os
import urllib
from django.http import HttpResponse
from warehouses.warehouse_entrance.models import *
from django.conf import settings
from catalogs.clients.models import Client
from catalogs.product.models import Product
from django.db.models.signals import pre_save
from catalogs.warehouse.models import Warehouse,WarehouseInventory
import datetime
from warehouses.utils import render_to_pdf
from django.db.models import Sum, Count
from warehouses.warehouse_exit.models import WarehouseExitPallet

class WarehouseOcupancy(LoginRequiredMixin, ListView):
    template_name = 'reportes/warehouse_ocupancy/index.html'
    model = WarehouseInventory
    queryset = WarehouseInventory.objects.none()
    def get_context_data(self, **kwargs):
    	context = super(WarehouseOcupancy, self).get_context_data(**kwargs)
    	context['formset'] = AFQFormSet
    	return context

class WarehouseOcupancyReportView(LoginRequiredMixin, View):
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
            queryset = WarehouseInventory.objects.filter(**query_list).extra(order_by=ordering_val)
            if len(queryset)>0:
                new_data = InventorySerializer(data=queryset, many=True)
                new_data.is_valid()
            else:
                queryset = WarehouseInventory.objects.none()
                new_data = InventorySerializer(data=queryset)
                new_data.is_valid()
        except:
            queryset = WarehouseInventory.objects.none()
            new_data = InventorySerializer(data=queryset)
            new_data.is_valid()
        return JsonResponse(new_data.data, safe=False)

class FilterWarehouseOcupancyChoicesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        new_data = ()
        foreign_data = kwargs['field'].split('__')
        if foreign_data[0] == "client":
            field_type = Client._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        if foreign_data[0] == "product":
            field_type = Product._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)

        elif foreign_data[0] == "warehouseentranceconfirmation":
            field_type = WarehouseEntranceConfirmation._meta.get_field(foreign_data[1]).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)        
        else:
            field_type = WarehouseInventory._meta.get_field(kwargs['field']).get_internal_type()
            return JsonResponse({"data": new_data, "field_type": field_type}, safe=False)
        
class DownloadWarehouseOcupancyPdfView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['pdf_ids_list'] != u'[]' and request.POST['pdf_ids_list'] != u'':
            qids = ast.literal_eval(request.POST['pdf_ids_list'])
            queryset = WarehouseInventory.objects.filter(id__in=qids).order_by('client__name')
            # GGV
	    # warehouse_inventory = queryset.values('client__client_code','client__name','client_id').annotate(total_kg=Sum('total_kg'),available_total_boxes= Sum('available_total_boxes'), total_boxes=Sum('total_boxes'), retained_boxes=Sum('retained_boxes'),gross_weight=Sum('warehouse_entrance_pallet__gross_weight') )
            warehouse_inventory = queryset.values('client__client_code','client__name','client_id').annotate(total_kg=Sum('total_kg'),available_total_boxes= Sum('available_total_boxes'), total_boxes=Sum('total_boxes'), retained_boxes=Sum('retained_boxes'),gross_weight=Sum('total_kg') )
            inventory_data = []

            count_total_boxes = 0
            count_available_total_boxes=0
            count_retained_boxes = 0
            count_total_and_retained = 0
            total_kg = 0
            total_gross_weight = 0
            total_pallet_count=0

            for inventory in warehouse_inventory:
                total_and_retained = 0
                total_and_retained1 = 0
                client_inventory = WarehouseInventory.objects.filter(client_id=inventory['client_id'])
                pallet_count = client_inventory.count()
                exitpallets = WarehouseExitPallet.objects.filter(inventory__in=client_inventory, werehouse_exit_confirmation__exit_product_measurement__werehouse_exit__status__in= ['InManeuvers', 'ManeuverComplete'])
                exit_gross_weight = sum([float(confirm.gross_weight) for confirm in exitpallets])
                exit_boxes = sum([float(confirm.boxes) for confirm in exitpallets])
                
                inv_gross_weight = (float(inventory['gross_weight']) + float(exit_gross_weight))
                inv_kg = (int(inventory['available_total_boxes']) + int(exit_boxes))

                # pallet_count = WarehouseInventory.objects.filter(client_id=inventory['client_id'], available_total_boxes__gt=0).count()
                # if inventory['retained_boxes'] != None and inventory['total_boxes'] != None:
                    # total_and_retained1 = float(inventory['total_boxes'] * inventory['retained_boxes'])
                if inventory['retained_boxes'] != None and inv_kg != None:
                    total_and_retained1 = float(inv_kg + inventory['retained_boxes'])
                else:
                   total_and_retained1=0
                if inv_gross_weight != None:
                    total_and_retained = float(inv_gross_weight) - total_and_retained1
                count_total_and_retained+=total_and_retained1
                if pallet_count != 0:
                    total_pallet_count += pallet_count

                if inventory['total_boxes'] != None:
                    count_available_total_boxes+= inv_kg

                if inventory['retained_boxes'] != None:   
                    count_retained_boxes+= inventory['retained_boxes']

                if inventory['total_kg'] != None:
                    total_kg+= inventory['total_kg']

                if inv_gross_weight != None:
                    total_gross_weight+= inv_gross_weight
                    total_and_retained = float(inv_gross_weight) - total_and_retained1

                data = {
                'cliente_code':inventory['client__client_code'],
                'cliente_name':inventory['client__name'],
                'total_boxes': inv_kg,
                # 'ocupacion_tarima': inventory['total_kg'],
                'ocupacion_tarima': pallet_count,
                'total_kg': inventory['total_kg'],
                'retained_boxes': inventory['retained_boxes'],
                # 'total_and_retained': total_and_retained ,
                'total_and_retained': total_and_retained1 ,
                'gross_weight': inv_gross_weight,
                }
                inventory_data.append(data)

            inventory_data_data = {'inventory_data': inventory_data,'total_gross_weight':total_gross_weight,
                'count_available_total_boxes':count_available_total_boxes,
                'count_retained_boxes':count_retained_boxes,'count_total_and_retained':count_total_and_retained,
                'total_pallet_count':total_pallet_count,
                "print_date": datetime.datetime.now().strftime("%Y/%m/%d")}

            pdf = render_to_pdf('pdf/ocupancy_list_pdf.html', inventory_data_data)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Ocupacion_Bodega_%s.pdf"%(datetime.datetime.now().strftime("%Y-%m-%d"))
                if not os.path.exists(filename):
                    os.system('touch %s'%filename)
                filename = os.path.join(settings.MEDIA_ROOT, "warehouse_inventory_reports", filename)
                with open(filename, "w") as file:
                    file.write(response.content)
                return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
            else:
                return JsonResponse({"message": "fail","code":500}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)
                      

class DownloadWarehouseOcupancyView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        if request.POST['ids_list'] != u'[]' and request.POST['ids_list'] != u'':
            qids = ast.literal_eval(request.POST['ids_list'])
            column =[        
        	(u"Codigo del Cliente", 20),
            (u"Descripcion", 20),
            (u"Peso Bruto Total (Kg)", 20),
            (u"Cantidad Disponible", 20),
            (u"Cantidad Retenida",20),
            (u"Cantidad Total",20),
            (u"Ocupación tarimas", 20),        
        	]

            reportData = []
            queryset = WarehouseInventory.objects.filter(id__in=qids).order_by('client__name')        
            #GGV
            #warehouse_inventory = queryset.values('client__client_code','client__name','client_id').annotate(total_kg=Sum('total_kg'), available_total_boxes= Sum('available_total_boxes'),total_boxes=Sum('total_boxes') , retained_boxes=Sum('retained_boxes'),gross_weight=Sum('warehouse_entrance_pallet__gross_weight'))
            warehouse_inventory = queryset.values('client__client_code','client__name','client_id').annotate(total_kg=Sum('total_kg'), available_total_boxes= Sum('available_total_boxes'),total_boxes=Sum('total_boxes') , retained_boxes=Sum('retained_boxes'),gross_weight=Sum('total_kg'))
            count_total_boxes = 0
            count_available_total_boxes=0
            count_retained_boxes = 0
            count_total_and_retained = 0
            total_kg = 0
            total_gross_weight = 0
            total_pallet_count=0

            for obj in warehouse_inventory:
                gross_weight = float(obj["gross_weight"])
                client_inventory = WarehouseInventory.objects.filter(client_id=obj['client_id'])
                pallet_ids = client_inventory.filter(available_total_boxes__gt=0).values_list("id", flat=True)
                exitpallets = WarehouseExitPallet.objects.filter(inventory__in=client_inventory, werehouse_exit_confirmation__exit_product_measurement__werehouse_exit__status__in= ['InManeuvers', 'ManeuverComplete'])
                exit_gross_weight = sum([float(confirm.gross_weight) for confirm in exitpallets])
                exit_boxes = sum([float(confirm.boxes) for confirm in exitpallets])
                inventories_ids = list(pallet_ids)
                pallet_inventory_ids = list(exitpallets.values_list("inventory_id", flat=True))
                pallet_count = len(list(set(inventories_ids + pallet_inventory_ids)))
                retained_count = client_inventory.filter(available_total_boxes=0, retained_boxes__gt=0)
                # for inv in client_inventory:
                #     if inv.available_gross_weight >0:
                #         gross_weight += float(inv.available_gross_weight)

                if float(exit_boxes) >0:
                    inv_gross_weight = (gross_weight + float(exit_gross_weight))
                else:
                    inv_gross_weight = gross_weight

                inv_kg = (float(obj['available_total_boxes']) + float(exit_boxes))
                total_and_retained = 0
                total_and_retained1 = 0
                # if obj['retained_boxes'] != None and obj['total_boxes'] != None:
                #     total_and_retained1 = float(obj['total_boxes'] * obj['retained_boxes'])
                if obj['retained_boxes'] != None and inv_kg != None:
                    total_and_retained1 = float(inv_kg + obj['retained_boxes'])
                else:
                   total_and_retained1=0 
                count_total_and_retained+=total_and_retained1
                pallet_count = pallet_count + len(retained_count)
                if pallet_count != 0:
                   
                    total_pallet_count += pallet_count

                if obj['total_boxes'] != None:
                    # count_total_boxes+= obj['total_boxes']
                    count_available_total_boxes+= inv_kg
                if obj['retained_boxes'] != None:   
                    count_retained_boxes+= obj['retained_boxes']
                
                if obj['total_kg'] != None:
                    total_kg+= obj['total_kg']
                if inv_gross_weight != None:
                    total_gross_weight+= inv_gross_weight
                    total_and_retained = inv_gross_weight - total_and_retained1
                    # count_total_and_retained+=total_and_retained
                
                reportData.append([
                obj['client__client_code'],
                obj['client__name'],
                inv_gross_weight,
                inv_kg,
                obj['retained_boxes'],
                # total_and_retained,
                total_and_retained1,
                # obj['total_kg'],
                pallet_count
                ])

            reportData.append(["","","","","","",""])
            reportData.append(["","Total",total_gross_weight,count_available_total_boxes,count_retained_boxes,count_total_and_retained,total_pallet_count])
            report_name = "Ocupacion_Bodega_%s.xlsx"%(datetime.datetime.now().strftime("%Y_%m_%d"))
            call = GenerateXlsxReport(report_name, column, reportData,'REPORTE DE OCUPACION BODEGA DETALLADO')
            filename = call.generate()
            f = open(filename, 'rb')
            excelfile = File(f)

            response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            filename = "Ocupacion_Bodega_%s.xlsx"%(datetime.datetime.now().strftime("%Y-%m-%d"))
            if not os.path.exists(filename):
                os.system('touch %s'%filename)
            filename = os.path.join(settings.MEDIA_ROOT, "warehouse_inventory_reports", filename)
            with open(filename, "w") as file:
                file.write(response.content)
            # content = "attachment; filename=%s" %(report_name)
            # response['Content-Disposition'] = content
            return JsonResponse({"message": "success","code":200, "file":filename.split('/media')[-1]}, safe=False)
        else:
            return JsonResponse({"message": "fail","code":500}, safe=False)
