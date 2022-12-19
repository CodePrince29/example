from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import ProductFamily


class ProductFamilyList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/product_family/list.html'
    model = ProductFamily


class ProductFamilyCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/product_family/create.html'
    model = ProductFamily
    fields = ['code', 'description']


class ProductFamilyDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/product_family/detail.html'
    model = ProductFamily
    fields = ['code', 'description']


class ProductFamilyDelete(LoginRequiredMixin, DeleteView):
    model = ProductFamily

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('productfamily-list')
