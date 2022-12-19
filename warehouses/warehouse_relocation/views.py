from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import json
from django.http import HttpResponse, HttpResponseRedirect

from warehouses.warehouse_exit.models import WarehouseExitPallet

from warehouses.warehouse_entrance.models import WarehouseEntrancePallet,WarehouseEntrance,WarehouseEntranceConfirmation
from catalogs.clients.models import Client
from catalogs.product.models import Product
from .models import WarehouseRelocation
from .forms import RelocationForm
import pdb
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from catalogs.warehouse.models import Warehouse,WarehouseLocation
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
from django.views.generic import DetailView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import (WarehouseEntranceSerializer,
    WarehouseEntranceConfirmationSerializer,WarehousePalletSerializer,
    WarehouseSerializer,WarehouseEntranceConfirmationProductSerializer)
from catalogs.warehouse.serializers import WarehouseRelocationSerializer
from .filters import WarehouseEntranceFilter, WarehouseRelocationFilterSet
from django.db.models import Q,Sum

class RelocationList(LoginRequiredMixin, CreateView):
   template_name = 'warehouse/warehouse_relocation/list.html'
   model = WarehouseRelocation
   fields = ['description']
   def get_context_data(self, **kwargs):
        context = super(RelocationList, self).get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['customers'] = Client.objects.all()
        context['locations'] = WarehouseLocation.objects.all()
        context['warehouses'] = Warehouse.objects.all()
        return context


class RelocationCreate(LoginRequiredMixin, CreateView):
    template_name = 'warehouse/warehouse_relocation/create.html'
    model = WarehouseRelocation
    form_class = RelocationForm

    def get_context_data(self, **kwargs):
       context = super(RelocationCreate, self).get_context_data(**kwargs)
       context['locations'] = WarehouseLocation.objects.all()
       context['warehouses'] = Warehouse.objects.all()
       context['werehouse_entrance'] = WarehouseEntrance.objects.filter(status='finish')

       if self.request.POST:
            context['warehouse_relocation'] = self.object        
       else:
           context['warehouse_relocation'] = self.object
       return context
      
    def form_valid(self, form):
        self.object = form.save(commit=False)
        context = self.get_context_data()
        if form.is_valid():
           self.object = form.save()          
           return super(RelocationCreate, self).form_valid(form)
        else:
           return self.render_to_response(self.get_context_data(form=form))


class RelocationShowView(LoginRequiredMixin, DetailView):
    template_name = 'warehouse/warehouse_relocation/show.html'
    model = WarehouseRelocation
    form_class = RelocationForm
    def get_context_data(self, **kwargs):
        context = super(RelocationShowView, self).get_context_data(**kwargs)
        context['relocation_serializer']=WarehouseRelocationSerializer(self.object).data
        
        return context

class RelocationWeightVolume(ListCreateAPIView):
    queryset = WarehouseLocation.objects.all()
    def post(self,request,*args,**kwargs):
        try:  
            warehouse = request.POST['warehouse']
            location = request.POST['location']
            s_location = request.POST['s_location']
            s_warehouse = request.POST['s_warehouse']
            product = request.POST['product']
            entrance = request.POST['entrance']
            queryset = WarehouseLocation.objects.filter(location_number= location, warehouse= warehouse ).first()
            if request.POST['palet_lot'] == '':
                pallets = WarehouseEntrancePallet.objects.filter(location__id=s_location,
                        warehouse__id=s_warehouse,
                        werehouse_entrance_confirmation__product=product,
                        werehouse_entrance_confirmation__werehouse_entrance__id=entrance).values('boxes').aggregate(total_boxes=Sum('boxes')).get('total_boxes')
            else:
                pallets = WarehouseEntrancePallet.objects.filter(palet_lot = request.POST['palet_lot'] ,location__id=s_location,
                        warehouse__id=s_warehouse,
                        werehouse_entrance_confirmation__product=product,
                        werehouse_entrance_confirmation__werehouse_entrance__id=entrance).values('boxes').aggregate(total_boxes=Sum('boxes')).get('total_boxes')
            
            data_relocation = { "available_weight":  queryset.available_weight , "available_volume": queryset.available_volume ,"total_boxes":pallets}
            
            return HttpResponse(json.dumps(data_relocation))
                  

        except Exception as ex:
            print(ex)
            data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0}
            return HttpResponse(json.dumps(data_relocation))

        

