from rest_framework import viewsets
from .serializers import WarehouseLocationSerializer, WExitConfirmationSerializer, PalletPesoVariableSerializer, EntrancePalletPesoVariableSerializer, WarehousePalletConfSerializer
from catalogs.warehouse.models import Warehouse, WarehouseLocation
from warehouses.warehouse_exit.models import WExitConfirmation ,WExitProductMeasurement, WarehouseExit, ExitPalletPesoVariable, WarehouseExitPallet
import pdb
from catalogs.product.models import *

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from warehouses.warehouse_entrance.models import *
import json
from django.db import transaction

class WarehouseLocationsAPIView(viewsets.ModelViewSet):
	queryset = WarehouseLocation.objects.all()
	serializer_class = WarehouseLocationSerializer
	def get_queryset(self):
		warehouse = Warehouse.objects.get(id=self.kwargs['pk'])
		queryset = warehouse.warehouselocation_set.order_by('id')
		return queryset

class WarehouseLocationsConfirmationAPIView(viewsets.ModelViewSet):
	queryset = WExitConfirmation.objects.all()
	serializer_class = WExitConfirmationSerializer
	def get_queryset(self):
		warehouse = WarehouseExit.objects.get(id=self.kwargs['pk'])
		queryset = warehouse.wexitconfirmation_set.order_by('id')
		return queryset

