from datetime import datetime as dt
from pprint import pformat
import logging
import operator

from django import forms

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    # django < 1.7 support
    from django.db.models import get_model

from django.conf import settings
from django.contrib import admin

try:
    from django.contrib.admin.utils import get_fields_from_path
except ImportError:
    # django < 1.7 support
    from django.contrib.admin.util import get_fields_from_path

from django.db.models import Q, FieldDoesNotExist
from django.db.models.fields import DateField
from django.forms.formsets import formset_factory, BaseFormSet
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves import range, reduce
from django.utils.text import capfirst

import django
from warehouses.warehouse_entrance.models import *
from advanced_filters.models import AdvancedFilter
from advanced_filters.form_helpers import CleanWhiteSpacesMixin,  VaryingTypeCharField
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.clients.models import Client
def date_to_string(timestamp):
    if timestamp:
        return dt.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    else:
        return ""


class AdvancedFilterQueryForm(CleanWhiteSpacesMixin, forms.Form):
    """ Build the query from field, operator and value """
    OPERATORS = (
        ("iexact", _("Igual")),
        ("icontains", _("Contiene")),
        ("iregex", _("Uno de")),
        ("daterange", _("Rango de fechas")),
        ("timerange", _("Tiempo igual")),
        ("isnull", _("Es nulo")),
        ("istrue", _("Es verdad")),
        ("isfalse", _("Es falso")),
        ("lt", _("Menos que")),
        ("gt", _("Mas grande que")),
        ("lte", _("Menos que o igual a")),
        ("gte", _("Mayor que o igual a")),
    )

    ORDERVALUE = (
        ("", _("-------")),
        ("ascending", _("ascending")),
        ("descending", _("descending")),
        
    )

    FIELD_CHOICES = (
        ("_OR", _("Or (mark an or between blocks)")),
    )

    field = forms.ChoiceField(required=True, widget=forms.Select(
        attrs={'class': 'form-control query-field'}), label=_('Field'))
    operator = forms.ChoiceField(
        label=_('Operator'),
        required=True, choices=OPERATORS, initial="iexact",
        widget=forms.Select(attrs={'class': 'form-control query-operator'}))

    ordering_data = forms.ChoiceField(
        label=_('Ordering A/D'),
        required=True, choices=ORDERVALUE, initial="",
        widget=forms.Select(attrs={'class': 'form-control query-ordering'}))

    value = VaryingTypeCharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control query-value'}), label=_('Value'))
    value_from = forms.DateTimeField(widget=forms.HiddenInput(
        attrs={'class': 'form-control query-dt-from'}), required=False)
    value_to = forms.DateTimeField(widget=forms.HiddenInput(
        attrs={'class': 'form-control query-dt-to'}), required=False)
    negate = forms.BooleanField(initial=False, required=False, label=_('Negate'))

    def _build_field_choices(self, fields):
        """
        Iterate over passed model fields tuple and update initial choices.
        """
        return fields

    def _build_query_dict(self, formdata=None):
        """
        Take submitted data from .form and create a query dict to be
        used in a Q object (or filter)
        """
        if self.is_valid() and formdata is None:
            formdata = self.cleaned_data
        key = "{field}__{operator}".format(**formdata)
        if formdata['operator'] == "isnull":
            return {key: None}
        elif formdata['operator'] == "istrue":
            return {formdata['field']: True}
        elif formdata['operator'] == "isfalse":
            return {formdata['field']: False}
        return {key: formdata['value']}

    @staticmethod
    def _parse_query_dict(query_data, model):
        """
        Take a list of query field dict and return data for form initialization
        """
        operator = 'iexact'
        if query_data['field'] == '_OR':
            query_data['operator'] = operator
            return query_data

        parts = query_data['field'].split('__')
        if len(parts) < 2:
            field = parts[0]
        else:
            if parts[-1] in dict(AdvancedFilterQueryForm.OPERATORS).keys():
                field = '__'.join(parts[:-1])
                operator = parts[-1]
            else:
                field = query_data['field']

        query_data['field'] = field
        mfield = get_fields_from_path(model, query_data['field'])
        if not mfield:
            raise Exception('Field path "%s" could not be followed to a field'
                            ' in model %s', query_data['field'], model)
        else:
            mfield = mfield[-1]  # get the field object

        if query_data['value'] is None:
            query_data['operator'] = "isnull"
        elif query_data['value'] is True:
            query_data['operator'] = "istrue"
        elif query_data['value'] is False:
            query_data['operator'] = "isfalse"
        else:
            if isinstance(mfield, DateField):
                # this is a date/datetime field
                query_data['operator'] = "range"  # default
            else:
                query_data['operator'] = operator  # default

        if isinstance(query_data.get('value'),
                      list) and query_data['operator'] == 'range':
            date_from = date_to_string(query_data.get('value_from'))
            date_to = date_to_string(query_data.get('value_to'))
            query_data['value'] = ','.join([date_from, date_to])

        return query_data

    def set_range_value(self, data):
        """
        Validates date range by parsing into 2 datetime objects and
        validating them both.
        """
        dtfrom = data.pop('value_from')
        dtto = data.pop('value_to')
        if dtfrom is dtto is None:
            self.errors['value'] = ['Date range requires values']
            raise forms.ValidationError([])
        data['value'] = (dtfrom, dtto)

    def clean(self):
        cleaned_data = super(AdvancedFilterQueryForm, self).clean()
        if cleaned_data.get('operator') == "range":
            if ('value_from' in cleaned_data and
                    'value_to' in cleaned_data):
                self.set_range_value(cleaned_data)
        return cleaned_data

    def make_query(self, *args, **kwargs):
        """ Returns a Q object from the submitted form """
        query = Q()  # initial is an empty query
        query_dict = self._build_query_dict(self.cleaned_data)
        if 'negate' in self.cleaned_data and self.cleaned_data['negate']:
            query = query & ~Q(**query_dict)
        else:
            query = query & Q(**query_dict)
        return query

    def __init__(self, model_fields={}, *args, **kwargs):
        super(AdvancedFilterQueryForm, self).__init__(*args, **kwargs)
        self.FIELD_CHOICES = self._build_field_choices(model_fields)
        self.fields['field'].choices = self.FIELD_CHOICES
        if not self.fields['field'].initial:
            self.fields['field'].initial = self.FIELD_CHOICES[0]


