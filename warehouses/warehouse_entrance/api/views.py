from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import WarehouseEntrancePalletSerializer,ProductSerializer,WarehouseLocationSerializer, WarehouseEntranceConfirmationSerializer,SectionSerializer,PalletPesoVariableSerializer
from rest_framework.decorators import detail_route
from catalogs.clients.models import Client
from catalogs.product.models import Product
from catalogs.warehouse.models import WarehouseLocation,WarehouseDepthLevel,WarehouseHeightLevel,Warehouse,WarehouseSection
from rest_framework.generics import ListCreateAPIView,CreateAPIView
from ..models import WarehouseEntranceConfirmation,WarehouseEntrancePallet, WarehouseEntrance,EntrancePalletPesoVariable,WProductMeasurement
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
import json, pdb
import datetime
from catalogs.general_params.models import GeneralParams
from ast import literal_eval
from django.db import transaction
from django.db.models import Sum, Q
from django.db.models.functions import Cast, Coalesce

class CustomerProductsAPIView(viewsets.ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	def get_queryset(self):
		if self.kwargs['pk'] == "ALL":
			queryset = Product.objects.all().order_by("product_code")
		else:
			queryset = Product.objects.filter(customer_id__in=[int(self.kwargs['pk'])]).order_by("product_code")
		return queryset

def get_pallet_detail(request,pallet):
  pallets = WarehouseEntrancePallet.objects.filter(id=pallet)
  if pallets.exists():
    pallet_data = WarehouseEntrancePalletSerializer(pallets.first(),many=False)  
    pallet_data = {'pallet_info': pallet_data.data, 'code': 200}
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'pallet_info': [], 'code': 500}
    return JsonResponse(pallet_data, safe=False)

#Add inventory taking preload pallet
def get_pallets_list(request,customer, product):
  if product != "ALL":
    products = Product.objects.filter(id=product)
  else:
    products = Product.objects.all()

  pallets = WarehouseEntrancePallet.objects.filter(Q(warehouseinventory__product__in=products)& Q(warehouseinventory__client=customer)&  Q(warehouseinventory__total_boxes__gt=0) & Q(warehouseinventory__total_kg__gt=0))
  if pallets.exists():
    pallet_data = WarehouseEntrancePalletSerializer(pallets,many=True)  
    pallet_data = {'data': pallet_data.data, 'code': 200}
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'data': [], 'code': 500}
    return JsonResponse(pallet_data, safe=False)


def get_pallet_peso_variable(request,pallet):
  pallet_peso_variable = EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet_id=pallet).order_by('-id')
  if pallet_peso_variable.exists():
    peso_variable = PalletPesoVariableSerializer(pallet_peso_variable,many=True)  
    return JsonResponse({'data': peso_variable.data, 'code': 200}, safe=True)
  else:
    return JsonResponse({'data': [], 'code':500}, safe=True)


@csrf_exempt
def save_romaneo_peso_variables(request, pk):
  try:
    request_data = literal_eval(request.POST.get('data'))
    pallet_peso_variable = WarehouseEntrancePallet.objects.get(id=pk).entrancepalletpesovariable_set.values_list('id', flat=True)
    new_peso_variable = [{"werehouse_entrance_pallet":item.get('werehouse_entrance_pallet'), "peso_variable_quantity": item.get('peso_variable_quantity')} for item in request_data if item.get('id') == '']
    request_ids = [int(item.get('id')) for item in request_data if item.get('id') != '']
    if len(request_ids) > 0:
      deletable_ids = list(set(pallet_peso_variable)-set(request_ids))
      EntrancePalletPesoVariable.objects.filter(id__in=deletable_ids).delete()

    queryset = EntrancePalletPesoVariable.objects.filter(id__in=request_ids)
    # Update existing peso variable
    for obj in queryset:
      obj.peso_variable_quantity = [item.get('peso_variable_quantity') for item in request_data if str(obj.id) == item.get('id')][0]
      obj.save()

    # Create new peso variable
    serializer = PalletPesoVariableSerializer(data=new_peso_variable, many=True)
    serializer.is_valid()
    serializer.save()
    pallet_peso_variable = WarehouseEntrancePallet.objects.get(id=pk)
    result = sum([float(confirm.peso_variable_quantity) for confirm in pallet_peso_variable.entrancepalletpesovariable_set.all()])

    pallet_peso_variable.gross_weight = result
    pallet_peso_variable.net_weight = result
    pallet_peso_variable.save()
    return JsonResponse({'code': 200, 'message': 'Detalles variables de peso de pallet actualizados.'}, safe=True)
  except:
    return JsonResponse({'code': 500, 'message': 'Error al actualizar los detalles de la variable de peso de paleta.'}, safe=True)



