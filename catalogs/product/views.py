from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
import pdb
from .models import Product
from .models import Client
from .forms import ProductForm
from ..utilities import WarehouseLocationPrams
from catalogs.warehouse.models import WarehouseDepthLevel
from django.http import JsonResponse

class ProductList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/product/list.html'
    model = Product


class ProductCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/product/create.html'
    model = Product
    form_class = ProductForm
    def get_context_data(self, **kwargs):
        context = super(ProductCreate, self).get_context_data(**kwargs)
        context['product_customers']  = Client.objects.all()
        return context 

class ProductDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/product/detail.html'
    model = Product
    form_class = ProductForm
    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context['product_customers']  = Client.objects.all()
        return context  

class ProductDelete(LoginRequiredMixin, DeleteView):
    model = Product

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('product-list')

def location_update(request):
    product_id = request.POST.get('product_id')
    net_weight = request.POST.get('net_weight')
    length = request.POST.get('length')
    width = request.POST.get('width')
    height = request.POST.get('height')
    product = Product.objects.get(pk=product_id)
    if product:
        for confirm in product.warehouseentranceconfirmation_set.filter(werehouse_entrance__status='finish'):
            for pallet in confirm.warehouseentrancepallet_set.all():
                available_weight,available_volume = WarehouseLocationPrams().get_location_params(pallet.location)
                
                depths = WarehouseDepthLevel.objects.filter(warehouse_location_id = pallet.location.id)
                if depths.exists():
                    for depth in depths:
                        pallet.location.available_weight = depth.weight_kg-available_weight
                        pallet.location.available_volume = depth.location_volume-available_volume
                        pallet.location.save()
    return JsonResponse({"message": "success","code": 200}, safe=True)


