from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from .models import Service
from catalogs.price_list.models import PriceList, ServiceRelation


class PriceListForm(forms.ModelForm):
    code = forms.CharField(
        label=_('Code'),
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    description = forms.CharField(
        label=_('Description'),
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    # is_baseline = forms.BooleanField(
    #     label=_('Baseline Price List'),
    #     widget=forms.CheckboxInput()
    # )

    class Meta:
        model = PriceList
        fields = ['code', 'description', 'is_baseline']


class PriceListItemForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        label=_('Service'),
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.FloatField(
        label=_('Price'),
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        )
    )

    class Meta:
        model = ServiceRelation
        fields = ['service', 'price']


PriceListItemsFormSet = inlineformset_factory(
    PriceList, ServiceRelation, exclude=('id',), extra=2, form=PriceListItemForm,
    can_delete=False
)