@csrf_exempt
def save_entrance_pallet(request):
  request_data = json.loads(request.POST['pallet_arr'])
  pallet_id = ""
  try:
    import math
    confirm_data = json.loads(request.POST.get('confirmation_array'))
    if confirm_data:
      w_confirmation_id = confirm_data[0]['w_confirmation_id']
      w_confirmations = WarehouseEntranceConfirmation.objects.filter(pk=w_confirmation_id)
      if w_confirmations.exists():
        w_confirmation = w_confirmations.first()
        w_confirmation.cost_lot = confirm_data[0]['cost_lot']
        w_confirmation.exp_date = confirm_data[0]['exp_date']
        w_confirmation.gross_weight = confirm_data[0]['gross_weight']
        w_confirmation.net_weight = confirm_data[0]['net_weight']
        w_confirmation.invoice_weight = confirm_data[0]['invoice_weight']
        w_confirmation.retained_quantity = confirm_data[0]['retained_quantity']
        w_confirmation.retained_reason = confirm_data[0]['retained_reason']
        w_confirmation.save()

    for pallet in request_data:
      
       
      exp_date = pallet['exp_date']
      if pallet['exp_date'] == "":
        exp_date = datetime.datetime.today().strftime('%Y-%m-%d')
      
      pallet_box_kg = float(pallet['box_kg'])
      if math.isnan(pallet_box_kg):
        pallet['box_kg']=0.0
      is_last_pallet = pallet['is_last_pallet']
      if pallet['palet_id'] =="":
        if pallet["deleteconfirmation_hashd"] == "true":
          confirmation = WarehouseEntranceConfirmation.objects.get(pk=pallet["confirmation_id"])
          measurement = confirmation.w_product_measurement
          product = measurement.product
          packages_per_pallet = product.packages_per_pallet
          if pallet['box_kg'] == 0:
            if is_last_pallet:
              total_pallet_boxes = measurement.get_total_palet_boxes()
              available_boxes = measurement.control_total_boxes - total_pallet_boxes
              last_pallet_value = available_boxes % packages_per_pallet
              measurement.control_total_boxes -= float(last_pallet_value)
              measurement.control_total_kg -= float(pallet['gross_weight'])
            else:
              measurement.control_total_boxes -= float(packages_per_pallet)
              measurement.control_total_kg -= float(pallet['gross_weight'])
          else:
            measurement.control_total_boxes -= float(pallet['box_kg'])
            measurement.control_total_kg -= float(pallet['gross_weight'])
          measurement.save()
        else:
          pallet_data = WarehouseEntrancePallet.objects.create(palet_lot=pallet['palet_lot'],
                                          boxes=pallet['boxes'],box_kg=pallet['box_kg'],
                                          cost_lot=pallet['cost_lot'],exp_date=exp_date,gross_weight=pallet['gross_weight'],
                                          net_weight=pallet['net_weight'],
                                          retained_quantity=pallet['retained_quantity'],retained_reason=pallet['retained_reason'],
                                          werehouse_entrance_confirmation_id=pallet['confirmation_id'])
          pallet_id = pallet_data.id
          if pallet['maniobras'] =="true":
            pallet_data.maniobras = True
            pallet_data.sent_to_maniobras_at = datetime.datetime.today()
            pallet_data.save()
          if pallet['added_new_pallet'] =="true":
            w_product_measurement = pallet_data.werehouse_entrance_confirmation.w_product_measurement
            w_product_measurement.control_total_boxes += float(pallet_data.boxes)
            w_product_measurement.control_total_kg += float(pallet_data.gross_weight)
            w_product_measurement.save()
          w_product_measurement = pallet_data.werehouse_entrance_confirmation.w_product_measurement
          save_entrance_pallet_romaneo(pallet_data, w_product_measurement)
      else:

        pallet_data = WarehouseEntrancePallet.objects.filter(pk=pallet['palet_id'])
        if pallet['deleteconfirmation_hashd'] =="true":
          pallet = pallet_data.first()
          w_product_measurement = pallet.werehouse_entrance_confirmation.w_product_measurement
          product = w_product_measurement.product
          packages_per_pallet = product.packages_per_pallet
          if pallet.boxes == 0: 
            if is_last_pallet:
              total_pallet_boxes = measurement.get_total_palet_boxes()
              available_boxes = measurement.control_total_boxes - total_pallet_boxes
              last_pallet_value = available_boxes % packages_per_pallet
              measurement.control_total_boxes -= float(last_pallet_value)
              measurement.control_total_kg -= float(pallet.gross_weight)
            else:
              measurement.control_total_boxes -= float(packages_per_pallet)
              measurement.control_total_kg -= float(pallet.gross_weight)
          else:
            w_product_measurement.control_total_boxes / packages_per_pallet
            w_product_measurement.control_total_boxes -= float(pallet.boxes)
            w_product_measurement.control_total_kg -= float(pallet.gross_weight)

          w_product_measurement.save()
          pallet_data.delete()
        else:

          pallets = pallet_data.first()
          w_product_measurement = pallets.werehouse_entrance_confirmation.w_product_measurement
          new_boxes = float(pallet['boxes'])
          pallet_boxes = float(pallets.boxes)
          new_gross_weight = float(pallet['gross_weight'])
          pallet_gross_weight = float(pallets.gross_weight)        
          pallets.palet_lot = pallet['palet_lot']
          pallets.boxes = pallet['boxes']
          pallets.box_kg = pallet['box_kg']        
          pallets.cost_lot = pallet['cost_lot']
          pallets.exp_date = pallet['exp_date']
          pallets.gross_weight = pallet['gross_weight']
          pallets.net_weight = pallet['net_weight']
          pallets.retained_quantity=pallet['retained_quantity']
          # pallets.inventory_id = pallet['inventory']
          pallets.retained_reason = pallet['retained_reason']
          pallets.werehouse_entrance_confirmation_id=pallet['confirmation_id']
          if pallet['maniobras'] =="true":
            pallets.maniobras = True
            pallets.sent_to_maniobras_at = datetime.datetime.today()
          # if(pallet_boxes > new_boxes):
          #   box_data = pallet_boxes - new_boxes 
          #   w_product_measurement.boxes -= int(box_data)
          # elif(pallet_boxes < new_boxes):
          #   box_data = new_boxes - pallet_boxes
          #   w_product_measurement.boxes += float(box_data)
          
          # w_product_measurement.save()
          pallets.save()
          save_entrance_pallet_romaneo(pallets, w_product_measurement)
          pallet_id = pallets.id
          
    return JsonResponse({"message": "success","code": 200, "pallet_id": pallet_id}, safe=True)
  except:
    return JsonResponse({"message": "success","code": 200, "pallet_id": ""}, safe=True)
  
