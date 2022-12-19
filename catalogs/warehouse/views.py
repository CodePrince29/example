import json
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from rest_framework.generics import ListCreateAPIView,CreateAPIView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from catalogs.product.models import Product
from catalogs.product_family.models import ProductFamily
from catalogs.clients.models import Client
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import JsonResponse


from .models import Warehouse, WarehouseLocation, WarehouseRow, WarehouseDepthLevel, WarehouseHeightLevel, \
    WarehouseSection,WarehouseInventory,WarehouseInventoryLog, Branch
from .forms import WarehouseForm,WarehouseInventoryLogForm
from .serializers import ProductFamilySerializer, WarehouseEntranceConfirmationSerializer,WarehouseExitConfirmationSerializer,WarehouseRelocationSerializer,WarehouseInventorySerializer,WarehouseInventoryFilterSerializer,WarehousePalletSerializer,WarehouseExitPalletSerializer
from warehouses.warehouse_entrance.models import WarehouseEntranceConfirmation,WarehouseEntrancePallet
from warehouses.warehouse_exit.models import WExitConfirmation,WarehouseExitPallet
from warehouses.warehouse_relocation.models import WarehouseRelocation
from django.http.response import HttpResponseRedirect
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from catalogs.utilities import WarehouseLocationPrams
from catalogs.general_params.models import GeneralParams
from django.contrib import messages

class WarehouseList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/warehouse/list.html'
    model = Warehouse


class WarehouseCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/warehouse/create.html'
    model = Warehouse
    form_class = WarehouseForm

    def form_valid(self, form):
        response = super(WarehouseCreate, self).form_valid(form)
        descriptions = json.loads(form.cleaned_data['descriptions'])
        location_numbering = 1
        section_numbering = 1
        for row in range(1, int(form.cleaned_data['rows'])+1):
            row_obj = WarehouseRow.objects.create(
                index=row,
                warehouse=self.object,
                description=descriptions['rows'].get(str(row))
            )
            for section in range(1, int(form.cleaned_data['sections_per_row'])+1):
                section_obj = WarehouseSection.objects.create(
                    index=section_numbering,
                    row=row_obj
                )
                for height in range(1, int(form.cleaned_data['height_levels'])+1):
                    height_obj = WarehouseHeightLevel.objects.create(
                        index=height,
                        section=section_obj,
                        description=descriptions['height_levels'].get(str(height))
                    )
                    for depth in range(1, int(form.cleaned_data['depth_levels'])+1):
                        warehouse_location_obj = WarehouseLocation.objects.create(
                            warehouse=self.object,
                            location_number=location_numbering
                        )
                        depth_obj = WarehouseDepthLevel.objects.create(
                            index=depth,
                            height=height_obj,
                            description=descriptions['depth_levels'].get(str(depth)),
                            warehouse_location=warehouse_location_obj
                        )
                        location_numbering += 1
                section_numbering +=1
        return response


class WarehouseDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/warehouse/detail.html'
    model = Warehouse
    form_class = WarehouseForm

    def get_context_data(self, **kwargs):
        context = super(WarehouseDetail, self).get_context_data(**kwargs)
        context.update({
            "products": Product.objects.all(),
            "product_family": ProductFamily.objects.all(),
            "clients": Client.objects.all()
        })
        return context

def warehouse_assign_short_code(request):
  if request.method == 'POST':
    import openpyxl
    code_assign = request.FILES['code_assign']
    wb = openpyxl.load_workbook(code_assign)
    worksheet = wb.active
    import pdb;
    counter = 1
    errors = False
    for row in worksheet.iter_rows():
      if (counter != 1):
        warehouse = row[0].value
        location_number = row[1].value
        short_code = row[2].value
        warehouse_detail = Warehouse.objects.get(code=warehouse)
        location = WarehouseLocation.objects.filter(warehouse_id=warehouse_detail.id, location_number= int(location_number))
        
        try:
          location.update(shortcode= short_code )
        except Exception as e:
          errors = True
        
      counter+=1
    if errors:
      response_message = "Parte de la ubicacion no se actualizo debido a un duplicado, verifique el archivo."
    else:
      response_message = "Codigo de acceso directo actualizado correctamente."

  messages.add_message(request, messages.SUCCESS, response_message)
  return HttpResponseRedirect(reverse('warehouse-list'))

