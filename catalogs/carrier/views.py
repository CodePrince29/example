from django.shortcuts import render

# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Carrier


class CarrierList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/carrier/list.html'
    model = Carrier


class CarrierCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/carrier/create.html'
    model = Carrier
    fields = ['code', 'name','telephone','address','email','attend_person']


class CarrierParamUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/carrier/detail.html'
    model = Carrier
    fields = ['code', 'name','telephone','address','email','attend_person']


class CarrierDelete(LoginRequiredMixin, DeleteView):
    model = Carrier

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('carrier-list')

