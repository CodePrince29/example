from django.shortcuts import render

# Create your views here.


from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Consignee
from .forms import ConsigneeForm


class ConsigneeList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/consignee/list.html'
    model = Consignee


class ConsigneeCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/consignee/create.html'
    model = Consignee
    # fields = ['code', 'name','client','email','contact_phone','signature']
    form_class = ConsigneeForm
    


class ConsigneeParamUpdate(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/consignee/detail.html'
    model = Consignee
    # fields = ['code', 'name','client','email','contact_phone']
    form_class = ConsigneeForm


class ConsigneeDelete(LoginRequiredMixin, DeleteView):
    model = Consignee

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('consignee-list')


