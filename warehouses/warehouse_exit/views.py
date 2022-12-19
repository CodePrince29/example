from django.shortcuts import render
import datetime
# Create your views here.
import copy 
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import View
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from .models import WarehouseExit, WExitConfirmation,WarehouseExitPallet, ExitPalletPesoVariable
from catalogs.warehouse.models import Warehouse, WarehouseInventory,WarehouseLocation,WarehouseSection

from warehouses.warehouse_entrance.models import WarehouseEntrance,WarehouseEntranceConfirmation,WarehouseEntrancePallet

from warehouses.warehouse_exit.models import WExitProductMeasurement
from django.db.models.functions import Cast, Coalesce
from django.db.models import Sum, Q

# from catalogs.warehouse.models import Warehouse
from .forms import (WarehouseExitForm,
  WExitProductMeasurementFormSet,
  WExitConfirmationFormSet,
  WExitConfirmationForm,
  WarehouseExitPalletFormSet,
  WarehouseExitPalletMFormset,)
from django.utils.translation import ugettext_lazy as _
from .serializers import (WarehouseEntranceFilterSerializer, WarehouseSerializer,WarehouseEntranceConfirmationSerializer,)

from warehouses.utils import render_to_pdf, render_entrance_pdf
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.template import loader
from catalogs.clients.models import Client
from catalogs.product.models import Product
from rest_framework.permissions import IsAuthenticated, BasePermission
import json, pdb
from ast import literal_eval



class ExitDelete(LoginRequiredMixin, DeleteView):
    model = WarehouseExit

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse-exit-list')

class ExitParamShow(LoginRequiredMixin, UpdateView):
    template_name = 'warehouse/warehouse_exit/show.html'
    model = WarehouseExit
    form_class = WarehouseExitForm
    def get_context_data(self, **kwargs):
       context = super(ExitParamShow, self).get_context_data(**kwargs)
       context['w_exit_product_measurment_form'] = WExitProductMeasurementFormSet(instance=self.object)
       # context['w_exit_confirmation_form_set'] = WExitConfirmationFormSet(instance=self.object)
       context['w_exit_confirmation_pallet'] = WarehouseExitPalletFormSet(instance=self.object)
       context['warehouse_location'] = Warehouse.objects.all()
       return context



class DownloadExitInvoiceUpdate(LoginRequiredMixin, View):
  
  def get(self, request, *args, **kwargs):
    from django.utils import timezone
    import pytz
    timezone.activate(pytz.timezone("America/Mexico_City"))
    confirmed_at = timezone.localtime(timezone.now())
    self.object = WarehouseExit.objects.get(id=kwargs['pk'])
    # measurement_products = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.object.id)

    measurement_query = WExitProductMeasurement.objects.filter(werehouse_exit_id=self.object.id).order_by('product__product_code')
    measurement_products = measurement_query.values('product_id', 'product_description', 'product__product_code').annotate(total_boxes=Coalesce(Sum('wexitconfirmation__warehouseexitpallet__boxes'), 0),total_gross_weight=Coalesce(Sum('wexitconfirmation__warehouseexitpallet__gross_weight'), 0))

    data = {
      'object': self.object,
      'print_datetime': confirmed_at, 
      'entrans_id': self.object.id,
      'customer_name': self.object.customer,
      'client_code': self.object.customer.client_code,
      'transportistas': self.object.carrier,
      'transporte': self.object.vehicle,
      'placas': self.object.license_plate,
      'measurement_products': measurement_products,
      'total_boxe_kgs': self.object.get_total_pallet_boxes_kgs,
      'total_boxes': self.object.get_total_pallet_boxes,
      'total_gross_weight': self.object.get_total_pallet_gross_weight,
      'total_net_weight': self.object.get_total_pallet_net_weight
      }

    pdf = render_entrance_pdf('pdf/new_invoice_exit.html', data)
    if pdf:
      response = HttpResponse(pdf, content_type='application/pdf')
      filename = "Salida_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
      content = "attachment; filename=%s" %(filename)
      response['Content-Disposition'] = content
      return response
    else:
      return HttpResponse("Not found")

def get_warehouse_locations(request,pk):
  warehouse = Warehouse.objects.get(id=pk)
  warehouse_html = loader.render_to_string('warehouse/warehouse_content.html',{'warehouse': warehouse})
  locations_data = {'warehouse': warehouse_html}
  return JsonResponse(locations_data, safe=False)