@csrf_exempt
def save_exit_pallet(request):
  confirm_data = json.loads(request.POST.get('confirmation_array'))
  request_data = json.loads(request.POST['pallet_arr'])
  for validate_pallet in request_data:
    if validate_pallet['warehouse_location'] in ['', 'None', 'undefined']:
       return JsonResponse({'code': 500, 'error': 'Please fill all data'})
    elif validate_pallet['rack_number'] in ['', 'None', 'undefined']:
      return JsonResponse({'code': 500, 'error': 'Please fill all data'})
    elif validate_pallet['warehouse'] in ['', 'None', 'undefined']:
      return JsonResponse({'code': 500, 'error': 'Please fill all data'})

  if confirm_data:
    w_confirmation_id = confirm_data[0]['w_confirmation_id']
    w_confirmations = WExitConfirmation.objects.filter(pk=w_confirmation_id)
    if w_confirmations.exists():
      w_confirmations.update(
        cost_lot = confirm_data[0]['cost_lot'],
        exp_date = confirm_data[0]['exp_date'],
        gross_weight = confirm_data[0]['gross_weight'],
        net_weight = confirm_data[0]['net_weight'],
        invoice_weight = confirm_data[0]['invoice_weight'],
        retained_quantity = confirm_data[0]['retained_quantity'],
        retained_reason = confirm_data[0]['warehouse_retained_reason'])
  
  if request.POST.get('pallet_type','') == "existing":
    measurement_data = json.loads(request.POST['measurement_data'])
    if measurement_data.get('measurement_id',False) !="N/A":
      WExitProductMeasurement.objects.filter(pk=measurement_data['measurement_id']).update(total_kg = measurement_data['total_kg'],price = measurement_data['total_price'],kg_per_price = measurement_data['kg_per_price'],boxes = measurement_data['boxes'],kg_per_boxes = measurement_data['kg_per_boxes'])
    
    
    for pallet in request_data:

      if pallet['palet_id'] =="" and pallet['is_deleted'] == False:
        try:
          WarehouseExitPallet.objects.create(palet_lot=pallet['palet_lot'],
            boxes=pallet['boxes'],
            box_kg=pallet['box_kg'],
            warehouse_id=pallet['warehouse'],
            rack_number_id=pallet['rack_number'],
            location_id=pallet['warehouse_location'],
            cost_lot=pallet['cost_lot'],
            exp_date=pallet['exp_date'],
            gross_weight=pallet['gross_weight'],
            net_weight=pallet['net_weight'],
            invoice_weight=pallet['invoice_weight'],
            retained_quantity=pallet['retained_quantity'],
            retained_reason=pallet['retained_reason'],
            werehouse_exit_confirmation_id=pallet['w_exit_conf'],
            inventory_id=pallet['inventory'])
        except Exception as ex:
          return JsonResponse({'code': 500, 'error': str(ex)})
        # perform inventory boxes reduction
        inventory = WarehouseInventory.objects.get(pk=pallet['inventory'])
        if int(pallet['boxes']) < inventory.available_total_boxes:
          inventory.available_total_boxes = inventory.available_total_boxes - int(pallet['boxes'])
        else:
          inventory.available_total_boxes = 0
        inventory.save()
        if request.session.get('%s-%s'%(inventory.id, request.user)):
          del request.session['%s-%s'%(inventory.id, request.user)]
      elif pallet['palet_id'] =="" and pallet['is_deleted'] == True:
        pass      
      else:
        pallet_data = WarehouseExitPallet.objects.filter(pk=pallet['palet_id'])
        pallets = pallet_data.first()
        if pallet['is_deleted'] ==False:
          # perform inventory boxes reduction
          if pallets.inventory.id == int(pallet['inventory']):
            inventory = WarehouseInventory.objects.get(pk=pallet['inventory'])

            if int(pallet['boxes']) < pallets.boxes:
              boxes = pallets.boxes - int(pallet['boxes'])
              inventory.available_total_boxes = inventory.available_total_boxes + boxes
            elif int(pallet['boxes']) > pallets.boxes:
              boxes = int(pallet['boxes']) - pallets.boxes
              inventory.available_total_boxes = inventory.available_total_boxes - boxes

            inventory.save()
            if request.session.get('%s-%s'%(inventory.id, request.user)):
              del request.session['%s-%s'%(inventory.id, request.user)]
          else:
            # previous inventory reverted
            invt = pallets.inventory
            invt.available_total_boxes = invt.available_total_boxes + pallets.boxes
            invt.save()

            # update boxes in new inventory
            inventory = WarehouseInventory.objects.get(pk=pallet['inventory'])
            if int(pallet['boxes']) < inventory.available_total_boxes:
              inventory.available_total_boxes = inventory.available_total_boxes - int(pallet['boxes'])
            else:
              inventory.available_total_boxes = 0
            inventory.save()
            if request.session.get('%s-%s'%(inventory.id, request.user)):
              del request.session['%s-%s'%(inventory.id, request.user)]

          
          pallets.palet_lot = pallet['palet_lot']
          pallets.boxes = pallet['boxes']
          pallets.box_kg = pallet['box_kg']
          pallets.warehouse_id = pallet['warehouse']
          pallets.location_id = pallet['warehouse_location'] 
          pallets.rack_number_id = pallet['rack_number']
          pallets.cost_lot = pallet['cost_lot']
          pallets.exp_date = pallet['exp_date']
          pallets.gross_weight = pallet['gross_weight']
          pallets.net_weight = pallet['net_weight']
          pallets.invoice_weight = pallet['invoice_weight']
          pallets.retained_quantity=pallet['retained_quantity']
          pallets.inventory_id = pallet['inventory']
          pallets.retained_reason = pallet['retained_reason']
          try:
            pallets.save()
          except Exception as ex:
            return JsonResponse({'code': 500, 'error': str(ex)})
        else:
          pallet_data.delete()
  else:

    request_data = json.loads(request.POST['pallet_arr'])
    conf_data = json.loads(request.POST['confirmation_data'])
    measurement_data = json.loads(request.POST['measurement_data'])
    if measurement_data.get('measurement_id',False) =="N/A":
      product = Product.objects.filter(pk=int(conf_data['exit_product'])).first()
      WExitProductMeasurement.objects.create(total_kg = measurement_data['total_kg'],price = measurement_data['total_price'],kg_per_price = measurement_data['kg_per_price'],boxes = measurement_data['boxes'],kg_per_boxes = measurement_data['kg_per_boxes'],werehouse_exit_id = int(conf_data['warehouse_exit_id']), product_id =  conf_data['exit_product'], product_description = product.product_description)
    else:
      WExitProductMeasurement.objects.filter(pk=measurement_data['measurement_id']).update(total_kg = measurement_data['total_kg'],price = measurement_data['total_price'],kg_per_price = measurement_data['kg_per_price'],boxes = measurement_data['boxes'],kg_per_boxes = measurement_data['kg_per_boxes'])
    if measurement_data.get('measurement_id',False) !="N/A":
      product_measurement_id = measurement_data['measurement_id']
    else:
      product_measurement_id = ""
    already = WExitConfirmation.objects.filter(exit_product_measurement_id=product_measurement_id)
    if len(already) > 0:
      already.delete()
    w_exit = WExitConfirmation.objects.create(product_id = conf_data['exit_product'], cost_lot = conf_data['warehouse_cost_lot'], exp_date = conf_data['warehouse_exp_date'], gross_weight = conf_data['peso_bruto'], net_weight = conf_data['peso_neto'], invoice_weight = conf_data['warehouse_invoice_weight'], retained_quantity = conf_data['warehouse_retained_quantity'], retained_reason = conf_data['warehouse_retained_reason'], werehouse_exit_id = int(conf_data['warehouse_exit_id']), removed_boxes = [], removed_kgs = [], auto_pick_data = {},exit_product_measurement_id=product_measurement_id )
    for pallet in request_data: 
      if pallet['is_deleted'] == False:
        try:
          WarehouseExitPallet.objects.create(palet_lot=pallet['palet_lot'],boxes=pallet['boxes'],box_kg=pallet['box_kg'],warehouse_id=pallet['warehouse'],rack_number_id=pallet['rack_number'],location_id=pallet['warehouse_location'], cost_lot=pallet['cost_lot'],exp_date=pallet['exp_date'],gross_weight=pallet['gross_weight'],net_weight=pallet['net_weight'],invoice_weight=pallet['invoice_weight'], retained_quantity=pallet['retained_quantity'],retained_reason=pallet['retained_reason'],werehouse_exit_confirmation=w_exit,inventory_id=pallet['inventory'])
        except Exception as ex:
          return JsonResponse({'code': 500, 'error': str(ex)})
        # perform inventory boxes reduction
        inventory = WarehouseInventory.objects.get(pk=pallet['inventory'])
        if int(pallet['boxes']) < inventory.available_total_boxes:
          inventory.available_total_boxes = inventory.available_total_boxes - int(pallet['boxes'])
        else:
          inventory.available_total_boxes = 0
        inventory.save()
        if request.session.get('%s-%s'%(inventory.id, request.user)):
          del request.session['%s-%s'%(inventory.id, request.user)]
          

  return JsonResponse({"message": "success","code": 200}, safe=True)
  

