from django.shortcuts import render
import datetime
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View
from django.views.generic.list import ListView
from catalogs.warehouse.models import Warehouse,WarehouseLocation
from django.forms import inlineformset_factory
from django.http import JsonResponse

# Create your views here.



class WarehouseLocationsAPIView(LoginRequiredMixin, ListView):
    template_name = 'warehouse/location_management/search.html'
    model = Warehouse
    # queryset = Warehouse.objects.all()

def warehouse_location_block_unblock(request,pk):
	location = WarehouseLocation.objects.get(id=pk)
	if location.is_locked:
		location.is_locked = False
	else:
		location.is_locked = True
	location.save()

	locations_data = {'status': location.is_locked}
	return JsonResponse(locations_data, safe=False)