def get_warehouse_exit_locations(request):
  request_data = request.POST
  warehouse = request_data.get('warehouse')
  product = request_data.get('product_id')

  warehouse = Warehouse.objects.get(id=warehouse)
  if product == None :
    warehouse_html = loader.render_to_string('warehouse/warehouse_exit_content.html',{'warehouse': warehouse})
  else:    
    warehouse_html = loader.render_to_string('warehouse/warehouse_content_exit.html',{'warehouse': warehouse,'product': product})

  locations_data = {'warehouse': warehouse_html}
  return JsonResponse(locations_data, safe=False)

def get_location_for_manage(request,pk):
  warehouse = Warehouse.objects.get(id=pk)
  warehouse_html = loader.render_to_string('warehouse/warehouse_location_manage.html',{'warehouse': warehouse})
  locations_data = {'warehouse': warehouse_html}
  return JsonResponse(locations_data, safe=False)


def get_warehouse_detail(invt,boxes,gross_weight,net_weight):
  return  {
         "id": invt.id,
         "inventory_gross_weight": invt.available_gross_weight,
         "inventory_net_weight": invt.available_net_weight,
         "available_total_boxes": boxes,
         "pallet_lot": invt.warehouse_entrance_pallet.palet_lot,
         "warehouse": invt.warehouse_entrance_pallet.warehouse.id,
         "location":invt.warehouse_entrance_pallet.location.id ,
         "rack_number":invt.warehouse_entrance_pallet.rack_number.id,
         "cost_lot": invt.warehouse_entrance_pallet.cost_lot ,
         "exp_date": invt.warehouse_entrance_pallet.exp_date ,
         "gross_weight": gross_weight,
         "net_weight": net_weight,
         "invoice_weight": invt.warehouse_entrance_pallet.invoice_weight,
         "retained_quantity": invt.warehouse_entrance_pallet.retained_quantity,
         "retained_reason": invt.warehouse_entrance_pallet.retained_reason,
         "box_kg": round(invt.total_kg,2),
         "total_kg": invt.total_kg,
         "packages_per_pallet": invt.product.packages_per_pallet ,
         "available_boxes": invt.available_total_boxes,

         "warehouse_name": invt.warehouse_entrance_pallet.warehouse.code,
         "location_name":invt.warehouse_entrance_pallet.location.location_number ,
         "rack_name":invt.warehouse_entrance_pallet.rack_number.index,
         "pallet_id":invt.warehouse_entrance_pallet.id,
       }

def responce_inventory_data(inventory,available_box):
    
    return {
    "inventory": inventory['id'],
    "boxes": available_box,
    "inventory_gross_weight": inventory['inventory_gross_weight'],
    "inventory_net_weight": inventory['inventory_net_weight'],
    "pallet": inventory['pallet_lot'],
    "warehouse":inventory['warehouse'],
    "location": inventory['location'],
    "rack_number": inventory['rack_number'],
    "cost_lot":  inventory['cost_lot'],
    "exp_date":  inventory['exp_date'],
    "gross_weight": round(inventory['gross_weight'] * available_box,2),
    "net_weight":  round(inventory['net_weight']* available_box,2) ,
    "invoice_weight":  inventory['invoice_weight'],
    "retained_quantity":  inventory['retained_quantity'],
    "retained_reason":  inventory['retained_reason'],
    "box_kg": inventory['box_kg'],
    "warehouse_name": inventory['warehouse_name'],
    "location_name": inventory['location_name'],
    "rack_name": inventory['rack_name'],
    "pallet_id":inventory['pallet_id'],
    }