def get_rack_location(request,warehouse):
  warehouse = Warehouse.objects.get(id=warehouse)
  racks = WarehouseSection.objects.filter(row__warehouse= warehouse).order_by('index')
  rack_data = SectionSerializer(racks,many=True)  
  locations_data = {'racks': rack_data.data}
  return JsonResponse(locations_data, safe=False)

def get_location(request,*args,**kwargs):
  
  rack = request.POST['rack']
  warehouse = request.POST['warehouse']
  boxes = request.POST['total_boxes']
  product_net_weight = request.POST['product_net_weight']
  current_weight = float(product_net_weight) * int(boxes)
  locations = WarehouseLocation.objects.prefetch_related('warehousedepthlevel_set').filter(warehousedepthlevel__height__section_id= rack, is_locked=False, available_weight__gte=current_weight).order_by('id')
  
  location_data = WarehouseLocationSerializer(locations, many=True)
  locations_data = {'locations': location_data.data}
  return JsonResponse(locations_data, safe=False)

class WarehouseLocationsConfirmationAPIView(viewsets.ModelViewSet):
	queryset = WarehouseEntranceConfirmation.objects.all()
	serializer_class = WarehouseEntranceConfirmationSerializer
	def get_queryset(self):
		warehouse = WarehouseEntrance.objects.get(id=self.kwargs['pk'])
		queryset = warehouse.warehouseentranceconfirmation_set.order_by('id')
		return queryset

