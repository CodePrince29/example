from django import forms
from .models import Product

from catalogs.product_family.models import ProductFamily
from catalogs.clients.models import Client
from catalogs.packaging.models import Packaging


class ProductForm(forms.ModelForm):
    BARCODE_CHOICES =(
    ("", "---------"), 
    ("bc_sasa", "Codigo SASA"),
    ("BC_Yoreme", "Yoreme"), 
    ("BC_LaVeinte", "Laveinte"), 
    ("BC_Carnicos", "Productos Carnicos"), 
    ("BC_GCM", "GCM"), 
    ("BC_Cicaba", "Cicaba"),
    ("BC_Integra", "Integra"),
    ("BC_Integra2", "Integra2"),
    ("BC_Bonacarne", "Bonacarme"),
    ("BC_Soles", "Codigo Soles"),
    ("Codigo Ayvi", "Codigo Ayvi"),
    ) 
    product_family = forms.ModelChoiceField(
        queryset=ProductFamily.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': "product_customer"})
    )
    package_type = forms.ModelChoiceField(
        queryset=Packaging.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    barcode_to_use = forms.ChoiceField(
        choices = BARCODE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'} )
    )
    class Meta:
        model = Product
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'barcode_to_use':
                self.fields[field].required = False
                if kwargs['instance']:
                    if kwargs['instance'].customer.barcoderead:
                        self.fields[field].widget.attrs['required'] = True
