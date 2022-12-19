from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Unit


class UnitList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/unit/list.html'
    model = Unit


class UnitCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/unit/create.html'
    model = Unit
    fields = ['code', 'description']


class UnitDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/unit/detail.html'
    model = Unit
    fields = ['code', 'description']


class UnitDelete(LoginRequiredMixin, DeleteView):
    model = Unit

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('unit-list')
