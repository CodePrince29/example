from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import GeneralParams


class CapacityList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/general_params/list.html'
    model = GeneralParams


class GeneralParamCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/general_params/create.html'
    model = GeneralParams
    fields = ['key', 'value', 'description']


class GeneralParamUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/general_params/detail.html'
    model = GeneralParams
    fields = ['key', 'value', 'description']


class GeneralParamDelete(LoginRequiredMixin, DeleteView):
    model = GeneralParams

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('gp-list')
