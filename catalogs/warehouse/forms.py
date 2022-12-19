from django import forms

from .models import Warehouse,WarehouseInventory,WarehouseInventoryLog


class WarehouseForm(forms.ModelForm):
    descriptions = forms.CharField()

    class Meta:
        model = Warehouse
        fields = ('code', 'description', 'descriptions', 'rows', 'sections_per_row', 'depth_levels', 'height_levels')



class WarehouseInventoryLogForm(forms.ModelForm):
    class Meta:
        model = WarehouseInventoryLog
        fields = ('warehouse_inventory','total_kg','total_boxes', 'retained_boxes', 'adjust_reason', 'description')
