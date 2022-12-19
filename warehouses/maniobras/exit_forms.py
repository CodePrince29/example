from django import forms
from warehouses.warehouse_exit.models import WarehouseExit, WarehouseExitPallet, WExitConfirmation
from django.forms.models import BaseInlineFormSet, inlineformset_factory

class WExitConfirmationForm(forms.ModelForm):

    auto_pick_data = forms.CharField(widget=forms.Textarea, label='')
    

    class Meta:
        model = WExitConfirmation
        fields= ('product',
                'cost_lot',
                'exp_date',
                'gross_weight',
                'net_weight',
                'invoice_weight',
                'retained_quantity',
                'retained_reason',
                )

    def __init__(self, *args, **kwargs):


        super(WExitConfirmationForm, self).__init__(*args, **kwargs)
        
        for field in self.fields:  
            if field == 'exp_date':
                self.fields[field].widget.attrs['class'] = 'form-control datepicker'
            elif field == 'auto_pick_data':
                self.fields[field].required = False
                self.fields[field].widget.attrs['class'] = 'form-control  hide'
            elif ((field == 'invoice_weight') or (field == 'retained_quantity') or (field == 'retained_reason')):
                self.fields[field].widget.attrs['class'] = 'form-control'
            elif field in ['removed_kgs']:
                self.fields[field].widget.attrs['class'] = 'form-control'
            elif field in ['removed_boxes']:
                self.fields[field].widget.attrs['class'] = 'form-control'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control'
            self.fields[field].widget.attrs['readonly'] = True


WExitConfirmationFormSet = inlineformset_factory(WarehouseExit, WExitConfirmation
    ,extra=0, min_num=1, form=WExitConfirmationForm,can_delete=True)


class WarehouseExitPalletMForm(forms.ModelForm):
    class Meta:
        model = WarehouseExitPallet
        fields=('id','palet_lot', 'boxes', 'box_kg','warehouse','rack_number','location','cost_lot','exp_date','gross_weight','net_weight','invoice_weight','retained_quantity','retained_reason','inventory','werehouse_exit_confirmation','confirmed')
        widgets= {
                'werehouse_exit_confirmation': forms.TextInput(attrs={'class': 'hide'}),    
                'palet_lot': forms.TextInput(attrs={'class': 'form-control palet_lot', 'readonly': True}),
                'boxes': forms.TextInput(attrs={'class': 'form-control boxes required-field required-pallet', 'readonly': True}),
                'box_kg': forms.TextInput(attrs={'class': 'form-control box_kg required-field required-pallet', 'readonly': True}),
                'warehouse': forms.Select(attrs={'class': 'form-control warehouse required-field required-pallet'}),
                'rack_number': forms.Select(attrs={'class': 'form-control rack_number required-field required-pallet'}),
                'location': forms.Select(attrs={'class': 'form-control location required-field required-pallet'}),
                'inventory': forms.Select(attrs={'class': 'form-control inventory required-field required-pallet'}),
                'cost_lot': forms.TextInput(attrs={'class': 'form-control cost_lot required-field required-pallet'}),
                'exp_date': forms.TextInput(attrs={'class': 'form-control exp_date datepicker required-field required-pallet'}),
                'gross_weight': forms.NumberInput(attrs={'class': 'form-control gross_weight required-field required-pallet'}),
                'net_weight': forms.NumberInput(attrs={'class': 'form-control net_weight required-field required-pallet'}),
                'invoice_weight': forms.NumberInput(attrs={'class': 'form-control invoice_weight required-field required-pallet'}),
                'retained_quantity': forms.NumberInput(attrs={'class': 'form-control retained_quantity required-field required-pallet'}),
                'retained_reason': forms.TextInput(attrs={'class': 'form-control retained_reason'}),
                }

    def __init__(self, *args, **kwargs):
        super(WarehouseExitPalletMForm, self).__init__(*args, **kwargs)
        for field in self.fields: 
            if (field == 'exp_date'):
                self.fields[field].widget.attrs['class'] = 'form-control exp_date datepicker'
            self.fields[field].widget.attrs['readonly'] = True
       

WarehouseExitPalletForm = inlineformset_factory(WExitConfirmation, WarehouseExitPallet
    ,extra=0, form=WarehouseExitPalletMForm, can_delete=True)


class WarehouseExitPalletMFormset(BaseInlineFormSet):
    """
    The base formset for editing Books belonging to a Publisher, and the
    BookImages belonging to those Books.
    """

    def add_fields(self, form, index):
        super(WarehouseExitPalletMFormset, self).add_fields(form, index)

        # Save the formset for a Book's Images in the nested property.
        form.nested = WarehouseExitPalletForm(
                                instance=form.instance,
                                data=form.data if form.is_bound else None,
                                files=form.files if form.is_bound else None,
                                prefix='pallete-%s-%s' % (
                                    form.prefix,
                                    WarehouseExitPalletForm.get_default_prefix()),
                                )

    def is_valid(self):
        """
        Also validate the nested formsets.
        """
        result = super(WarehouseExitPalletMFormset, self).is_valid()
        if self.is_bound:
            for idx, form in enumerate(self.forms):
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
                if form.is_valid():
                    d1 = form.save()
                    form.data._mutable = True
                    form.data["w_exit_confirmation_set-{}-id".format(idx)] = d1.id
        return result

    def save(self, commit=True):
        """
        Also save the nested formsets.
        """
        result = super(WarehouseExitPalletMFormset, self).save(commit=commit)
        for form in self.forms:

            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result

WarehouseExitPalletFormSet = inlineformset_factory(
                                WarehouseExit,
                                WExitConfirmation,
                                formset=WarehouseExitPalletMFormset,
                                form=WExitConfirmationForm,
                                extra=0,
                                can_delete=True
                            )

class WarehouseExitFormSet1(forms.ModelForm):
   class Meta:
       model = WarehouseExit
       fields= ('id', 'status')