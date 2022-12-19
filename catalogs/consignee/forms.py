from django import forms
from .models import Consignee

from catalogs.clients.models import Client


class ConsigneeForm(forms.ModelForm):    
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )   

    class Meta:
        model = Consignee
        fields = '__all__'
