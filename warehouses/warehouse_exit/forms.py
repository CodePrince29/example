from django import forms
from .models import WarehouseExit,WarehouseExitPallet,WExitProductMeasurement,WExitProductVehicleInspection, WExitConfirmation

from catalogs.clients.models import Client
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.product.models import Product
from catalogs.general_params.models import GeneralParams
from django.forms import inlineformset_factory
from catalogs.warehouse.models import Warehouse,WarehouseInventory
from catalogs.consignee.models import Consignee
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from concurrent import futures

class WarehouseExitForm(forms.ModelForm):

    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'required': True})
    )  
    carrier = forms.ModelChoiceField(
        queryset=Carrier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'required': True})
    ) 
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'required': True})
    )

    consignee = forms.ModelChoiceField(
        queryset=Consignee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': True})
    )

    CHOICES=((0,''),(1,''),(2 ,''))
    vehicle_temograph= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    temprature_cel= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    cont_flr_sta= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    fasteners= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    container_clean= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    inside_container_good= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    save_continue = forms.CharField(widget=forms.HiddenInput(), initial=0)
    print_picking = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = WarehouseExit
        fields = '__all__'
        exclude = ('created_by',)
        widgets = {
                'cargo_sender': forms.TextInput(attrs={'class': 'form-control'}),
                'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
                'temp_front': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_middle': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_back': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'cust_reference': forms.TextInput(attrs={'class': 'form-control'}),
                'seal1': forms.TextInput(attrs={'class': 'form-control'}),
                'seal2': forms.TextInput(attrs={'class': 'form-control'}),
                }

    def __init__(self, *args, **kwargs):
        super(WarehouseExitForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
            if field == 'exit_date':
                self.fields[field].widget.attrs['class'] = 'form-control datepicker'
    

class WarehouseExitPalletFonfirmForm(forms.ModelForm):
    print_picking = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    process_print_picking = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = WarehouseExit
        fields = ('id','print_picking','status','process_print_picking',)

class WExitProductMeasurementForm(forms.ModelForm):
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2 w_product_measurment','required': True})
    )

    class Meta:
        model = WExitProductMeasurement
        fields=('product','product_description','total_kg','price','kg_per_price','boxes','kg_per_boxes',)
        widgets = {
           'product':forms.Select(attrs={'class': 'form-control whm_product'}),
           'product_description': forms.TextInput(attrs={'class': 'form-control whm_p_description p_description','readonly': 'true'}),
           'total_kg': forms.TextInput(attrs={'required': 'true', 'class': 'form-control price_calculation whm_total_kg','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
           'price': forms.TextInput(attrs={'class': 'form-control price_calculation whm_tprice','onkeypress': 'return isFloat(event)'}),
           'kg_per_price': forms.TextInput(attrs={'class': 'form-control price_calculation whm_kg_per_price','onkeypress': 'return isFloat(event)'}),
           'boxes': forms.TextInput(attrs={'required': 'true', 'class': 'form-control price_calculation whm_boxes','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 1);"}),
           'kg_per_boxes': forms.TextInput(attrs={'required': 'true', 'class': 'form-control price_calculation whm_kg_per_boxes','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
       }

    def __init__(self, *args, **kwargs):
        super(WExitProductMeasurementForm, self).__init__(*args, **kwargs)
        gp = GeneralParams.objects.filter(key="AllowPzEntry")
        for field in self.fields:
            self.fields[field].required = False
            if gp.exists():
                val = gp.first().value
                if (int(val) == 0):
                    if field == 'price' or field =='kg_per_price':
                        self.fields[field].widget.attrs['readonly'] = True 
            

WExitProductMeasurementFormSet = inlineformset_factory(WarehouseExit, WExitProductMeasurement
    ,extra=1, max_num=1, form=WExitProductMeasurementForm,can_delete=True)



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
                'werehouse_exit',
                'exit_product_measurement'
                )
        widgets= {
                'gross_weight': forms.TextInput(attrs={'onkeypress': " return checkDecimal(event, this, 5, 3);"}),
                'net_weight': forms.TextInput(attrs={'onkeypress': " return checkDecimal(event, this, 5, 3);"}),
                }

    def __init__(self, *args, **kwargs):


        super(WExitConfirmationForm, self).__init__(*args, **kwargs)
        products = [(u'',u'------')] 
        products.extend([
            (
                product.get('id'), 
                product.get('product_description')
            ) for product in Product.objects.values('id', 'product_description').iterator()
        ])
        # if self.instance.id != None and self.instance.warehouse.all().exists():
        #     self.fields['warehouse'].initial = self.instance.warehouse.all()
        #     self.fields['warehouse'].queryset = self.instance.warehouse.all()

        self.fields['product'].choices = products
        

        for field in self.fields:  
            if field == 'exp_date':
                self.fields[field].widget.attrs['class'] = 'form-control move_next warehouse_exp_date datepicker skip_validation'
                self.fields[field].widget.attrs['readonly'] = True
            elif field == 'cost_lot':
                self.fields[field].widget.attrs['class'] = 'form-control move_next warehouse_cost_lot skip_validation'
            elif field == 'retained_quantity':
                self.fields[field].widget.attrs['class'] = 'form-control move_next warehouse_retained_quantity'
            elif field == 'invoice_weight':
                self.fields[field].widget.attrs['class'] = 'form-control move_next warehouse_invoice_weight'
            elif field == 'retained_reason':
                self.fields[field].widget.attrs['class'] = 'form-control move_next warehouse_retained_reason'
            elif field == 'auto_pick_data':
                self.fields[field].required = False
                self.fields[field].widget.attrs['class'] = 'form-control  hide'            
            elif field in ['removed_kgs']:
                self.fields[field].widget.attrs['class'] = 'form-control'
                self.fields[field].widget.attrs['readonly'] = True
            elif field in ['removed_boxes']:
                self.fields[field].widget.attrs['class'] = 'form-control'
                self.fields[field].widget.attrs['readonly'] = True
            elif field in ['gross_weight']:
                self.fields[field].widget.attrs['class'] = 'form-control move_next skip_validation peso_bruto'
            elif field in ['net_weight']:
                self.fields[field].widget.attrs['class'] = 'form-control move_next skip_validation peso_neto'
            elif field in ['product']:
                self.fields[field].widget.attrs['class'] = 'form-control exit_product skip_validation'
            else:
                self.fields[field].widget.attrs['class'] = 'form-control move_next skip_validation'



WExitConfirmationFormSet = inlineformset_factory(WarehouseExit, WExitConfirmation
    ,extra=0, min_num=1, form=WExitConfirmationForm,can_delete=True)


class WarehouseExitPalletMForm(forms.ModelForm):
    class Meta:
        model = WarehouseExitPallet
        fields=('id','palet_lot', 'boxes', 'box_kg','warehouse','rack_number','location','cost_lot','exp_date','gross_weight','net_weight','invoice_weight','retained_quantity','retained_reason','inventory','werehouse_exit_confirmation',)
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
                'exp_date': forms.TextInput(attrs={'class': 'form-control exp_date required-field required-pallet','readonly': True}),
                'gross_weight': forms.NumberInput(attrs={'class': 'form-control gross_weight required-field required-pallet','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
                'net_weight': forms.NumberInput(attrs={'class': 'form-control net_weight required-field required-pallet','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
                'invoice_weight': forms.NumberInput(attrs={'class': 'form-control invoice_weight required-field required-pallet'}),
                'retained_quantity': forms.NumberInput(attrs={'class': 'form-control retained_quantity required-field required-pallet'}),
                'retained_reason': forms.TextInput(attrs={'class': 'form-control retained_reason'}),
                }

    def __init__(self, *args, **kwargs):
        super(WarehouseExitPalletMForm, self).__init__(*args, **kwargs)
        for field in self.fields: 
            if (field == 'exp_date'):
                self.fields[field].widget.attrs['class'] = 'form-control exp_date'

       

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
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        # for form in self.forms:
            # form.save(commit=commit)
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


#-----------------new exit process started as per document---------------------

class NewWarehouseExitForm(forms.ModelForm):
    #Y
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2', 'required': True})
    )

    consignee = forms.ModelChoiceField(
        queryset=Consignee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'required': True})
    )

    class Meta:
        model = WarehouseExit
        fields = '__all__'
        fields = ('id','customer','exit_date', 'exit_hour', 'cargo_sender', 'status','boxes','total_kg', 'cust_reference', 'consignee',)
        widgets = {
                'cargo_sender': forms.TextInput(attrs={'class': 'form-control'}),
                'cust_reference': forms.TextInput(attrs={'class': 'form-control'}),
                }

    def __init__(self, *args, **kwargs):
        super(NewWarehouseExitForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'exit_date':
                self.fields[field].widget.attrs['class'] = 'form-control datepicker'
            elif field in ['consignee', 'cargo_sender', 'cust_reference']:
                self.fields[field].widget.attrs['required'] = 'True'


class NewWExitProductMeasurementForm(forms.ModelForm):
    
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2 w_product_measurment','required': True})
    )

    class Meta:
        model = WExitProductMeasurement
        fields=('product','product_description','exp_date', 'cost_lot', 'palet_lot', 'werehouse_entrance_id','boxes' ,'total_kg' )
        widgets = {
           'product':forms.Select(attrs={'class': 'form-control whm_product'}),
           'product_description': forms.TextInput(attrs={'class': 'form-control whm_p_description p_description','readonly': 'true'}),
           'exp_date': forms.TextInput(attrs={'class': 'form-control exp_date'}),
           'cost_lot': forms.TextInput(attrs={'class': 'form-control cost_lot'}),
           'palet_lot': forms.TextInput(attrs={'class': 'form-control palet_lot'}),
           'werehouse_entrance_id': forms.TextInput(attrs={'class': 'form-control werehouse_entrance'}),
           'boxes': forms.TextInput(attrs={'required': 'true', 'class': 'form-control price_calculation whm_boxes only_int_value','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 1);"}),
           'total_kg': forms.TextInput(attrs={'required': 'true', 'class': 'form-control price_calculation whm_total_kg only_float_value','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
       }

    def __init__(self, *args, **kwargs):
        super(NewWExitProductMeasurementForm, self).__init__(*args, **kwargs)

NewWExitProductMeasurementFormSet = inlineformset_factory(WarehouseExit, WExitProductMeasurement
    ,extra=1, max_num=1, form=NewWExitProductMeasurementForm,can_delete=True)


class ExitConfirmEditMeasurementForm(forms.ModelForm):
    class Meta:
        model = WExitProductMeasurement
        fields=('id', 'product','product_description','boxes','total_kg',)
        widgets = {
           'product':forms.Select(attrs={'class': 'form-control readonly_true ', 'required': 'false'}),
           'product_description': forms.TextInput(attrs={'class': 'form-control whm_p_description p_description','readonly': 'true'}),
           'boxes': forms.TextInput(attrs={'class': 'form-control','readonly': 'true','onkeypress': " ValidateInteger(event);"}),
           'total_kg': forms.TextInput(attrs={'class': 'form-control','readonly': 'true'}),
          
       }

    def __init__(self, *args, **kwargs):

        super(ExitConfirmEditMeasurementForm, self).__init__(*args, **kwargs)


        gp = GeneralParams.objects.filter(key="AllowPzEntry")


        for field in self.fields:
            self.fields[field].required = False
            if gp.exists():
                val = gp.first().value
                if (int(val) == 0):
                    if field == 'price' or field =='kg_per_price':
                        self.fields[field].widget.attrs['readonly'] = True
            
            
ConfirmationMeasurementEditFormSet = inlineformset_factory(WarehouseExit, WExitProductMeasurement, form=ExitConfirmEditMeasurementForm,can_delete=False,max_num=1)


class WarehouseSingleExitPalletMForm(forms.ModelForm):
    class Meta:
        model = WarehouseExitPallet
        fields=('id','palet_lot', 'boxes', 'box_kg','warehouse','rack_number','location','cost_lot','exp_date','gross_weight','net_weight','invoice_weight','retained_quantity','retained_reason','inventory','werehouse_exit_confirmation',)

    def __init__(self, *args, **kwargs):
        super(WarehouseSingleExitPalletMForm, self).__init__(*args, **kwargs)
        for field in self.fields: 
            if (field == 'exp_date'):
                self.fields[field].widget.attrs['class'] = 'form-control exp_date'