def get_warehouse_location_detail(request):
    warehouse_uniq_code = request.GET['short_code']
    locations = WarehouseLocation.objects.filter(shortcode = warehouse_uniq_code)
    if locations.exists():
        location = locations.first()
        warehouse = location.warehouse
        section = warehouse.get_section_id(str(location.location_number))
        rack = WarehouseSection.objects.get( id= section )
        rack_detail = {"id": rack.id, "index": rack.index }
        warehouse_detail = {"id": warehouse.id, "code": warehouse.code, "description": warehouse.description }
        location_detail = {"id": location.id, "location_number": location.location_number }
        data = {"rack_detail": rack_detail, "warehouse_detail": warehouse_detail, "location_detail": location_detail, "location_not_found": False }
        
    else:
        data = {"rack_detail": {}, "warehouse_detail": {}, "location_detail": {} , "location_not_found": True}

    return JsonResponse(data, safe=False)

class WarehouseQRCodeGenerater(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/warehouse/warehouse_qr_code.html'
    model = Warehouse
    form_class = WarehouseForm

    def get_context_data(self, **kwargs):
        context = super(WarehouseQRCodeGenerater, self).get_context_data(**kwargs)
        context.update({
            "sections": WarehouseSection.objects.filter(row__warehouse__id= self.object.id)
        })
        return context
class WarehouseQRCodePrinter(ListView):
    model = WarehouseDepthLevel
    queryset = WarehouseDepthLevel.objects.all()    
    template_name = 'pdf/warehouse_qrcode_pdf.html'
    
    def get(self, request):
        from sga.render import Render
        printed_data = self.request.GET['printed_data'].split(",")
        query_set = WarehouseDepthLevel.objects.filter(id__in=printed_data)
        print2_locations = GeneralParams.objects.filter(key='Print2Locations')
        if print2_locations.exists():
            print_data = int(print2_locations.first().value)
        else:
            print_data = 0
        
        params = {
        'object_list': query_set,
        'print_data':print_data           
        }

        return Render.render('pdf/warehouse_qrcode_pdf.html',
       params)

class WarehouseUpdateDetails(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/warehouse/update_details.html'
    model = Warehouse
    form_class = WarehouseForm

    def get_context_data(self, **kwargs):
        context = super(WarehouseUpdateDetails, self).get_context_data(**kwargs)
        
        return context


class WarehouseDelete(LoginRequiredMixin, DeleteView):
    model = Warehouse

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse-list')


# class WarehouseLocationList(LoginRequiredMixin, ListView):
#     template_name = 'catalogs/warehouse_location/list.html'
#     model = WarehouseLocation
#
#
# class WarehouseLocationCreate(LoginRequiredMixin, CreateView):
#     template_name = 'catalogs/warehouse_location/create.html'
#     model = WarehouseLocation


class WarehouseLocationDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/warehouse_location/detail.html'
    model = WarehouseLocation

# class WarehouseProductFilter(LoginRequiredMixin, ListView):

#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)

#     def get_success_url(self):
#         return reverse_lazy('warehouselocation-list')

class WarehouseProductFilter(ListCreateAPIView):
    queryset = ProductFamily.objects.all()
    serializer_class = ProductFamilySerializer

    def get_queryset(self, pk=None):
        client = Client.objects.get(id= self.kwargs['pk'])
        return client.get_product_family()

class WarehouseLocationProduct(ListCreateAPIView):
    queryset = WarehouseEntrancePallet.objects.all()
    def get(self,request,*args,**kwargs):
        customer = self.kwargs['customer']
        if int(customer) != 0:
            location = WarehouseLocation.objects.filter(warehouse_id=kwargs['warehouse'],location_number=kwargs['location']).first()
            stored_kg = location.total_stored_kg
            stored_boxes = location.total_stored_boxes
            
            entrance_queryset = WarehouseEntrancePallet.objects.filter(warehouseinventory__available_total_boxes__gt=0,
                warehouse_id=self.kwargs['warehouse'],location__location_number=self.kwargs['location'],werehouse_entrance_confirmation__werehouse_entrance__customer_id=customer).select_related('werehouse_entrance_confirmation__product')

            entrance_serializer = WarehousePalletSerializer(data=entrance_queryset,many=True)
            entrance_serializer.is_valid()
            # location_number = [int(i) for i in self.kwargs['location']]
            exit_queryset = WarehouseExitPallet.objects.filter(inventory__available_total_boxes__gt=0,warehouse_id=self.kwargs['warehouse'],location__location_number=self.kwargs['location'],werehouse_exit_confirmation__werehouse_exit__customer_id=customer).select_related('werehouse_exit_confirmation__product')
            # exit_queryset = WExitConfirmation.objects.filter(id__in=[location.id for location in WExitConfirmation.objects.filter(warehouse__in=[self.kwargs['warehouse']],werehouse_exit__customer_id=customer).select_related('product') if all([z in [int(i) for i in location.location.split(",")] for z in location_number ]) ])
            # exit_serializer = WarehouseExitConfirmationSerializer(data=exit_queryset,many=True)
            exit_serializer = WarehouseExitPalletSerializer(data=exit_queryset,many=True)
            relocation = WarehouseRelocation.objects.filter((Q(source_warehouse=self.kwargs['warehouse'],source_location=self.kwargs['location']) | Q(destination_warehouse=self.kwargs['warehouse'],destination_location__location_number =self.kwargs['location'])) & Q(customer_id=customer))
            relocation_serializer = WarehouseRelocationSerializer(data=relocation,many=True)

            inventory_queryset = WarehouseInventory.objects.filter(available_total_boxes__gt=0,warehouse_location__warehouse=self.kwargs['warehouse'],warehouse_location__location_number=self.kwargs['location'],client_id=customer).select_related('product')

            inventory_serializer = WarehouseInventorySerializer(data=inventory_queryset,many=True)

            entrance_serializer.is_valid()
            exit_serializer.is_valid()
            relocation_serializer.is_valid()
            inventory_serializer.is_valid()

            data_entrance = [{"entrance_conf": entrance_serializer.data},{"exit_conf": exit_serializer.data},{"relocation_serializer": relocation_serializer.data},{"inventory_serializer": inventory_serializer.data},{"stored_kg": stored_kg},{"stored_boxes": stored_boxes}]
            return HttpResponse(json.dumps(data_entrance))
        else:
            location = WarehouseLocation.objects.filter(warehouse_id=kwargs['warehouse'],location_number=kwargs['location']).first()
            stored_kg = location.total_stored_kg
            stored_boxes = location.total_stored_boxes
            entrance_queryset = WarehouseEntrancePallet.objects.filter(warehouseinventory__available_total_boxes__gt=0,warehouse_id=self.kwargs['warehouse'],location__location_number=self.kwargs['location']).select_related('werehouse_entrance_confirmation__product')
            entrance_serializer = WarehousePalletSerializer(data=entrance_queryset,many=True)
            # location_number = [int(i) for i in self.kwargs['location']]
            # exit_queryset = WExitConfirmation.objects.filter(warehouse=self.kwargs['warehouse'],location=self.kwargs['location']).select_related('product')
            # exit_serializer = WarehouseExitConfirmationSerializer(data=exit_queryset,many=True)
            exit_queryset = WarehouseExitPallet.objects.filter(inventory__available_total_boxes__gt=0,warehouse_id=self.kwargs['warehouse'],location__location_number=self.kwargs['location']).select_related('werehouse_exit_confirmation__product')
            exit_serializer = WarehouseExitPalletSerializer(data=exit_queryset,many=True)
            relocation = WarehouseRelocation.objects.filter(Q(source_warehouse=self.kwargs['warehouse'],source_location=self.kwargs['location']) | Q(destination_warehouse=self.kwargs['warehouse'],destination_location__location_number =self.kwargs['location']))
            
            relocation_serializer = WarehouseRelocationSerializer(data=relocation,many=True)

            inventory_queryset = WarehouseInventory.objects.filter(available_total_boxes__gt=0,warehouse_location__warehouse=self.kwargs['warehouse'],warehouse_location__location_number=self.kwargs['location']).select_related('product')

            inventory_serializer = WarehouseInventorySerializer(data=inventory_queryset,many=True)

            entrance_serializer.is_valid()
            exit_serializer.is_valid()
            relocation_serializer.is_valid()
            inventory_serializer.is_valid()
            
            data_entrance = [{"entrance_conf": entrance_serializer.data},{"exit_conf": exit_serializer.data},{"relocation_serializer": relocation_serializer.data},{"inventory_serializer": inventory_serializer.data},{"stored_kg": stored_kg},{"stored_boxes": stored_boxes}]
            return HttpResponse(json.dumps(data_entrance))

class WarehouseInventoryList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/warehouse/inventory_list.html'
    model = WarehouseInventory
    def get_context_data(self, **kwargs):
        context = super(WarehouseInventoryList, self).get_context_data(**kwargs)
        context['locations'] = WarehouseLocation.objects.all()
        context['warehouses'] = Warehouse.objects.all()
        context['clients'] = Client.objects.all()
        context['products'] = Product.objects.all()
        return context

class WarehouseInventoryFilterAPI(LoginRequiredMixin, CreateAPIView):
    # GGV make load faster
    queryset = WarehouseInventory.objects.all()
    serializer_class = WarehouseInventoryFilterSerializer
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        from datetime import datetime
        warehouse = self.request.POST.get('warehouse', '')
        location = self.request.POST.get('warehouse_location', '')
        product = self.request.POST.get('product', '')
        lote_tarima = self.request.POST.get('lote_tarima', '')
        client = self.request.POST.get('client', '')
        expire_date = self.request.POST.get('expire_date', '')
        lote_cliente = self.request.POST.get('lote_cliente', '')
        query_list = {}
        
        if client == 'ALL':
            customers = tuple(Client.objects.all())
        else:
            customers = [] if client == '' else tuple(Client.objects.filter(id = client))

        if product == 'ALL' and client != '':
            products = tuple(Product.objects.filter(customer_id__in=customers))
        
        elif product == 'ALL' and client == '':
            products = tuple(Product.objects.all())
        else:
            products = [] if product == '' else tuple(Product.objects.filter(id =product))
        if client != '':
            query_list.update(client__in=customers)
        if product != '':
            query_list.update(product__in=products)

        if location != '':
            query_list.update(warehouse_location=location)
        if warehouse != '':
            query_list.update(warehouse_entrance_pallet__warehouse=warehouse)
        if lote_tarima != '':
            query_list.update(warehouse_entrance_pallet__palet_lot=lote_tarima)

        if lote_cliente != '':
            query_list.update(warehouse_entrance_pallet__cost_lot=lote_cliente)

        if expire_date != '':
            query_list.update(exp_date__gte=expire_date)
        result = WarehouseInventory.objects.filter(**query_list) #WarehouseInventory.objects.filter(warehouse_location=location,warehouse_entrance_confirmation__warehouse=warehouse)
        if len(result) > 0:
            url = "<a role='button' href='/warehouses/warehouse_inventories/{}/edit' class='btn btn-success'><i class='fa fa-edit'></i></a>"
            result = [[data.client.name, data.product.product_description , data.total_kg,data.total_boxes,data.retained_boxes, url.format(data.id)] for data in result]
        return Response(tuple(result))

class WarehouseInventoryEdit(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/warehouse/edit_inventory.html'
    model = WarehouseInventoryLog
    form_class = WarehouseInventoryLogForm

    def get_object(self):
       return WarehouseInventory.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        inventory_log = self.form_class(self.request.POST)
        inventory_log.is_valid()
        inv_log = inventory_log.save(commit=False)
        inv_log.user = self.request.user
        inv_log.save()
        request_params = self.request.POST
        inventory = self.get_object()
        inventory.total_kg = request_params['total_kg']
        inventory.total_boxes = request_params['total_boxes']
        inventory.retained_boxes = request_params['retained_boxes']
        #GGV update available kg and boxes
        inventory.available_gross_weight = request_params['total_kg']
        inventory.available_net_weight = request_params['total_kg']
        inventory.available_total_boxes = request_params['total_boxes']
        inventory.save()

        from django.shortcuts import reverse
        return HttpResponseRedirect(reverse('warehouse-inventory-list'))

class WarehouseUpdateDepthAPI(LoginRequiredMixin, CreateAPIView):    
    queryset = WarehouseDepthLevel.objects.all()
    def post(self, request, *args, **kwargs):
        from datetime import datetime
        depth_mts = self.request.POST['depth_mts']
        depth_id = self.request.POST['depth_id']
        height_mts = self.request.POST['height_mts']
        width_mts = self.request.POST['width_mts']
        weight_kg = self.request.POST['weight_kg']
        depth = WarehouseDepthLevel.objects.get(id=depth_id)
        depth.depth_mts = float(depth_mts)
        depth.height_mts = float(height_mts)
        depth.width_mts = float(width_mts)
        depth.weight_kg = float(weight_kg)        
        total_volume = (depth.depth_mts * depth.height_mts * depth.width_mts)
        depth.location_volume = round(float(total_volume),2)
        
        
       
        location = depth.warehouse_location

        available_weight,available_volume = WarehouseLocationPrams().get_location_params(location)    
        
        location.available_weight = float(weight_kg)-available_weight
        
        location.available_volume = round(float(total_volume),2)-available_volume
       
        if location.available_weight<0 or location.available_volume<0:
            return Response({'available_weight':available_weight,'available_volume':available_volume,'location_weight':location.available_weight,'location_volume':location.available_volume,'message':'failed',"code": 500})
        else:
            location.save()
            depth.save()
            return Response({'message':'success',"code": 200})


class WarehouseBranchList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/branches/branch_list.html'
    model = Branch

class WarehouseBranchCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/branches/create.html'
    model = Branch
    fields = '__all__'
    success_url = reverse_lazy('branch-list')

class WarehouseBranchUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/branches/create.html'
    model = Branch
    fields = '__all__'
    success_url = reverse_lazy('branch-list')

class WarehouseBranchDelete(LoginRequiredMixin, DeleteView):
    model = Branch
    success_url = reverse_lazy('branch-list')
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
