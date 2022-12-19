from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Service


class ServiceList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/service/list.html'
    model = Service


class ServiceCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/service/create.html'
    model = Service
    fields = ['code', 'description', 'billable']


class ServiceDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/service/detail.html'
    model = Service
    fields = ['code', 'description', 'billable']


class ServiceDelete(LoginRequiredMixin, DeleteView):
    model = Service

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('service-list')