def FilterPickerResponse(inventories, request):
  request_boxes = float(request.POST.get('request_boxes'))
  current_user = request.user.id
  inventory_boxes = 0
  inventory_data = []
  
  for invt in inventories:
    gross_weight = round((float(invt.warehouse_entrance_pallet.gross_weight) / float(invt.warehouse_entrance_pallet.boxes)),2)
    net_weight = round((float(invt.warehouse_entrance_pallet.net_weight) / float(invt.warehouse_entrance_pallet.boxes)),2)
    if request.session.get('%s-%s'%(invt.id, current_user)) == None:
      inventory_boxes += invt.available_total_boxes
      if invt.available_total_boxes > 0:        
        inv_hash = get_warehouse_detail(invt,invt.available_total_boxes,gross_weight,net_weight)
        inventory_data.append(inv_hash)
    else:
      inventory_boxes += request.session.get('%s-%s'%(invt.id, current_user))
      if request.session.get('%s-%s'%(invt.id, current_user)) >0:        
        inv_hash = get_warehouse_detail(invt,request.session.get('%s-%s'%(invt.id, current_user)),gross_weight,net_weight)
        inventory_data.append(inv_hash)
  responce_data = []
  
  if inventory_boxes < request_boxes:
    return JsonResponse({"status": "false","code": 500, "boxes": inventory_boxes}, safe=False)
  else:

    for inventory in inventory_data:
      
      palet = inventory['packages_per_pallet']
      available_box = request.session.get('%s-%s'%(inventory['id'], current_user))

      if not available_box:
        available_box = inventory['available_total_boxes']
        request.session['%s-%s'%(inventory['id'], current_user)] = available_box        
      if available_box and available_box < 0:
        request.session['%s-%s'%(inventory['id'], current_user)] = inventory['available_total_boxes']
        available_box = inventory['available_total_boxes']
      if(request_boxes >= available_box):
        data = responce_inventory_data(inventory,available_box)
        responce_data.append(data)
        if not inventory['available_total_boxes']==available_box:
          request.session['%s-%s'%(inventory['id'], current_user)] = request_boxes - available_box
        else:
          request.session['%s-%s'%(inventory['id'], current_user)]= inventory['available_total_boxes']-available_box
        if request_boxes == available_box:
          break
        else:
          request_boxes-= available_box
          continue  
            
      else:
        if request_boxes>0:            
          inv_kg = inventory['total_kg']
          
          total_boxes = inv_kg/palet
          data = responce_inventory_data(inventory,request_boxes)          
          responce_data.append(data)
            
          if request.session.get('%s-%s'%(inventory['id'], current_user)):
            if request.session.get('%s-%s'%(inventory['id'], current_user)) > request_boxes:
              request.session['%s-%s'%(inventory['id'], current_user)] = request.session.get('%s-%s'%(inventory['id'], current_user), 0) - request_boxes
            else:
              request.session['%s-%s'%(inventory['id'], current_user)] = request_boxes - request.session.get('%s-%s'%(inventory['id'], current_user), 0)
          break
        else:
          break
          pass
    responce_data = [dict(t) for t in {tuple(d.items()) for d in responce_data}]
    return JsonResponse({"status": "true","code": 200 , "responcedata": responce_data}, safe=False)



class WarehouseFilterAPI(LoginRequiredMixin, View):
  permission_classes = (IsAuthenticated,)
  def post(self, request, *args, **kwargs):
      match = ["werehouse_entrance_confirmation__werehouse_entrance_id", "werehouse_entrance_confirmation__werehouse_entrance__cust_reference", "exp_date", "cost_lot", "palet_lot","werehouse_entrance_confirmation__product_id"]
      hash_data = {}
      product = False
      [hash_data.update({"%s"%key: value }) for key,value in request.POST.items() if key in match and value not in [None, '']]
      order_by = ['exp_date','warehouse_entrance_pallet_id']
      inventories_ids = WarehouseEntrancePallet.objects.filter(**hash_data).values_list('warehouseinventory', flat=True)
      inventories = WarehouseInventory.objects.filter(available_total_boxes__gt=0, id__in=inventories_ids).order_by(*order_by)

      return FilterPickerResponse(inventories, request)

class CheckRetainedQuantity(LoginRequiredMixin, View):
  permission_classes = (IsAuthenticated,)
  def post(self, request, *args, **kwargs):
    
    inventory_id  = json.loads(request.POST.get('inventory_id'))
    exit_retained_quantity  = json.loads(request.POST.get('retained_quantity'))
    if inventory_id != '':
      inventory_id = int(inventory_id)
      inventories = WarehouseInventory.objects.filter(id = inventory_id)
      if inventories.exists():
        inventory = inventories.first()
        entrance_retained_quantity = inventory.warehouse_entrance_pallet.retained_quantity
        if entrance_retained_quantity < exit_retained_quantity:
          responce_data = {'entrance_retained_quantity':entrance_retained_quantity}
          return JsonResponse({"status": "true","code": 500 , "data": responce_data}, safe=False)
    return JsonResponse({"status": "true","code": 200 }, safe=False)