class WarehouseAvailabilityApiView(ListCreateAPIView):
  queryset = WarehouseEntrance.objects.all()
  def create(self,request,*args, **kwargs):
    warehouse = request.data['warehouse']
    location = request.data['location']
    product = request.data['product']
    boxes = request.data['boxes']
    product_data = Product.objects.get(id=product)
    net_weight = product_data.net_weight
    current_weight = net_weight * int(boxes)
    warehouse_location = WarehouseLocation.objects.filter(warehouse_id= warehouse, id=location)
    if warehouse_location.exists():
      warehouse_location = warehouse_location.first()
      if(warehouse_location.available_weight >= current_weight):
        return Response({"message":"Valid boxes" , "code": 200})
      else:
        return Response({"message":"Invalid boxes" , "code": 500})
    else:
      return Response({"message":"Invalid boxes" , "code": 500})

class BoxesAvailabilityApiView(APIView):
    queryset = WarehouseEntrance.objects.all()
    def post(self,request,*args, **kwargs):
      import json
      request_data = json.loads(request.data['data'])
      warehouse = request_data['warehouse']
      location = request_data['location']
      current_weight = float(request_data.get('product_net_weight')) * int(request_data.get('total_boxes'))
      warehouse_location = WarehouseLocation.objects.filter(warehouse_id= warehouse, id=location)
      if warehouse_location.exists():
        warehouse_location = warehouse_location.first()
        if(warehouse_location.available_weight >= current_weight):
          return Response({"message":"Valid boxes" , "code": 200})
        else:
          return Response({"message":"Invalid boxes" , "code": 500})
      else:
        return Response({"message":"Invalid boxes" , "code": 500})

# update total kg and kg per boxes on confirm romaneos
@csrf_exempt
def update_romaneo_product_total_kg(request):
  w_products = WProductMeasurement.objects.filter(pk=request.POST.get('product_measurement_id'))
  if w_products.exists():
    w_product = w_products.first()
    w_product.total_kg=request.POST.get('total_kg')
    w_product.kg_per_boxes=request.POST.get('kg_per_boxes')
    w_product.save()
  return JsonResponse({"message": "success","code": 200}, safe=True)

# Check Peso variable quantity against the actually quantity
@csrf_exempt
def check_peso_variable_quantity(request):
  request_data = literal_eval(request.POST.get('data'))
  pallet_peso_variable = WarehouseEntrancePallet.objects.filter(id__in=request_data).values('entrancepalletpesovariable__peso_variable_quantity').aggregate(total_quantity=Coalesce(Sum('entrancepalletpesovariable__peso_variable_quantity'), 0))
  return JsonResponse({"message": "success","code": 200, "data":{"total_quantity": pallet_peso_variable.get('total_quantity', 0) }}, safe=True)


# Update pallet and measurement weight when user confirm send to maneuvar yes.
@csrf_exempt
def save_romaneo_weights(request):
  request_data = literal_eval(request.POST.get('pallet_ids'))
  pallets = WarehouseEntrancePallet.objects.filter(id__in=request_data)
  for ent_pallet in pallets:
    quantity = ent_pallet.entrancepalletpesovariable_set.values('peso_variable_quantity').aggregate(total_quantity=Coalesce(Sum('peso_variable_quantity'), 0)).get('total_quantity', 0)
    ent_pallet.gross_weight = quantity
    ent_pallet.net_weight = quantity
    ent_pallet.save()
    gross_weight_data = ent_pallet.werehouse_entrance_confirmation.warehouseentrancepallet_set.values('gross_weight').aggregate(romaneo_total_weight=Coalesce(Sum('gross_weight'), 0))
    total_boxes = ent_pallet.werehouse_entrance_confirmation.warehouseentrancepallet_set.values('boxes').aggregate(total_boxes=Coalesce(Sum('boxes'), 0)).get('total_boxes', 0)
    kg_per_boxes = float(gross_weight_data.get('romaneo_total_weight'))/total_boxes

    w_product_measurement = ent_pallet.werehouse_entrance_confirmation.w_product_measurement
    w_product_measurement.total_kg=float(gross_weight_data.get('romaneo_total_weight'))
    w_product_measurement.kg_per_boxes= kg_per_boxes
    w_product_measurement.save()

    ent_pallet.box_kg=round(kg_per_boxes*ent_pallet.boxes,2)
    ent_pallet.save()
  return JsonResponse({"message": "success","code": 200}, safe=True)