class AdvancedFilterFormSet(BaseFormSet):
    fields = ()
    extra_kwargs = {}

    def __init__(self, *args, **kwargs):       

        entrance_fields = []
        customer_fields = []
        measurment_fields = []
        vehicleinspection_fields = []
        confirmation_fields = []
        wincidenceproduct_fields = []
        carrier_fields = []
        vehicle_fields = []

        [entrance_fields.append(("{}".format(field.name), field.verbose_name)) for field in WarehouseEntrance._meta.get_fields() if not field.is_relation]
        [customer_fields.append(("customer__{}".format(field.name), field.verbose_name)) for field in Client._meta.get_fields() if not field.is_relation]
        [measurment_fields.append(("wproductmeasurement__{}".format(field.name), field.verbose_name)) for field in WProductMeasurement._meta.get_fields() if not field.is_relation]
        [confirmation_fields.append(("warehouseentranceconfirmation__{}".format(field.name), field.verbose_name)) for field in WarehouseEntranceConfirmation._meta.get_fields() if not field.is_relation]
        [wincidenceproduct_fields.append(("wincidenceproduct__{}".format(field.name), field.verbose_name)) for field in WIncidenceProduct._meta.get_fields() if not field.is_relation]
        [carrier_fields.append(("carrier__{}".format(field.name), field.verbose_name)) for field in Carrier._meta.get_fields() if not field.is_relation]
        [vehicle_fields.append(("vehicle__{}".format(field.name), field.verbose_name)) for field in Vehicle._meta.get_fields() if not field.is_relation]

        self.model_fields = tuple([
           (_('Warehouse Entrance'),tuple(entrance_fields)),
           (_('Customer'), tuple(customer_fields)),
           (_('Warehouse Product Measurement'), tuple(measurment_fields)),
           (_('Warehouse Product Entrance Confirmation'), tuple(confirmation_fields)),
           (_('Carrier'), tuple(carrier_fields)),
           (_('Vehicle'), tuple(vehicle_fields)),
           (_('Warehouse Incidence Product'), tuple(wincidenceproduct_fields))])

       
        super(AdvancedFilterFormSet, self).__init__(*args, **kwargs)
        if self.forms:
            form = self.forms[0]
            self.fields = form.visible_fields()


    @property
    def empty_form(self):
        form = self.form(
            model_fields=self.model_fields,
            auto_id=self.auto_id,
            prefix=self.add_prefix('__prefix__'),
            empty_permitted=True,

        )
        self.add_fields(form, None)
        return form

    def _construct_forms(self):
        # not strictly required, but Django 1.5 calls this on init
        # django == 1.5 support
        self.forms = []
        for i in range(min(self.total_form_count(), self.absolute_max)):
            self.forms.append(self._construct_form(
                i, model_fields=self.model_fields))

    @cached_property
    def forms(self):
        # override the original property to include `model_fields` argument
        forms = [self._construct_form(i, model_fields=self.model_fields)
                 for i in range(self.total_form_count())]
        forms.append(self.empty_form)  # add initial empty form
        return forms

AFQFormSet = formset_factory(
    AdvancedFilterQueryForm, formset=AdvancedFilterFormSet,
    extra=0, can_delete=True)

AFQFormSetNoExtra = formset_factory(
    AdvancedFilterQueryForm, formset=AdvancedFilterFormSet,
    extra=0, can_delete=True)