class WarehouseConfirmationProduct(ListCreateAPIView):
    queryset = WarehouseEntrancePallet.objects.all()
    def get(self,request,*args,**kwargs):
        customer = self.kwargs['customer']
        entrance = self.kwargs['entrance']
        product = self.kwargs['product']

        entrance_queryset = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance__customer_id=customer,werehouse_entrance_confirmation__werehouse_entrance=entrance,werehouse_entrance_confirmation__product=product)
        entrance_serializer = WarehousePalletSerializer(data=entrance_queryset,many=True)
        entrance_serializer.is_valid()
        data_entrance = {"entrance_conf": entrance_serializer.data}
        return HttpResponse(json.dumps(data_entrance))

class WarehouseRelocationAPI(LoginRequiredMixin, CreateAPIView):
    queryset = WarehouseEntrance.objects.all()
    serializer_class = WarehouseEntranceSerializer

    def post(self, request, *args, **kwargs):
        
        queryset_entrance = WarehouseEntranceFilter(data=self.request.POST)
        
        customers = []
        products = []
        product_measurements = []
        warehouses = []
        locations = []
        pallets = []
        entrances = []
        palet_lot_status = False
        palet_lot = self.request.POST['palet_lot']
        if queryset_entrance != None:
            for entrance in queryset_entrance:

                if palet_lot == '':
                    pallet_data = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance_id=entrance.id)
                else:
                    palet_lot_status = True
                    pallet_data = WarehouseEntrancePallet.objects.filter(werehouse_entrance_confirmation__werehouse_entrance_id=entrance.id,palet_lot=palet_lot)

                for pallet in pallet_data:
                    pallets.append({'id': pallet.id , 'warehouse': pallet.warehouse.code,'location': pallet.location.location_number,'palet_lot': pallet.palet_lot,'rack_number': pallet.rack_number.index,'boxes': pallet.boxes,'cost_lot': pallet.cost_lot,'exp_date': pallet.exp_date,'gross_weight': pallet.gross_weight,'net_weight': pallet.net_weight,'invoice_weight': pallet.invoice_weight,'retained_quantity': pallet.retained_quantity,'product': pallet.werehouse_entrance_confirmation.product.product_code})
                customers.append({'id': entrance.customer.id, 'name': entrance.customer.name})
                

                if palet_lot == '':
                    warehouses.append(list(entrance.get_confirm_product_warehous()))
                    locations.append(list(entrance.get_confirm_product_locations()))
                    entrances.append(list(entrance.get_confirm_product_entrance()))
                    products.append(list(entrance.get_confirm_products()))
                    product_measurements.append(list(entrance.get_product_measurementss()))

                else:
                    print("here")
                    warehouses.append(list(entrance.get_confirm_product_warehous(pallet_data.first().id)))
                    locations.append(list(entrance.get_confirm_product_locations(pallet_data.first().id)))
                    entrances.append(list(entrance.get_confirm_product_entrance(pallet_data.first().id)))
                    products.append(list(entrance.get_confirm_products(pallet_data.first().id)))
                    product_measurements.append(list(entrance.get_product_measurementss(pallet_data.first().id)))

            try:
                data = {'palet_lot_status':palet_lot_status,'customers': customers, 'products': products[0],'entrances':entrances[0],
                        'warehouses': warehouses[0], 'locations': locations[0],'product_measurements': product_measurements[0] , 'pallets': pallets , 'code': 200}
            except:
                data = [{'response': 'NoDat', 'code': 404}]
        else:
            data = [{'response': 'NoDat', 'code': 404}]
        return Response(data)

class WarehouseRelocationFilterAPI(LoginRequiredMixin, APIView):
    def post(self, request, *args, **kwargs):
        from datetime import datetime
        
        data = request.data
        filter_data ={k:data[k] for k in data }

        result = WarehouseRelocation.objects.filter(**filter_data).distinct('id')
        if result.exists():
            url = "<a role='button' href='{}/detail' class='btn btn-warning'><i class='fa fa-eye'></i></a>"
            result = [[datetime.strftime(data.created_at, "%Y-%m-%d"), data.customer.name, data.product.product_code , data.werehouse_entrance.total_kg, url.format(data.id)] for data in result.iterator()]
        return Response(tuple(result))


class WarehouseLocationAPI(LoginRequiredMixin, ListCreateAPIView):
    serializer_class = WarehouseSerializer
    def get_queryset(self):
        from catalogs.warehouse.models import WarehouseLocation
        if self.kwargs['pk'] == "ALL":
            queryset = WarehouseLocation.objects.all()
        else:
            queryset = WarehouseLocation.objects.filter(warehouse_id=self.kwargs['pk']).order_by('pk')
        return queryset