class PrintPickingView(LoginRequiredMixin, UpdateView):
    model = WarehouseExit
    form_class = WarehouseExitForm
    def get_context_data(self, **kwargs):
       context = super(PrintPickingView, self).get_context_data(**kwargs)

       WExitConfirmationFormSet = inlineformset_factory(WarehouseExit, WExitConfirmation
    ,extra=0, min_num=len(self.object.wexitproductmeasurement_set.all()), form=WExitConfirmationForm,can_delete=True)

       
       if self.request.POST:
          context['w_exit_product_measurment_form'] = WExitProductMeasurementFormSet(self.request.POST, instance=self.object)
          context['w_exit_confirmation_pallet'] = WarehouseExitPalletFormSet(self.request.POST, instance=self.object)
       return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        context = self.get_context_data()
        w_exit_product_measurment_form = context['w_exit_product_measurment_form']
        w_exit_confirmation_pallet = context['w_exit_confirmation_pallet']
        # w_exit_confirmation_pallet = context['w_exit_confirmation_pallet']
        if form.is_valid():
             self.object = form.save()
             w_exit_product_measurment_form.instance = self.object
             w_exit_confirmation_pallet.instance = self.object
             if w_exit_product_measurment_form.is_valid():
                try:
                  w_exit_product_measurment_form.save()
                except:
                  pass
             if w_exit_confirmation_pallet.is_valid():
                try:
                  w_exit_confirmation_pallet.save()
                except:
                  pass
             conf = self.object.wexitconfirmation_set.all().values_list('id',flat=True)                 
             exit_pallet = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation_id__in=conf)
             data = {
                  'object': self.object,
                  'print_datetime': self.object.exit_date, 
                  'entrans_id': self.object.id,
                  'customer_name': self.object.customer,
                  'client_code': self.object.customer.client_code,
                  'transportistas': self.object.carrier,
                  'transporte': self.object.vehicle,
                  'placas': self.object.license_plate,
                  'entrance_confirmation': exit_pallet,
                  'total_boxes': self.object.get_total_pallet_boxes,
                  'total_gross_weight': self.object.get_total_pallet_gross_weight,
                  'total_net_weight': self.object.get_total_pallet_net_weight,
                  'get_total_kgs': self.object.get_pallet_total_kgs,
                  
                }
             
             pdf = render_to_pdf('pdf/print_picking.html', data)
             if pdf:
               response = HttpResponse(pdf, content_type='application/pdf')
               filename = "Salida_%s_%s.pdf" %(self.object.id, datetime.datetime.now().strftime("%Y%m%d"))
               content = "attachment; filename=%s" %(filename)
               response['Content-Disposition'] = content
               return response

class AutoPickingView(LoginRequiredMixin, View):
  permission_classes = (IsAuthenticated,)
  def post(self, request, *args, **kwargs):
    from catalogs.warehouse.models import WarehouseInventory ,WarehouseLocation
    customer = request.POST.get('customer')
    product = request.POST.get('product')
    # from django.forms.models import model_to_dict
    order_by = ['exp_date','warehouse_entrance_pallet_id']
    inventories = WarehouseInventory.objects.filter(available_total_boxes__gt=0,product__id=product,client=customer).order_by(*order_by)
    return FilterPickerResponse(inventories, request)



class ClearSession(LoginRequiredMixin, View):
  def get(self, request):
    current_user = request.user.id
    for key in request.session.keys():
      lenk = key.split("-")
      if len(lenk) > 1 and int(lenk[1]) == current_user:
        print(key)
        del request.session[key]
    return JsonResponse({'message': 'clear sessions', 'code': 200})