def get_pallet_peso_variable(request,pallet):
  pallet_peso_variable = ExitPalletPesoVariable.objects.filter(werehouse_exit_pallet=pallet)
  exit_palet = WarehouseExitPallet.objects.filter(id=pallet).first().palet_lot
  entrance_palet = WarehouseEntrancePallet.objects.filter(palet_lot=exit_palet)

  
  if len(pallet_peso_variable)>0:
    peso_variable = PalletPesoVariableSerializer(pallet_peso_variable,many=True)  
    locations_data = {'peso_variable': peso_variable.data, 'data-matched': "true"}
    return JsonResponse(locations_data, safe=True)
  elif len(entrance_palet) >0:
    entrance_pallet_peso_variable = entrance_palet.first().entrancepalletpesovariable_set.all()
    if len(entrance_pallet_peso_variable)>0:
      entrance_pallet_variable = EntrancePalletPesoVariableSerializer(entrance_pallet_peso_variable,many=True)  
      locations_data = {'peso_variable': entrance_pallet_variable.data, 'data-matched': "yes"}
      return JsonResponse(locations_data, safe=True)
    else:
      locations_data = {'peso_variable': [], 'data-matched': "false"}
      return JsonResponse(locations_data, safe=False)
  else:
    locations_data = {'peso_variable': [], 'data-matched': "false"}
    return JsonResponse(locations_data, safe=False)