class RelocationWeightVolumeShortCode(ListCreateAPIView):
    queryset = WarehouseLocation.objects.all()
    def post(self,request,*args,**kwargs):
        try:
            pallet_code = request.POST["pallet_code"]
            new_location = request.POST["new_location"]
            entrance = request.POST["entrance_id"]
            locations = WarehouseLocation.objects.filter(shortcode= new_location)
            if locations.exists():
                warehouse_location = locations.first()
                location = warehouse_location.id
                warehouse = warehouse_location.warehouse.id            
                existing_pallets = WarehouseEntrancePallet.objects.filter(palet_lot = pallet_code)
                if existing_pallets.exists():
                    pallet = existing_pallets.first()
                    product = pallet.werehouse_entrance_confirmation.w_product_measurement.product
                    if pallet.warehouse != None:
                        s_warehouse = pallet.warehouse.id
                    else:
                        s_warehouse = 0
                    if pallet.location != None:
                        s_location = pallet.location.id
                    else:
                        s_location = 0
                    product_volume = (product.length / 100) * (product.width / 100) * (product.height / 100)
                    product_net_weight = product.net_weight
                    product = product.id
                    queryset = WarehouseLocation.objects.filter(id= location, warehouse= warehouse ).first()
                    if request.POST['pallet_code'] == '':
                        pallets = WarehouseEntrancePallet.objects.filter(location__id=s_location,
                                warehouse__id=s_warehouse,
                                werehouse_entrance_confirmation__product=product).values('boxes').aggregate(total_boxes=Sum('boxes')).get('total_boxes')
                    else:
                        pallets = WarehouseEntrancePallet.objects.filter(palet_lot = pallet_code,location__id=s_location,
                                warehouse__id=s_warehouse,
                                werehouse_entrance_confirmation__product=product).values('boxes').aggregate(total_boxes=Sum('boxes')).get('total_boxes')
                    data_relocation = { "available_weight":  queryset.available_weight , "available_volume": queryset.available_volume ,"total_boxes": pallets, "location_not_found": False,"product_volume": product_volume, "product_net_weight": product_net_weight}
                    
                    return HttpResponse(json.dumps(data_relocation))
                else:
                    data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0, "location_not_found": True, "product_volume": 0, "product_net_weight": 0}
                    return HttpResponse(json.dumps(data_relocation))
            else:
                data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0, "location_not_found": True, "product_volume": 0, "product_net_weight": 0}
                return HttpResponse(json.dumps(data_relocation))   

        except Exception as ex:
            print(ex)
            data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0, "location_not_found": False, "product_volume": 0, "product_net_weight": 0}
            return HttpResponse(json.dumps(data_relocation))


class SaveRelocationFromShortCode(LoginRequiredMixin, CreateAPIView):
    queryset = WarehouseRelocation.objects.all()
    model = WarehouseRelocation
    def post(self, request):
        new_location = request.POST["new_location"]
        palet_lot = request.POST["pallet_code"]
        description = request.POST["description"]
        existing_pallets = WarehouseEntrancePallet.objects.filter(palet_lot = palet_lot)
        if existing_pallets.exists():
            pallet = existing_pallets.first()
            
            product = pallet.werehouse_entrance_confirmation.w_product_measurement.product
            locations = WarehouseLocation.objects.filter(shortcode= new_location)
            warehouse_location = locations.first()
            destination_location = warehouse_location.id
            destination_warehouse = warehouse_location.warehouse.id   
            
            if pallet.warehouse != None:
                source_warehouse = pallet.warehouse.id
            else:
                source_warehouse = ''
            if pallet.location != None:
                source_location = pallet.location.id
            else:
                source_location = ''
            werehouse_entrance = pallet.werehouse_entrance_confirmation.werehouse_entrance.id
            customer = pallet.werehouse_entrance_confirmation.werehouse_entrance.customer.id
            product_id = product.id
            
            WarehouseRelocation.objects.create(
            customer_id = customer, 
            werehouse_entrance_id = werehouse_entrance,
            product_id = product_id,
            description = description,
            source_warehouse = source_warehouse,
            source_location = source_location,
            destination_warehouse_id = destination_warehouse,
            destination_location_id = destination_location,
            palet_lot = palet_lot,
            created_by= self.request.user)
        data_relocation = { "message":  "" }
        return HttpResponse(json.dumps(data_relocation))

