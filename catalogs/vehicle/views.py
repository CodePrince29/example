from django.shortcuts import render

# Create your views here.


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Vehicle


class VehicleList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/vehicle/list.html'
    model = Vehicle


class VehicleCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/vehicle/create.html'
    model = Vehicle
    fields = ['code', 'description','capicity']


class VehicleParamUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/vehicle/detail.html'
    model = Vehicle
    fields = ['code', 'description','capicity']


class VehicleDelete(LoginRequiredMixin, DeleteView):
    model = Vehicle

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('vehicle-list')