@csrf_exempt
def save_pallet_peso_variable(request):
  total_array = request.POST['arr_counter']
  pallet_id = request.POST.get('pallet_id', '')
  

  create_enteries=[]
  from django.db import connection
  cursor = connection.cursor()
  with transaction.atomic():
    for x in range(int(total_array)):
      palet_value = request.POST.get('palet_values[%s][palet_value]'%x)
      palet_id = request.POST.get('palet_values[%s][palet_id]'%x)
      peso_id = request.POST.get('palet_values[%s][id]'%x,'')  
      deleted_pallet = request.POST.get('palet_values[%s][delete]'%x,'False')
      if peso_id == '':
        create_enteries.append(ExitPalletPesoVariable(peso_variable_quantity=float(palet_value),werehouse_exit_pallet_id=int(palet_id)))
        ExitPalletPesoVariable.objects.create(peso_variable_quantity=palet_value,werehouse_exit_pallet_id=int(palet_id))
      else:

        exit_variable = ExitPalletPesoVariable.objects.filter(id=int(peso_id))
        if 'True' in str(deleted_pallet):
          # exit_variable.delete()
          cursor.execute("DELETE FROM warehouse_exit_exitpalletpesovariable WHERE warehouse_exit_exitpalletpesovariable.id = %s"%(int(peso_id)))          
        else:
          # exit_variable.update(peso_variable_quantity=palet_value, werehouse_exit_pallet_id=int(palet_id))
          cursor.execute("UPDATE warehouse_exit_exitpalletpesovariable SET peso_variable_quantity=%s, werehouse_exit_pallet_id=%s WHERE warehouse_exit_exitpalletpesovariable.id = %s"%(palet_value, int(palet_id), int(peso_id)))
    # if create_enteries:
    #   ExitPalletPesoVariable.objects.bulk_create(create_enteries)
    total_weight = 0
    measurement_gross_weight = 0

    if pallet_id != "":
      pallet = WarehouseExitPallet.objects.get(id=pallet_id)
      total_peso_weight = ExitPalletPesoVariable.objects.filter(werehouse_exit_pallet_id=pallet_id).aggregate(peso_variable_quantity=Coalesce(Sum('peso_variable_quantity'),0))
      total_weight = total_peso_weight['peso_variable_quantity']
      total_palets = pallet.werehouse_exit_confirmation.warehouseexitpallet_set.all()
      prev_gross_weight = 0
      prev_net_weight = 0
      for before_pallet in total_palets:
        prev_gross_weight += float("%s" % before_pallet.gross_weight)
        prev_net_weight += float("%s" % before_pallet.net_weight)
  
      pallet.gross_weight =total_weight
      pallet.net_weight = total_weight
      pallet.save()

      after_gross_weight = 0
      after_net_weight = 0

      after_save_palets = pallet.werehouse_exit_confirmation.warehouseexitpallet_set.all()
      inv = pallet.inventory
      for after_pallet in after_save_palets:
        after_gross_weight += float("%s" % after_pallet.gross_weight)
        after_net_weight += float("%s" % after_pallet.net_weight) 
      if prev_gross_weight < after_gross_weight:
        new_gross_weight = after_gross_weight - prev_gross_weight        
        inv.total_kg -= new_gross_weight
        inv.available_gross_weight -= new_gross_weight
        inv.available_net_weight -= new_gross_weight
        inv.save()
      elif prev_gross_weight > after_gross_weight:
        new_gross_weight = prev_gross_weight - after_gross_weight 
        inv.total_kg += new_gross_weight
        inv.available_gross_weight +=new_gross_weight
        inv.available_net_weight +=new_gross_weight
        inv.save()
      elif prev_gross_weight == after_gross_weight:
        new_gross_weight = prev_gross_weight

      measurement_gross_weight = pallet.werehouse_exit_confirmation.exit_product_measurement.get_total_palet_gross_weight()

  return JsonResponse({"message": "Pallet peso variable details updated","code": 200, "total_weight": total_weight, "measurement_gross_weight": measurement_gross_weight}, safe=True)
  
@csrf_exempt
def save_romaneo_product_weight(request):
  if len(json.loads(request.POST['weight_array'])) > 0:
    weight_data = json.loads(request.POST['weight_array'])
    pallet_data = json.loads(request.POST['pallet_array'])
    kg_per_boxes=round((weight_data[0].get('romaneo_total_weight')/float(weight_data[0].get('boxes'))), 2)
    w_products = WExitProductMeasurement.objects.filter(pk=weight_data[0].get('product_measurement_id'))
    if w_products.exists():
      w_product = w_products.first()
      w_product.total_kg=weight_data[0].get('romaneo_total_weight')
      w_product.kg_per_boxes=kg_per_boxes
      w_product.save()

    # box_kg = round(kg_per_boxes*weight_data[0].get('pallet_boxes'),2)
    # WarehouseExitPallet.objects.filter(pk=weight_data[0].get('pallet_id')).update(box_kg=box_kg)
    pallet_ids = [ WarehouseExitPallet.objects.filter(pk=item.get('pallet_id')).update(box_kg=round(kg_per_boxes*float(item.get('pallet_boxes')),2)) for item in pallet_data if not str(item.get('pallet_id')) in ['','None']]

    if w_product:
      return JsonResponse({"message": "success","code": 200}, safe=True)
    else:
      return JsonResponse({"message": "fail","code": 500}, safe=True)
  return JsonResponse({"message": "fail","code": 500}, safe=True)
  

