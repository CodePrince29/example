# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic import View
import json
from django.http import JsonResponse
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
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from warehouses.warehouse_entrance.api.serializers import WarehouseEntrancePalletSerializer
from rest_framework.permissions import IsAuthenticated, BasePermission
from ast import literal_eval

class Trazabilidad(LoginRequiredMixin, ListView):
    template_name = 'reportes/trazabilidad/index.html'
    model = WarehouseEntrancePallet
    queryset = WarehouseEntrancePallet.objects.none()
    def get_context_data(self, **kwargs):
    	context = super(Trazabilidad, self).get_context_data(**kwargs)
    	Client
        context['customers'] = Client.objects.all()
        context['products'] = Product.objects.all()
    	return context

class TrazabilidadReportView(CreateAPIView):
    queryset = WarehouseEntrancePallet.objects.all()
    serializer_class = WarehouseEntrancePalletSerializer
    # permission_classes = (IsAuthenticated, IsCustomerInSGA)
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        from rest_framework.response import Response
        hash_data = {}
        queryset_entrance = ()
        
        request_data = request.POST
        

        for key,value in request_data.items():
            if(key == "product" and value not in [None, '']):
              hash_data.update({"werehouse_entrance_confirmation__w_product_measurement__product_id": value })
            if(key == "entrance_id" and value not in [None, '']):
              hash_data.update({"werehouse_entrance_confirmation__w_product_measurement__werehouse_entrance_id": value })
            if(key == "client" and value not in [None, '']):
              hash_data.update({"werehouse_entrance_confirmation__w_product_measurement__werehouse_entrance__customer_id": value })

            if(key == "exp_date" and value not in [None, '']):
              hash_data.update({"exp_date": value })

            if(key == "lote_tarima" and value not in [None, '']):
              hash_data.update({"palet_lot": value })
            if(key == "lote_cliente" and value not in [None, '']):
              hash_data.update({"cost_lot": value })

        query_set = WarehouseEntrancePallet.objects.filter(**hash_data)
        responce_data = []
        for pallet in query_set:

            inventories = WarehouseInventory.objects.filter(warehouse_entrance_pallet_id=pallet.id)
            inventory = inventories.values('available_gross_weight', 'available_total_boxes').aggregate(available_gross_weight=Coalesce(Sum('available_gross_weight'), 0), available_total_boxes=Coalesce(Sum('available_total_boxes'), 0))

            data = []
            data.append(pallet.werehouse_entrance_confirmation.w_product_measurement.werehouse_entrance_id)
            data.append(pallet.werehouse_entrance_confirmation.w_product_measurement.werehouse_entrance.entrance_date)
            data.append(pallet.palet_lot)
            data.append( pallet.werehouse_entrance_confirmation.w_product_measurement.werehouse_entrance.customer.name)
            data.append(pallet.werehouse_entrance_confirmation.w_product_measurement.product.product_code)
            data.append(pallet.boxes)
            data.append(pallet.retained_quantity)
            data.append(inventory['available_gross_weight'])
            data.append(inventory['available_total_boxes'])
            
            
            if pallet.location:
                data.append(pallet.location.shortcode)
            else:
                data.append("")
            url = "<a role='button' href='/trazabilidad_reporte/trazabilidad-generate-report/{}/' class='btn btn-success'><i class='fa fa-edit'></i></a>"
            data.append(url.format(pallet.id))

            responce_data.append(data)
        return Response(responce_data)

class DownloadTrazabilidadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        from warehouses.reserve_inventory.models import ReserveInventory
        from warehouses.warehouse_relocation.models import WarehouseRelocation
        import ast
        entrance_pallet = WarehouseEntrancePallet.objects.get(pk=kwargs['pallet'])
        
        pallet_lot = entrance_pallet.palet_lot
        exit_pallets = WarehouseExitPallet.objects.filter(palet_lot= pallet_lot )

        column =[        
    	(u"Lote Tarima", 20),
        (u"Tipo Movimiento", 20),
        (u"Movimiento", 20),
        (u"Folio", 20),
        (u"Fecha",20),
        (u"Hora",20),
        (u"Cajas", 20),
        (u"Kg", 20), 
        (u"Usuario", 20),
    	]
        reportData = []
        entrance = entrance_pallet.werehouse_entrance_confirmation.w_product_measurement.werehouse_entrance
        created_by = ""
        if entrance.created_by:
            created_by = entrance.created_by.username

        sent_to_maniobras_by = ""
        if entrance.sent_to_maniobras_by:
            sent_to_maniobras_by = entrance.sent_to_maniobras_by.username

        confirmed_by = ""
        if entrance.confirmed_by:
            confirmed_by = entrance.confirmed_by.username

        data = [pallet_lot, "Entrada", "Capture Mesa Control", entrance.id, entrance.entrance_date, entrance.entrance_hour,entrance.boxes, entrance.total_kg, created_by ]
        reportData.append(data)
        sent_to_maniobras_at_date = ""
        sent_to_maniobras_at_time = ""
        maniobras_completed_by = ""
        if entrance_pallet.maniobras_completed_by:
            maniobras_completed_by = entrance_pallet.maniobras_completed_by.username

        if entrance_pallet.sent_to_maniobras_at:
            sent_to_maniobras_at_date = entrance_pallet.sent_to_maniobras_at.strftime("%Y-%M-%d")
            sent_to_maniobras_at_time = entrance_pallet.sent_to_maniobras_at.strftime("%I:%M %p")
        data = [pallet_lot, "Entrada", "Recibo Almacén", entrance.id, sent_to_maniobras_at_date, sent_to_maniobras_at_time,entrance_pallet.boxes, entrance_pallet.gross_weight, sent_to_maniobras_by ]
        reportData.append(data)        

        entrance_confirmed_date = ""
        entrance_confirmed_time = ""
        if entrance.confirmed_at:
            entrance_confirmed_date = entrance.confirmed_at.strftime("%Y-%M-%d")
            entrance_confirmed_time = entrance.confirmed_at.strftime("%I:%M %p")

        maniobras_completed_date = ""
        maniobras_completed_time = ""
        if entrance_pallet.maniobras_completed_at:
            maniobras_completed_date = entrance_pallet.maniobras_completed_at.strftime("%Y-%M-%d")
            maniobras_completed_time = entrance_pallet.maniobras_completed_at.strftime("%I:%M %p")   
        data = [pallet_lot, "Entrada", "Confirmación de Maniobra", entrance.id, maniobras_completed_date, maniobras_completed_time,entrance_pallet.boxes, entrance_pallet.gross_weight, maniobras_completed_by ]
        reportData.append(data)
        data = [pallet_lot, "Entrada", "Confirmación de Entrada", entrance.id, entrance_confirmed_date, entrance_confirmed_time,entrance_pallet.boxes, entrance_pallet.gross_weight, confirmed_by ]
        reportData.append(data)
        
        for exit_pallet in exit_pallets:

            exit = exit_pallet.werehouse_exit_confirmation.exit_product_measurement.werehouse_exit
            exit_completed_by = ""
            if exit.confirmed_by:
                exit_completed_by = exit.confirmed_by.username

            exit_maniobras_completed_by = ""
            if exit_pallet.maniobras_completed_by:
                exit_maniobras_completed_by = exit_pallet.maniobras_completed_by.username

            data = [pallet_lot, "Salida", "Captura Mesa de Control", exit.id, exit.created_at.strftime("%Y-%M-%d"), exit.created_at.strftime("%I:%M %p"),exit.get_total_pallet_boxes, exit.get_pallet_total_kgs, exit.created_by.username ]
            reportData.append(data)
            maniobras_completed_date = ""
            maniobras_completed_time = ""
            if exit_pallet.maniobras_completed_at:
                maniobras_completed_date = exit_pallet.maniobras_completed_at.strftime("%Y-%M-%d")
                maniobras_completed_time = exit_pallet.maniobras_completed_at.strftime("%I:%M %p")
            data = [pallet_lot, "Salida", "Confirmación de Maniobra", exit.id, maniobras_completed_date, maniobras_completed_time,exit_pallet.boxes, exit_pallet.gross_weight, exit_maniobras_completed_by ]
            reportData.append(data)
            exit_confirmed_date = ""
            exit_confirmed_time = ""
            if exit.confirmed_at:
                exit_confirmed_date = exit.confirmed_at.strftime("%Y-%M-%d")
                exit_confirmed_time = exit.confirmed_at.strftime("%I:%M %p")

            data = [pallet_lot, "Salida", "Confirmación de Salida", exit.id, exit_confirmed_date, exit_confirmed_time,exit.boxes, exit_pallet.gross_weight, exit_completed_by ]
            reportData.append(data)
        reallocations = WarehouseRelocation.objects.filter(palet_lot=pallet_lot)
        for reallocation in reallocations:
            rellocation_entrance = reallocation.werehouse_entrance
            
            reallocation_created_by = ""
            if reallocation.created_by:
                reallocation_created_by = reallocation.created_by.username
            data = [pallet_lot, "Concentración", "Concentración de Tarimas", rellocation_entrance.id, reallocation.created_at.strftime("%Y-%M-%d"), reallocation.created_at.strftime("%I:%M %p"),rellocation_entrance.boxes, rellocation_entrance.total_kg, reallocation_created_by ]
            reportData.append(data)


        reserve_inv = ReserveInventory.objects.filter(palet_lot=pallet_lot)
        for reserve in reserve_inv:
            res_created_by = ""
            if reserve.created_by:
                res_created_by = reserve.created_by.username
            data = [pallet_lot, "Retención", "Retención de Producto", reserve.id, reserve.created_at.strftime("%Y-%M-%d"), reserve.created_at.strftime("%I:%M %p"),reserve.reserve_boxes,"", res_created_by]
            reportData.append(data)
            total_retained = reserve.reserve_boxes - reserve.released_store_box
            data = [pallet_lot, "Retención", "Liberación de Producto", reserve.id, reserve.created_at.strftime("%Y-%M-%d"), reserve.created_at.strftime("%I:%M %p"),total_retained,"", res_created_by]
            reportData.append(data)
        inv = entrance_pallet.warehouseinventory_set.all().last()
        if inv:
            data = [pallet_lot, "Inventario", "Inventario Físico de Almacén", inv.id, entrance_confirmed_date, entrance_confirmed_time,inv.total_boxes,"", confirmed_by ]
            reportData.append(data)
            data = [pallet_lot, "Inventario", "Ajuste de información de inventario", inv.id, inv.updated_at.strftime("%Y-%M-%d"), inv.updated_at.strftime("%I:%M %p"),inv.total_boxes,"", confirmed_by ]
            reportData.append(data)
        report_name = "Trazabilidad_%s.xlsx"%(entrance_pallet.palet_lot)
        call = GenerateXlsxReport(report_name, column, reportData,'Romaneo Salida')
        filename = call.generate()
        f = open(filename, 'rb')
        excelfile = File(f)

        response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        content = "attachment; filename=%s" %(report_name)
        response['Content-Disposition'] = content
        return response