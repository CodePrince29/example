from django import forms
from catalogs.clients.models import Client
from catalogs.product.models import Product


class HistoryListForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Product
        fields = '__all__'