@csrf_exempt
def entrance_pallet_details(request, pk):
  measurment_id = literal_eval(request.POST.get('pk'))
  return JsonResponse({"message": "success","code": 200, "data":{"total_quantity": [measurment_id] }}, safe=True)

@csrf_exempt
def save_pallet_measurement(request):
  product_id = request.POST.get('product_id')
  total_kg = request.POST.get('total_kg')
  total_boxes = request.POST.get('total_boxes')
  entrance_id = request.POST.get('entrance_id')
  product = Product.objects.get(pk=product_id)
  measurement = WProductMeasurement.objects.create(
    control_total_kg = total_kg,
    control_total_boxes = total_boxes,
    product_id = product_id,
    werehouse_entrance_id = entrance_id,
    product_description = product.product_description,
    total_kg = 0,
    boxes = 0
    )
  return JsonResponse({"message": "success","code": 200}, safe=True)

def get_single_pallet_detail(request):
  
  entrance_id = request.GET["entrance_id"]
  pallet_code = request.GET["pallet_code"]
  pallets = WarehouseEntrancePallet.objects.filter(maniobras= True, palet_lot= pallet_code, werehouse_entrance_confirmation__werehouse_entrance_id=entrance_id )
  
  if pallets.exists():
    pallet = pallets.first()
    pallet_data = WarehouseEntrancePalletSerializer(pallet,many=False)
    pallet_url = json.dumps(pallet.get_pallet_information)
    pallet_location_url = json.dumps(pallet.get_warehouse_information)
    pallet_data = {'pallet_info': pallet_data.data, 'code': 200, "pallet_url": pallet_url, 'pallet_location_url': pallet_location_url }
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'pallet_info': [], 'code': 500, "pallet_url": "", 'pallet_location_url': ""}
    return JsonResponse(pallet_data, safe=False)

def get_pallet_detail_for_relocation(request):
  
  pallet_code = request.GET["pallet_code"]
  pallets = WarehouseEntrancePallet.objects.filter(palet_lot= pallet_code )
  
  if pallets.exists():
    pallet = pallets.first()
    pallet_data = WarehouseEntrancePalletSerializer(pallet,many=False)
    pallet_url = json.dumps(pallet.get_pallet_information)
    pallet_location_url = json.dumps(pallet.get_warehouse_information)
    pallet_data = {'pallet_info': pallet_data.data, 'code': 200, "pallet_url": pallet_url, 'pallet_location_url': pallet_location_url }
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'pallet_info': [], 'code': 500, "pallet_url": "", 'pallet_location_url': ""}
    return JsonResponse(pallet_data, safe=False)


def save_pallet_location(request):
  warehouse_id = request.POST["warehouse_id"]
  rack_id = request.POST["rack_id"]
  location_id = request.POST["location_id"]
  pallet_id = request.POST["pallet_id"]
  pallets = WarehouseEntrancePallet.objects.filter(id= int(pallet_id))  
  if pallets.exists():
    pallet = pallets.first()
    pallet.warehouse_id = warehouse_id
    pallet.location_id = location_id
    pallet.rack_number_id = rack_id    
    qr_enables = GeneralParams.objects.filter(key="QR_Read", value=0).exists()
    if qr_enables:
      pallet.confirmed = True
      pallet.maniobras_completed_at = datetime.datetime.today()
      pallet.maniobras_completed_by = request.user
    pallet.save()
    werehouse_entrance = pallet.werehouse_entrance_confirmation.werehouse_entrance
    if werehouse_entrance.status == "InManeuvers":
      previous_pallets = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance_id= werehouse_entrance.id)
      confirmed_pallet = previous_pallets.filter(confirmed=True)
      if len(previous_pallets) == len(confirmed_pallet):
        werehouse_entrance.status = "ManeuverComplete"
        werehouse_entrance.save()
    return JsonResponse({"message": "success","code": 200}, safe=True)
  else:
    return JsonResponse({"message": "failled","code": 500}, safe=True)

