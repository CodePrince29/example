from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import PriceList, ServiceRelation
from .forms import PriceListForm, PriceListItemForm, PriceListItemsFormSet


class PriceListList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/price_list/list.html'
    model = PriceList


class PriceListCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/price_list/create.html'
    model = PriceList
    form_class = PriceListForm

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        item_form = PriceListItemsFormSet()
        return self.render_to_response(
            self.get_context_data(
                form=form,
                item_form=item_form,
            )
        )

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        item_form = PriceListItemsFormSet(self.request.POST)
        if form.is_valid() and item_form.is_valid():
            return self.form_valid(form, item_form)
        else:
            return self.form_invalid(form, item_form)

    def form_valid(self, form, item_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        item_form.instance = self.object
        item_form.save()
        item_form.instance = self.object
        item_form.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, item_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(
                form=form,
                item_form=item_form
            )
        )


class PriceListDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/price_list/detail.html'
    model = PriceList
    fields = ['code', 'description', 'is_baseline']


class PriceListDelete(LoginRequiredMixin, DeleteView):
    model = PriceList

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('pricelist-list')


class ServiceRelationList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/pricelist_service_relation/list.html'
    model = ServiceRelation


class ServiceRelationCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/pricelist_service_relation/create.html'
    model = ServiceRelation
    form_class = PriceListItemForm


class ServiceRelationDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/pricelist_service_relation/detail.html'
    model = ServiceRelation
    form_class = PriceListItemForm


class ServiceRelationDelete(LoginRequiredMixin, DeleteView):
    model = ServiceRelation

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('pricelistservicerelation-list')