@csrf_exempt
def update_exit_romaneo_product_kg(request):
  w_products = WExitProductMeasurement.objects.filter(pk=request.POST.get('product_measurement_id'))
  if w_products.exists():
    w_product = w_products.first()
    w_product.total_kg=request.POST.get('total_kg')
    w_product.kg_per_boxes=request.POST.get('kg_per_boxes')
    w_product.save()
  return JsonResponse({"message": "success","code": 200}, safe=True)
  

def check_print_picking(request, pk):
  try:
    warehouses_exit = WarehouseExit.objects.get(pk=pk)
    print_picking = warehouses_exit.print_picking
    if warehouses_exit.status == 'InManeuvers':
      print_picking = False
    return JsonResponse({"message": "success","code": 200, "data": {"print_picking": print_picking }}, safe=True)
  except:
    return JsonResponse({"message": "Error","code": 500, "data": {"print_picking": False }}, safe=True)

@csrf_exempt
def get_prev_next_pallet(request, pk):
  measurement_id = request.GET.get('measurement_id')
  pallet_id = request.GET.get('pallet_id', 0)
  request_type = request.GET.get('filter_type', "")
  product_id = request.GET.get('product_id', "")
  warehouse_exit = WarehouseExit.objects.get(id= pk)
  measurement = WExitProductMeasurement.objects.get(id=measurement_id)
  total_boxes = measurement.get_total_palet_boxes()
  total_gross_weight = measurement.get_total_palet_gross_weight()
  total_pallet = len(measurement.wexitconfirmation.warehouseexitpallet_set.all())
  pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation__exit_product_measurement_id= measurement_id).order_by('id')
  product = Product.objects.get(id=product_id)
  if request_type == "prev":
    pallet = pallets.filter(id__lt=pallet_id).order_by('id').last()
  elif request_type == "next":
    pallet = pallets.filter(id__gt=pallet_id).order_by('id').first()
  elif int(pallet_id) == 0:
    pallet = pallets.first()
  else:
    pallet = []
  if pallet != None:
    pallet_data = WarehousePalletConfSerializer(pallet,many=False)
    measurement_detail = {'total_boxes': total_boxes, 'total_gross_weight': total_gross_weight, 'total_pallet': total_pallet}
    return JsonResponse({"data": pallet_data.data, 'pallet_found': True, 'measurement_detail': measurement_detail }, safe=True)
  else:
    return JsonResponse({"data": [], 'pallet_found': False }, safe=True)

@csrf_exempt
def confirm_exit_pallet(request, pk):
  pallet_id = request.GET.get('pallet_id', 0)
  warehouse_exit = WarehouseExit.objects.get(id= pk)
  pallet = WarehouseExitPallet.objects.get(id= pallet_id)
  romaneo_zero_exists = pallet.exitpalletpesovariable_set.all().filter(peso_variable_quantity=0).exists()
  not_confirmed = False
  if romaneo_zero_exists:
    pallet.confirmed = False
  else:
    pallet.confirmed = True
    from datetime import datetime
    pallet.maniobras_completed_at = datetime.now()
    pallet.maniobras_completed_by = request.user
  pallet.save()
  confirmed_pallets = WarehouseExitPallet.objects.filter(werehouse_exit_confirmation__exit_product_measurement__werehouse_exit_id=pk, confirmed= False )
  if romaneo_zero_exists:
    not_confirmed = True
    message = "The romaneo is incomplete, please check"
    pass
  elif confirmed_pallets.exists():
    message = "Palet confirmado"
    pass
  else:
    warehouse_exit.status = "ManeuverComplete"
    warehouse_exit.save()
    message = "Todo el palet esta confirmado ahora"

  return JsonResponse({'message': message, 'not_confirmed': not_confirmed}, safe=True)
