from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Packaging


class PackagingList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/packaging/list.html'
    model = Packaging


class PackagingCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/packaging/create.html'
    model = Packaging
    fields = ['code', 'description']


class PackagingDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/packaging/detail.html'
    model = Packaging
    fields = ['code', 'description']


class PackagingDelete(LoginRequiredMixin, DeleteView):
    model = Packaging

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('packaging-list')
