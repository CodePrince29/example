from django.shortcuts import render
import datetime
# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from rest_framework.permissions import IsAuthenticated, BasePermission

from warehouses.warehouse_entrance.models import WarehouseEntrance
from warehouses.warehouse_exit.models import WarehouseExit
from catalogs.warehouse.models import Warehouse
from catalogs.clients.models import Client
from catalogs.product.models import Product
from rest_framework.generics import ListCreateAPIView, CreateAPIView
from .serializers import WarehouseEntranceSerializer
from .filters import EntranceFilter, ExitFilter

class HistoryList(LoginRequiredMixin, CreateView):
    template_name = 'warehouse/warehouse_history/list.html'
    model = WarehouseEntrance
    fields = ['entrance_date','entrance_hour']
    def get_context_data(self, **kwargs):
	    context = super(HistoryList, self).get_context_data(**kwargs)
	    context['products'] = Product.objects.all()
	    if self.request.user.is_staff:
	    	context['customers'] = Client.objects.all()
	    else:
	    	context['customers'] = self.request.user.client_set.all()
	    return context


class IsCustomerInSGA(BasePermission):
    def has_object_permission(self, request, view, academy):
        return not request.user.is_staff

class WarehouseEntranceProductFilter(CreateAPIView):
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
			url1 = "<a role='button' href='/warehouse_entrance/new-confirm-entrance-pallets/{}' class='btn btn-warning'><i class='fa fa-eye'></i></a>"
			url2 = "<a role='button' href='/warehouse_entrance/{}/download-entrace-invoice/' class='btn btn-info'><i class='fa fa-print'></i></a>"
			if self.request.user.is_staff:
				queryset_entrance = [[data.customer.name, [product.product.product_code for product in data.wproductmeasurement_set.all()] , "Entrada",data.id, data.entrance_date, data.total_kg, url1.format(data.id),url2.format(data.id)] for data in queryset_entrance]
			else:
				queryset_entrance = [[data.customer.name, [product.product.product_code for product in data.wproductmeasurement_set.all()] , "Entrada",data.id, data.entrance_date, data.total_kg, url1.format(data.id),url2.format(data.id)] for data in queryset_entrance]
				# queryset_entrance = [[data.customer.name, [product.product.product_code for product in data.wproductmeasurement_set.all()] , "Entrada",data.id, data.entrance_date, data.total_kg] for data in queryset_entrance]

			
		if len(queryset_exit) > 0:
			url1 = "<a role='button' href='/warehouse_exit/confirm-warehouse-exit/{}' class='btn btn-warning'><i class='fa fa-eye'></i></a>"
			url2 = "<a role='button' href='/warehouse_exit/{}/download-exit-invoice/' class='btn btn-info'><i class='fa fa-print'></i></a>"
			if self.request.user.is_staff:
				queryset_exit = [[data.customer.name, [product.product.product_code for product in data.wexitproductmeasurement_set.all()] , "Salida", data.id ,data.exit_date, (data.total_kg if data.total_kg != None else 0 ), url1.format(data.id), url2.format(data.id)] for data in queryset_exit]
			else:
				queryset_exit = [[data.customer.name, [product.product.product_code for product in data.wexitproductmeasurement_set.all()] , "Salida", data.id ,data.exit_date, (data.total_kg if data.total_kg != None else 0 ), url1.format(data.id), url2.format(data.id)] for data in queryset_exit]
				# queryset_exit = [[data.customer.name, [product.product.product_code for product in data.wexitproductmeasurement_set.all()] , "Salida", data.id ,data.exit_date, (data.total_kg if data.total_kg != None else 0 )] for data in queryset_exit]
		data = tuple(queryset_exit)+tuple(queryset_entrance)
		return Response(data)

