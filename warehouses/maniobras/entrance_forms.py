from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from catalogs.warehouse.models import Warehouse,WarehouseSection,WarehouseHeightLevel,WarehouseDepthLevel,WarehouseLocation
from warehouses.warehouse_entrance.models import *
from warehouses.warehouse_exit.models import *


class WarehouseEntranceConfirmationForm(forms.ModelForm):
    
    class Meta:
        model = WarehouseEntranceConfirmation
        fields= ('product', 'cost_lot', 'exp_date', 'gross_weight', 'net_weight', 'invoice_weight', 'retained_quantity', 'retained_reason',)

    def __init__(self, *args, **kwargs):
        super(WarehouseEntranceConfirmationForm, self).__init__(*args, **kwargs)
        products = [(u'',u'------')]
        products.extend([
            (
                c.pk, 
                c.product_description
            ) for c in Product.objects.all()
        ])


        self.fields['product'].choices = products
        for field in self.fields:  
            if field == 'exp_date':
                self.fields[field].widget.attrs['class'] = 'form-control datepicker skip_validation {}'.format(field)
            elif ((field == 'invoice_weight') or (field == 'retained_quantity') or (field == 'retained_reason')):
                self.fields[field].widget.attrs['class'] = 'form-control {}'.format(field)
            
            elif field =='cost_lot':
                self.fields[field].widget.attrs['value'] = '0'
                self.fields[field].widget.attrs['class'] = 'form-control skip_validation {}'.format(field)
            else:
                self.fields[field].widget.attrs['class'] = 'form-control skip_validation {}'.format(field)
            self.fields[field].widget.attrs['readonly'] = True

WarehouseEntranceConfirmationFormSet = inlineformset_factory(WarehouseEntrance, WarehouseEntranceConfirmation
    ,extra=0, min_num=1, form=WarehouseEntranceConfirmationForm,can_delete=True)


class WarehouseEntrancePalletMForm(forms.ModelForm):
    class Meta:
        model = WarehouseEntrancePallet
        fields=('id','palet_lot', 'boxes' , 'box_kg' ,'warehouse','rack_number','location','cost_lot','exp_date','gross_weight','net_weight','invoice_weight','retained_quantity','retained_reason','werehouse_entrance_confirmation', 'confirmed',)
        widgets= {
                'werehouse_entrance_confirmation': forms.TextInput(attrs={'class': 'hide'}),    
                'palet_lot': forms.TextInput(attrs={'class': 'form-control palet_lot', 'readonly': True}),
                'boxes': forms.TextInput(attrs={'class': 'form-control boxes required-field required-pallet', 'readonly': True}),
                'box_kg': forms.TextInput(attrs={'class': 'form-control box_kg required-field required-pallet', 'readonly': True}),
                'warehouse': forms.Select(attrs={'class': 'form-control warehouse required-field required-pallet'}),
                'rack_number': forms.Select(attrs={'class': 'form-control rack_number required-field required-pallet'}),
                'location': forms.Select(attrs={'class': 'form-control location required-field required-pallet'}),
                'cost_lot': forms.TextInput(attrs={'class': 'form-control cost_lot required-field required-pallet'}),
                'exp_date': forms.TextInput(attrs={'class': 'form-control exp_date datepicker required-field required-pallet'}),
                'gross_weight': forms.NumberInput(attrs={'class': 'form-control gross_weight required-field required-pallet'}),
                'net_weight': forms.NumberInput(attrs={'class': 'form-control net_weight required-field required-pallet'}),
                'invoice_weight': forms.NumberInput(attrs={'class': 'form-control invoice_weight required-field required-pallet'}),
                'retained_quantity': forms.NumberInput(attrs={'class': 'form-control retained_quantity required-field required-pallet'}),
                'retained_reason': forms.TextInput(attrs={'class': 'form-control retained_reason'}),
                }

    def __init__(self, *args, **kwargs):
        super(WarehouseEntrancePalletMForm, self).__init__(*args, **kwargs)
        

        for field in self.fields: 
            if (field == 'exp_date'):
                self.fields[field].widget.attrs['class'] = 'form-control exp_date datepicker'

            self.fields[field].widget.attrs['readonly'] = True

WarehouseEntrancePalletForm = inlineformset_factory(WarehouseEntranceConfirmation, WarehouseEntrancePallet
    ,extra=0, form=WarehouseEntrancePalletMForm, can_delete=True)


class WarehouseEntrancePalletMFormset(BaseInlineFormSet):
    """
    The base formset for editing Books belonging to a Publisher, and the
    BookImages belonging to those Books.
    """

    def add_fields(self, form, index):
        super(WarehouseEntrancePalletMFormset, self).add_fields(form, index)

        # Save the formset for a Book's Images in the nested property.
        form.nested = WarehouseEntrancePalletForm(
                                instance=form.instance,
                                data=form.data if form.is_bound else None,
                                files=form.files if form.is_bound else None,
                                prefix='pallete-%s-%s' % (
                                    form.prefix,
                                    WarehouseEntrancePalletForm.get_default_prefix()),
                                )

    def is_valid(self):
        """
        Also validate the nested formsets.
        """
        result = super(WarehouseEntrancePalletMFormset, self).is_valid()
        if self.is_bound:
            for idx, form in enumerate(self.forms):
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
                if form.is_valid():
                    d1 = form.save()
                    form.data._mutable = True
                    form.data["warehouseentranceconfirmation_set-{}-id".format(idx)] = d1.id
        return result

    def save(self, commit=True):
        """
        Also save the nested formsets.
        """
        result = super(WarehouseEntrancePalletMFormset, self).save(commit=commit)
        for form in self.forms:

            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result

WarehouseEntrancePalletFormSet = inlineformset_factory(
                                WarehouseEntrance,
                                WarehouseEntranceConfirmation,
                                formset=WarehouseEntrancePalletMFormset,
                                form=WarehouseEntranceConfirmationForm,
                                extra=0,
                                can_delete=True
                            )


class WarehouseEntrance1FormSet(forms.ModelForm):
   class Meta:
       model = WarehouseEntrance
       fields= ('id', 'status')