class RelocationExitWeightVolumeShortCode(ListCreateAPIView):
    queryset = WarehouseLocation.objects.all()
    def post(self,request,*args,**kwargs):
        try:
            pallet_code = request.POST["pallet_code"]
            new_location = request.POST["new_location"]
            exit = request.POST["exit_id"]
            locations = WarehouseLocation.objects.filter(shortcode= new_location)
            
            if locations.exists():
                warehouse_location = locations.first()
                location = warehouse_location.id
                warehouse = warehouse_location.warehouse.id            
                existing_pallets = WarehouseExitPallet.objects.filter(palet_lot = pallet_code)
                if existing_pallets.exists():
                    pallet = existing_pallets.first()
                    product = pallet.werehouse_exit_confirmation.w_product_measurement.product
                    if pallet.warehouse != None:
                        s_warehouse = pallet.warehouse.id
                    else:
                        s_warehouse = 0
                    if pallet.location != None:
                        s_location = pallet.location.id
                    else:
                        s_location = 0
                    product_volume = (product.length / 100) * (product.width / 100) * (product.height / 100)
                    product_net_weight = product.net_weight
                    product = product.id
                    queryset = WarehouseLocation.objects.filter(id= location, warehouse= warehouse ).first()
                    if request.POST['pallet_code'] == '':
                        pallets = WarehouseExitPallet.objects.filter(location__id=s_location,
                                warehouse__id=s_warehouse,
                                werehouse_exit_confirmation__product=product).values('boxes').aggregate(total_boxes=Sum('boxes')).get('total_boxes')
                    else:
                        pallets = WarehouseExitPallet.objects.filter(palet_lot = pallet_code,location__id=s_location,
                                warehouse__id=s_warehouse,
                                werehouse_exit_confirmation__product=product).values('boxes').aggregate(total_boxes=Sum('boxes')).get('total_boxes')
                    data_relocation = { "available_weight":  queryset.available_weight , "available_volume": queryset.available_volume ,"total_boxes": pallets, "location_not_found": False,"product_volume": product_volume, "product_net_weight": product_net_weight}
                    
                    return HttpResponse(json.dumps(data_relocation))
                else:
                    data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0, "location_not_found": True, "product_volume": 0, "product_net_weight": 0}
                    return HttpResponse(json.dumps(data_relocation))
            else:
                data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0, "location_not_found": True, "product_volume": 0, "product_net_weight": 0}
                return HttpResponse(json.dumps(data_relocation))   

        except Exception as ex:
            print(ex)
            data_relocation = { "available_weight":  0 , "available_volume": 0, "total_boxes":0, "location_not_found": False, "product_volume": 0, "product_net_weight": 0}
            return HttpResponse(json.dumps(data_relocation))

class SaveExitRelocationFromShortCode(LoginRequiredMixin, CreateAPIView):
    queryset = WarehouseRelocation.objects.all()
    model = WarehouseRelocation
    def post(self, request):
        new_location = request.POST["new_location"]
        palet_lot = request.POST["pallet_code"]
        description = request.POST["description"]
        existing_pallets = WarehouseExitPallet.objects.filter(palet_lot = palet_lot)
        if existing_pallets.exists():
            pallet = existing_pallets.first()
            
            product = pallet.werehouse_exit_confirmation.exit_product_measurement.product
            locations = WarehouseLocation.objects.filter(shortcode= new_location)
            warehouse_location = locations.first()
            destination_location = warehouse_location.id
            destination_warehouse = warehouse_location.warehouse.id   
            
            if pallet.warehouse != None:
                source_warehouse = pallet.warehouse.id
            else:
                source_warehouse = ''
            if pallet.location != None:
                source_location = pallet.location.id
            else:
                source_location = ''
            customer = pallet.werehouse_exit_confirmation.werehouse_exit.customer.id
            product_id = product.id
            werehouse_entrance = pallet.inventory.warehouse_entrance_pallet.werehouse_entrance_confirmation.werehouse_entrance_id
            WarehouseRelocation.objects.create(
            customer_id = customer, 
            werehouse_entrance_id = werehouse_entrance,
            product_id = product_id,
            description = description,
            source_warehouse = source_warehouse,
            source_location = source_location,
            destination_warehouse_id = destination_warehouse,
            destination_location_id = destination_location,
            palet_lot = palet_lot)
        data_relocation = { "message":  "" }
        return HttpResponse(json.dumps(data_relocation))