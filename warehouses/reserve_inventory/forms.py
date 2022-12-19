from django import forms
from .models import ReserveInventory


class ReserveInventoryForm(forms.ModelForm):
    class Meta:
        model = ReserveInventory
        fields = '__all__'
        exclude = ('created_by',)

        widgets = {
            'notes': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
            'palet_lot': forms.TextInput(attrs={'required': 'true'}),
            'released_store_box': forms.HiddenInput(),
            'inventory': forms.HiddenInput()
        }
        

    def __init__(self, *args, **kwargs):
        super(ReserveInventoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:    
            if field == 'palet_lot' or field == "boxes":
                self.fields[field].widget.attrs['readonly'] = 'true'
            elif field == 'reserve_boxes' or field == "boxes":
                self.fields[field].widget.attrs['min'] = '0'
            self.fields[field].widget.attrs['class'] = 'form-control'