from django import forms
from .models import WarehouseRelocation

from catalogs.clients.models import Client
from catalogs.product.models import Product
from catalogs.warehouse.models import Warehouse,WarehouseLocation
from warehouses.warehouse_entrance.models import WarehouseEntrance


class RelocationForm(forms.ModelForm):

    class Meta:
        model = WarehouseRelocation
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(RelocationForm, self).__init__(*args, **kwargs)
        werehouse_entrance = [(u'',u'')] 
        werehouse_entrance.extend([
            (
                c.pk, 
                c.id
            ) for c in WarehouseEntrance.objects.all()
        ])

        self.fields['werehouse_entrance'].choices = werehouse_entrance

        for field in self.fields:    
            if field == 'werehouse_entrance' or field == 'palet_lot' or field == "source_warehouse" or field == "source_location" :           
                self.fields[field].required = False
            self.fields[field].widget.attrs['class'] = 'form-control'