def get_pallet_from_entrance(request):
  
  entrance_id = request.GET["entrance_id"]
  pallets = WarehouseEntrancePallet.objects.filter(confirmed=False,maniobras= True, werehouse_entrance_confirmation__werehouse_entrance_id=entrance_id )
  
  if pallets.exists():
    pallet_data = WarehouseEntrancePalletSerializer(pallets,many=True)  
    pallet_data = {'pallet_info': pallet_data.data, 'code': 200}
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'pallet_info': [], 'code': 500}
    return JsonResponse(pallet_data, safe=False)

def get_prev_next_pallet(request):
  
  entrance_id = request.POST["entrance_id"]
  pallet_id = request.POST["pallet_id"]
  request_type = request.POST["type"]
  pallets = WarehouseEntrancePallet.objects.filter(maniobras= True,werehouse_entrance_confirmation__werehouse_entrance_id=entrance_id )
  
  if pallets.exists():
    pallet_found = True
    if int(pallet_id) ==0:
      pallet = pallets.first()
    elif request_type == "previous":
      pallet = pallets.filter(id__lt=pallet_id).order_by('id').first()
    elif request_type == "next":
      pallet = pallets.filter(id__gt=pallet_id).order_by('id').first()
    else:
      pallet = []
      pallet_found = False
    if pallet != None:
      pallet_data = WarehouseEntrancePalletSerializer(pallet,many=False)
      pallet_url = json.dumps(pallet.get_pallet_information)
      pallet_location_url = json.dumps(pallet.get_warehouse_information)
      pallet_data = {'pallet_info': pallet_data.data, 'code': 200, "pallet_url": pallet_url, 'pallet_location_url': pallet_location_url, "pallet_found": pallet_found }
    else: 
      pallet_data = {'pallet_info': [], 'code': 500, "pallet_found": False}
    return JsonResponse(pallet_data, safe=True)
  else:
    pallet_data = {'pallet_info': [], 'code': 500, "pallet_found": False}
    return JsonResponse(pallet_data, safe=False)

def compare_measurement_pallet(request, pk):
  entrance = WarehouseEntrance.objects.get(pk=pk)
  measurements = entrance.wproductmeasurement_set.all()
  authorizable = False
  product_code = []
  for measurement in measurements:
    measurement_boxes = measurement.control_total_boxes
    pallet_boxes = measurement.get_total_palet_boxes()
    if pallet_boxes < measurement_boxes:
      authorizable = True
      product_code.append(measurement.product.product_code)
  return JsonResponse({'authorizable': authorizable, 'product_code': ", ".join( product_code ) }, safe=False)

def save_entrance_pallet_romaneo(entrance_pallet, product_measurement):
  
  product = product_measurement.product
  if product.average_weight and product.variable_weight:
    existing_peso_variables = EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet_id=entrance_pallet.id)
    per_kg = 0
    if(product_measurement.total_kg >0 and product_measurement.boxes>0):
      per_kg = round(product_measurement.total_kg/product_measurement.boxes, 3)
    elif (product_measurement.control_total_boxes >0 and product_measurement.control_total_kg >0):
      per_kg = round(product_measurement.control_total_kg/product_measurement.control_total_boxes, 3)
    else:
      per_kg = 0
    if existing_peso_variables.exists():
      existing_count = len(existing_peso_variables)
      difference = int(entrance_pallet.boxes) - existing_count
      if difference <0:
        to_be_removed = existing_count - int(entrance_pallet.boxes)
        EntrancePalletPesoVariable.objects.filter(pk__in=EntrancePalletPesoVariable.objects.filter(werehouse_entrance_pallet=entrance_pallet).order_by('-id').values('pk')[:to_be_removed]).delete()
      elif difference >0:
        if per_kg >0:
          for box in range(difference):
            EntrancePalletPesoVariable.objects.create(werehouse_entrance_pallet=entrance_pallet, peso_variable_quantity=per_kg)
      else:
        pass
    else:
      if per_kg >0:
        for box in range(int(entrance_pallet.boxes)):
          EntrancePalletPesoVariable.objects.create(werehouse_entrance_pallet=entrance_pallet, peso_variable_quantity=per_kg)
    if per_kg >0:
      pallet_weight = int(entrance_pallet.boxes) * per_kg
      entrance_pallet.gross_weight = pallet_weight
      entrance_pallet.net_weight = pallet_weight
      entrance_pallet.save()