class AutoPrintPickingView(LoginRequiredMixin, View):
  permission_classes = (IsAuthenticated,)
  def post(self, request, *args, **kwargs):
    match = ["werehouse_entrance_confirmation__werehouse_entrance_id", "werehouse_entrance_confirmation__werehouse_entrance__cust_reference", "exp_date", "cost_lot", "palet_lot","werehouse_entrance_confirmation__product_id"]
    hash_data = {}
    data_response = []
    request_data = literal_eval(request.POST.get('data'))
    for item in request_data:
      whm_boxes = item['whm_boxes']
      whm_total_kg = item['whm_total_kg']
      product_id = item['product_id']
      customer_id = item['customer_id']

      for key,value in item.items():
        # if(key == "product_id" and value not in [None, '']):
        #   hash_data.update({"werehouse_entrance_confirmation__product_id": value })
        if(key == "werehouse_entrance_id" and value not in [None, '']):
          hash_data.update({"werehouse_entrance_confirmation__werehouse_entrance_id": value })
        else:
          if key in match and value not in [None, '']:
            hash_data.update({"%s"%key: value })

      order_by = ['exp_date','warehouse_entrance_pallet_id']
      inventories_ids = WarehouseEntrancePallet.objects.filter(**hash_data)
      inventories_ids = inventories_ids.filter(werehouse_entrance_confirmation__product_id= product_id ).values_list('warehouseinventory', flat=True)
      inventories = WarehouseInventory.objects.filter(available_total_boxes__gt=0, id__in=inventories_ids).order_by(*order_by)
      if len(hash_data) > 0 and inventories.exists():
        data_response.append(get_inventory_detail(inventories, whm_boxes, product_id))
      else:
        order_by = ['exp_date','warehouse_entrance_pallet_id']
        inventories = WarehouseInventory.objects.filter(available_total_boxes__gt=0,product__id=product_id,client=customer_id).order_by(*order_by)
        if inventories.exists():
          data_response.append(get_inventory_detail(inventories, whm_boxes, product_id))
        else:
          product = Product.objects.get(id= product_id )
          data_response.append({"status": "false","code": 500, "boxes": 0, 'product_code': product.product_code, 'product_desc': product.product_description, 'product_id': product_id, 'request_boxes': whm_boxes })

    from operator import is_not
    from functools import partial
    data_response = list(filter(partial(is_not, None), data_response))
    return JsonResponse({"data": data_response})   


def get_inventory_detail(inventories, request_boxes, product_id):
  product = Product.objects.get(id= product_id )
  inventory_boxes = 0
  for invt in inventories:
    inventory_boxes += invt.available_total_boxes
  if inventory_boxes >= int(float(request_boxes)):
    return {"status": "true","code": 200, "boxes": inventory_boxes, 'product_code': product.product_code, 'product_desc': product.product_description, 'product_id': product_id, 'request_boxes': request_boxes }
  else:
    return {"status": "false","code": 500, "boxes": inventory_boxes, 'product_code': product.product_code, 'product_desc': product.product_description, 'product_id': product_id, 'request_boxes': request_boxes }

class ExitResultadoRomaneo(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        from reportes.utility import GenerateXlsxReport
        from django.core.files import File
        import ast
        exit = WarehouseExit.objects.get(id=kwargs['pk'])
        # pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation__exit_product_measurement__werehouse_exit__id=exit.pk)
        exit_pallets = ExitPalletPesoVariable.objects.filter(werehouse_exit_pallet__werehouse_exit_confirmation__exit_product_measurement__werehouse_exit__id=exit.pk)
        column =[
        (u"Id", 20),
        (u"Cliente", 20),
        (u"Fecha de Salida", 20),
        (u"Referencia", 20),
        (u"Codigo", 20),
        (u"Descripcion", 20),
        (u"Lote Tarima", 20),
        (u"Peso Bruto", 20)
        ]
        reportData = []
        for exit_pallet in exit_pallets:
          pallet = exit_pallet.werehouse_exit_pallet
          reportData.append([
          exit.id,
          exit.customer.name,
          exit.created_at.strftime("%Y/%m/%d"),
          exit.cust_reference,
          pallet.werehouse_exit_confirmation.exit_product_measurement.product.product_code,
          pallet.werehouse_exit_confirmation.exit_product_measurement.product.product_description,
          pallet.palet_lot,
          exit_pallet.peso_variable_quantity

          ])
        report_name = "Romaneo_Salida_%s.xlsx"%(exit.id)
        call = GenerateXlsxReport(report_name, column, reportData,'Romaneo Salida')
        filename = call.generate()
        f = open(filename, 'rb')
        excelfile = File(f)

        response = HttpResponse(excelfile, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        content = "attachment; filename=%s" %(report_name)
        response['Content-Disposition'] = content
        return response
