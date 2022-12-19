from django.shortcuts import render
import datetime
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from django.views.generic.list import ListView
from catalogs.warehouse.models import Warehouse, WarehouseLocation ,WarehouseSection
from catalogs.clients.models import Client
from .models import WarehouseEntrance, WarehouseEntranceConfirmation,WarehouseEntrancePallet, WProductMeasurement, EntrancePalletPesoVariable
from .forms import (WarehouseEntranceForm,
  WProductMeasurementFormSet,
  WWIncidenceProductFormSet,
  WWIncidenceImageFormset,
  WWIncidenceImageEditFormset,
  WarehouseEntranceConfirmationForm,
  WarehouseEntranceConfirmationFormSet,
  WarehouseEntrancePalletFormSet)
from django.forms import inlineformset_factory
from warehouses.utils import render_to_pdf, render_entrance_pdf
from django.core.urlresolvers import reverse
import time, os, sys
from django.conf import settings
from django.http import JsonResponse


class EntranceDetail(LoginRequiredMixin, UpdateView):
    template_name = 'warehouse/warehouse_entrance/show.html'
    model = WarehouseEntrance
    form_class = WarehouseEntranceForm
    def get_context_data(self, **kwargs):
       context = super(EntranceDetail, self).get_context_data(**kwargs)
       if self.request.POST:
           context['w_product_measurment_form'] = WProductMeasurementFormSet(self.request.POST, instance=self.object)
           context['w_incidence_product_form'] = WWIncidenceProductFormSet(self.request.POST, instance=self.object)
           context['w_incidence_image_form'] = WWIncidenceImageEditFormset(self.request.POST,self.request.FILES, instance=self.object)
           # context['w_entrance_confirmation'] = WarehouseEntranceConfirmationFormSet(self.request.POST, instance=self.object)
           context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(self.request.POST, instance=self.object)
       else:
           context['w_product_measurment_form'] = WProductMeasurementFormSet(instance=self.object)
           context['w_incidence_product_form'] = WWIncidenceProductFormSet(instance=self.object)
           context['w_incidence_image_form'] = WWIncidenceImageEditFormset(instance=self.object)
           # context['w_entrance_confirmation'] = WarehouseEntranceConfirmationFormSet(instance=self.object)
           context['w_entrance_confirmation_pallet'] = WarehouseEntrancePalletFormSet(instance=self.object)
           context['w_incidence_images'] = self.object.wincidenceimage_set.all()
       context['warehouse_location'] = Warehouse.objects.all()
       return context

    def form_valid(self, form):
       self.object = form.save(commit=False)
       context = self.get_context_data()
       w_product_measurment_form = context['w_product_measurment_form']
       w_incidence_product_form = context['w_incidence_product_form']
       w_incidence_image_form = context['w_incidence_image_form']
       # w_entrance_confirmation_form = context['w_entrance_confirmation']
       w_entrance_confirmation_pallet = context['w_entrance_confirmation_pallet']
       
       try:
         if form.is_valid():
             self.object = form.save()
             w_product_measurment_form.instance = self.object
             w_incidence_product_form.instance = self.object
             w_incidence_image_form.instance = self.object
             w_entrance_confirmation_pallet.instance = self.object
             if w_product_measurment_form.is_valid():
                try:
                  w_product_measurment_form.save()
                except:
                  pass

             if w_incidence_product_form.is_valid():
                try:
                  w_incidence_product_form.save()
                except:
                  pass
             if w_incidence_image_form.is_valid():
                try:
                  w_incidence_image_form.save()
                except:
                  pass 
             if w_entrance_confirmation_pallet.is_valid():
                try:
                  w_entrance_confirmation_pallet.save()
                except:
                  pass
             return super(EntranceParamUpdate, self).form_valid(form)
         else:
             return self.render_to_response(self.get_context_data(form=form))
       except:
         return self.render_to_response(self.get_context_data(form=form))


class EntranceDelete(LoginRequiredMixin, DeleteView):
    model = WarehouseEntrance

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse-entrances-list')

class NewEntranceDelete(LoginRequiredMixin, DeleteView):
    model = WarehouseEntrance

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('entrances-list')



class GetWarehousePaletQrcode(ListView):
    model = WarehouseEntrancePallet
    queryset = WarehouseEntrancePallet.objects.all()    
    template_name = 'pdf/warehouse_qrcode_pdf.html'
    
    def get(self, request):
        from sga.render import Render
        import base64, json, pdb
        pallet_data = json.loads(base64.b64decode(self.request.GET.get('qs')))
        ids = []
        for item in pallet_data:
          ids.append(item.get('id'))
          WarehouseEntrancePallet.objects.filter(id=item.get('id')).update(gross_weight=item.get('gross_weight'),net_weight=item.get('net_weight'))
        query_set = WarehouseEntrancePallet.objects.filter(id__in=ids)
        params = {
          'object_list': query_set            
        }
        return Render.render('pdf/entrance_qrcode_pdf.html',params)

class DownloadEntranceInvoiceUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
       self.object = WarehouseEntrance.objects.get(id=kwargs['pk'])
       if self.object.status == "finish":
           measurement_products = WProductMeasurement.objects.filter(werehouse_entrance_id=self.object.id)
           ent_conf = self.object.warehouseentranceconfirmation_set.values_list('id',flat=True)
           # pallet = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation_id__in=ent_conf)
          

           data = {
            'object': self.object,
            'print_datetime': self.object.confirmed_at, 
            'print_entrance_hour': self.object.entrance_hour,
            'entrans_id': self.object.id,
            'customer_name': self.object.customer,
            'client_code': self.object.customer.client_code,
            'transportistas': self.object.carrier,
            'transporte': self.object.vehicle,
            'placas': self.object.license_plate,
            'entrance_confirmation': ent_conf,
            'measurement_products': measurement_products,
            'total_boxes': self.object.get_total_pallet_boxes,
            'total_boxe_kgs': self.object.get_total_pallet_boxes_kgs,
            'total_gross_weight': self.object.get_total_pallet_gross_weight,
            'total_net_weight': self.object.get_total_pallet_net_weight
            }
           pdf = render_entrance_pdf('pdf/new_invoice_entrance.html', data)
           if pdf:
             response = HttpResponse(pdf, content_type='application/pdf')
             filename = "Entrada_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
             content = "attachment; filename=%s" %(filename)
             response['Content-Disposition'] = content
             return response
       else:
          return HttpResponse("Not found")


def update_inventory(entrance_confirmation,calculate_total_weight):
    from catalogs.warehouse.models import  WarehouseInventory,WarehouseLocation
    try:
        for instance in entrance_confirmation.warehouseentranceconfirmation_set.all():
            inventory = WarehouseInventory.objects.filter(product=instance.product,
            warehouse_location__location_number=instance.location,
            client=instance.werehouse_entrance.customer)            
            if inventory.exists():                
                product_measurment = instance.werehouse_entrance.wproductmeasurement_set.filter(product=instance.product).first()
                if inventory.filter(warehouse_entrance_confirmation =instance).exists():
                  rack = inventory.first().warehouse_entrance_confirmation.warehouse.get_section(inventory.first().warehouse_entrance_confirmation.location)
                  inventory.update(
                    total_kg=product_measurment.total_kg,
                    total_boxes=product_measurment.boxes,
                    rack = rack,
                    exp_date=instance.exp_date,
                    retained_boxes=instance.retained_quantity)
                else:
                  rack = inventory.first().warehouse_entrance_confirmation.warehouse.get_section(inventory.first().warehouse_entrance_confirmation.location)
                  inventory.update(
                    total_kg=product_measurment.total_kg,
                    total_boxes=product_measurment.boxes,
                    rack = rack,
                    exp_date=instance.exp_date,
                    warehouse_entrance_confirmation=instance,
                    retained_boxes=instance.retained_quantity)
            else:
                warehouse_location = WarehouseLocation.objects.filter(location_number=instance.location, warehouse=instance.warehouse)
                if warehouse_location.exists():
                    warehouse_location = warehouse_location.first()
                    rack = instance.warehouse.get_section(instance.location)
                    product_measurment = instance.werehouse_entrance.wproductmeasurement_set.filter(product=instance.product).first()
                    WarehouseInventory.objects.create(warehouse_location=warehouse_location,
                    product=instance.product,
                    client=instance.werehouse_entrance.customer,
                    total_kg=product_measurment.total_kg,
                    total_boxes=product_measurment.boxes,
                    exp_date=instance.exp_date,
                    rack=rack,
                    warehouse_entrance_confirmation=instance,
                    retained_boxes=instance.retained_quantity)
            warehouse_numbers = instance.warehouse.id #entrance_confirmation.warehouseentranceconfirmation_set.all().values_list('warehouse', flat=True)
            location_numbers = instance.location #entrance_confirmation.warehouseentranceconfirmation_set.all().values_list('location', flat=True)

            for location in WarehouseLocation.objects.filter(location_number__in=list(location_numbers),warehouse_id=warehouse_numbers):
              location.total_stored_kg = sum(location.warehouseinventory_set.all().values_list('total_kg', flat=True))
              location.total_stored_boxes = sum(location.warehouseinventory_set.all().values_list('total_boxes', flat=True))
              location.total_retained_boxes = sum(location.warehouseinventory_set.all().values_list('retained_boxes', flat=True))
              if calculate_total_weight == 'true':
                boxes = instance.werehouse_entrance.wproductmeasurement_set.filter(product_id=instance.product.id).first().boxes
                location.available_weight = location.available_weight - (instance.product.get_available_weight * boxes)
                location.available_volume =location.available_volume - (instance.product.get_available_volume * boxes)
              location.save()
    except:
        pass


class EntranceResultadoRomaneo(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        entrance = WarehouseEntrance.objects.get(id=kwargs['pk'])
        # pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__w_product_measurement__werehouse_entrance__id=entrance.pk)
        entrance_pallets = EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet__werehouse_entrance_confirmation__w_product_measurement__werehouse_entrance__id=entrance.pk)
        column =[
        (u"Id", 20),
        (u"Cliente", 20),
        (u"Fecha de Entrada", 20),
        (u"Referencia", 20),
        (u"Codigo", 20),
        (u"Descripcion", 20),
        (u"Lote Tarima", 20),
        (u"Peso Bruto", 20)
        ]
        reportData = []
        for entrance_pallet in entrance_pallets:
          pallet = entrance_pallet.werehouse_entrance_pallet
          reportData.append([
          entrance.id,
          entrance.customer.name,
          entrance.created_at.strftime("%Y/%m/%d"),
          entrance.cust_reference,
          pallet.werehouse_entrance_confirmation.w_product_measurement.product.product_code,
          pallet.werehouse_entrance_confirmation.w_product_measurement.product.product_description,
          pallet.palet_lot,
          entrance_pallet.peso_variable_quantity

          ])
        report_name = "Romaneo_Entrada_%s.xlsx"%(entrance.id)
        call = GenerateXlsxReport(report_name, column, reportData,'Romaneo Entrada')
        filename = call.generate()
        f = open(filename, 'rb')
        excelfile = File(f)

        response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        content = "attachment; filename=%s" %(report_name)
        response['Content-Disposition'] = content
        return response
