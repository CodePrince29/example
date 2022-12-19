from django import forms
from .models import (WarehouseEntrance,
    WProductMeasurement,
    WProductVehicleInspection,
    WIncidenceProduct,
    WIncidenceImage,
    WarehouseEntranceConfirmation,
    WarehouseEntrancePallet)

from catalogs.clients.models import Client
from catalogs.carrier.models import Carrier
from catalogs.vehicle.models import Vehicle
from catalogs.product.models import Product
from catalogs.general_params.models import GeneralParams
from catalogs.warehouse.models import Warehouse,WarehouseSection,WarehouseHeightLevel,WarehouseDepthLevel,WarehouseLocation
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from concurrent import futures

class WarehouseEntranceForm(forms.ModelForm):    
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )  
    carrier = forms.ModelChoiceField(
        queryset=Carrier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    ) 
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    cargo_type = forms.CharField(widget=forms.RadioSelect(attrs={'class': 'radio-inline'},choices=WarehouseEntrance.CARGO_TYPE), initial=0 )
    CHOICES=((0,''),(1,''),(2 ,''))
    vehicle_temograph= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    temprature_cel= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    cont_flr_sta= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    fasteners= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    container_clean= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    inside_container_good= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    save_continue = forms.CharField(widget=forms.HiddenInput(), initial=0)

    def __init__(self, *args, **kwargs):
        super(WarehouseEntranceForm, self).__init__(*args, **kwargs)
        # self.fields['created_by'].required = False

    class Meta:
        model = WarehouseEntrance
        fields = '__all__'
        exclude = ('created_by',)
        widgets={
                'cargo_sender': forms.TextInput(attrs={'class': 'form-control'}),
                'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
                'temp_front': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_middle': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_back': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'cust_reference': forms.TextInput(attrs={'class': 'form-control'}),
                'seal1': forms.TextInput(attrs={'class': 'form-control'}),
                'seal2': forms.TextInput(attrs={'class': 'form-control'}),
                }
    


class WProductMeasurementForm(forms.ModelForm):
    class Meta:
        model = WProductMeasurement
        fields=('product','product_description','total_kg','price','kg_per_price','boxes','kg_per_boxes',)
        widgets = {
           'product':forms.Select(attrs={'class': 'form-control select2 w_product_measurment whm_product ', 'required': 'true'}),
           'product_description': forms.TextInput(attrs={'class': 'form-control whm_p_description p_description','readonly': 'true'}),
           'total_kg': forms.TextInput(attrs={'class': 'form-control price_calculation whm_total_kg','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 3);", 'required': 'true'}),
           'price': forms.TextInput(attrs={'class': 'form-control price_calculation whm_tprice','onkeypress': 'return isFloat(event)'}),
           'kg_per_price': forms.TextInput(attrs={'class': 'form-control price_calculation whm_kg_per_price','onkeypress': 'return isFloat(event)'}),
           'boxes': forms.TextInput(attrs={'class': 'form-control price_calculation whm_boxes','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 1);", 'required': 'true'}),
           'kg_per_boxes': forms.TextInput(attrs={'class': 'form-control price_calculation whm_kg_per_boxes','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 3);", 'required': 'true'}),
       }

    def __init__(self, *args, **kwargs):

        super(WProductMeasurementForm, self).__init__(*args, **kwargs)
        gp = GeneralParams.objects.filter(key="AllowPzEntry")
        for field in self.fields:
            self.fields[field].required = False
            if gp.exists():
                val = gp.first().value
                if (int(val) == 0):
                    if field == 'price' or field =='kg_per_price':
                        self.fields[field].widget.attrs['readonly'] = True             
                    
            
WProductMeasurementFormSet = inlineformset_factory(WarehouseEntrance, WProductMeasurement
    ,extra=1, max_num=1, form=WProductMeasurementForm,can_delete=True)



class WWIncidenceProductForm(forms.ModelForm):
    class Meta:
        model = WIncidenceProduct
        fields=('product','code','incidence','notes',)
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'product':forms.Select(attrs={'class': 'form-control product-incidence'}),
            'incidence': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),            
        }

    def __init__(self, *args, **kwargs):
        super(WWIncidenceProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:                
            self.fields[field].required = False


WWIncidenceProductFormSet = inlineformset_factory(WarehouseEntrance, WIncidenceProduct
    ,extra=1, max_num=1, form=WWIncidenceProductForm,can_delete=True)


class WWIncidenceImageForm(forms.ModelForm):
    class Meta:
        model = WIncidenceImage
        exclude = ['thumbnail']
        fields=('image',)
        


WWIncidenceImageFormset = inlineformset_factory(WarehouseEntrance, WIncidenceImage,
    extra=1, form=WWIncidenceImageForm,can_delete=True)

WWIncidenceImageEditFormset = inlineformset_factory(WarehouseEntrance, WIncidenceImage,
    extra=1,  form=WWIncidenceImageForm,can_delete=True)


class WarehouseEntrancePalletFonfirmForm(forms.ModelForm):
    print_picking = forms.CharField(widget=forms.HiddenInput(), initial=0)
    class Meta:
        model = WarehouseEntrance
        fields = ('id','print_picking','status',)

class WarehouseEntranceConfirmationForm(forms.ModelForm):
    
    class Meta:
        model = WarehouseEntranceConfirmation
        fields= ('product',
                'cost_lot',
                'exp_date',
                'gross_weight',
                'net_weight',
                'invoice_weight',
                'retained_quantity',
                'retained_reason',
                'werehouse_entrance',
                'w_product_measurement'
                )

        widgets= {
                'code': forms.TextInput(attrs={'readonly': True}),
                'gross_weight': forms.TextInput(attrs={'onkeypress': " return checkDecimal(event, this, 5, 3);",'class':'confirm_enter'}),
                'net_weight': forms.TextInput(attrs={'onkeypress': " return checkDecimal(event, this, 5, 3);",'class':'confirm_enter'}),
                }

    def __init__(self, *args, **kwargs):
        super(WarehouseEntranceConfirmationForm, self).__init__(*args, **kwargs)
        products = [(u'',u'------')]
        # products.extend([
        #     (
        #         product.get('id'), 
        #         product.get('product_description')
        #     ) for product in Product.objects.values('id', 'product_description').iterator()
        # ])


        self.fields['product'].choices = products
        for field in self.fields:  
            if field == 'exp_date':
                self.fields[field].widget.attrs['class'] = 'form-control move_next datepicker skip_validation {}'.format(field)
            elif ((field == 'invoice_weight') or (field == 'retained_quantity') or (field == 'retained_reason')):
                self.fields[field].widget.attrs['class'] = 'form-control move_next {}'.format(field)
            elif field == 'code':
                self.fields[field].widget.attrs['class'] = 'hide_field'
            elif field =='cost_lot':
                self.fields[field].widget.attrs['value'] = '0'
                self.fields[field].widget.attrs['class'] = 'form-control move_next skip_validation {}'.format(field)
            else:
                self.fields[field].widget.attrs['class'] = 'form-control move_next skip_validation {}'.format(field)


WarehouseEntranceConfirmationFormSet = inlineformset_factory(WarehouseEntrance, WarehouseEntranceConfirmation
    ,extra=0, min_num=1, form=WarehouseEntranceConfirmationForm,can_delete=True)



class WarehouseEntrancePalletMForm(forms.ModelForm):
    class Meta:
        model = WarehouseEntrancePallet
        fields=('id','palet_lot', 'boxes' , 'box_kg' ,'warehouse','rack_number','location','cost_lot','exp_date','gross_weight','net_weight','invoice_weight','retained_quantity','retained_reason','werehouse_entrance_confirmation','maniobras',)
        widgets= {
                'werehouse_entrance_confirmation': forms.TextInput(attrs={'class': 'hide'}),    
                'palet_lot': forms.TextInput(attrs={'class': 'form-control palet_lot', 'readonly': True}),
                'boxes': forms.TextInput(attrs={'class': 'form-control pallet_required_boxes boxes required-field required-pallet pallet_boxes' ,'onkeypress': " ValidateInteger(event);"}),
                'box_kg': forms.TextInput(attrs={'class': 'form-control box_kg required-field required-pallet', 'readonly': True}),
                'warehouse': forms.Select(attrs={'class': 'form-control warehouse required-field required-pallet'}),
                'rack_number': forms.Select(attrs={'class': 'form-control rack_number required-field required-pallet'}),
                'location': forms.Select(attrs={'class': 'form-control location required-field required-pallet'}),
                'cost_lot': forms.TextInput(attrs={'class': 'form-control cost_lot required-field required-pallet'}),
                'exp_date': forms.TextInput(attrs={'class': 'form-control exp_date datepicker required-field required-pallet '}),
                'gross_weight': forms.NumberInput(attrs={'readonly': "true", 'class': 'form-control gross_weight required-field required-pallet','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
                'net_weight': forms.NumberInput(attrs={'readonly': "true", 'class': 'form-control net_weight required-field required-pallet','onkeypress': " return checkDecimal(event, this, 5, 3);"}),
                'invoice_weight': forms.NumberInput(attrs={'class': 'form-control invoice_weight required-field required-pallet'}),
                'retained_quantity': forms.NumberInput(attrs={'class': 'form-control retained_quantity required-field required-pallet'}),
                'retained_reason': forms.TextInput(attrs={'class': 'form-control retained_reason'}),
                'maniobras': forms.TextInput(attrs={'class': "maniobras hide"})
                }

    def __init__(self, *args, **kwargs):
        super(WarehouseEntrancePalletMForm, self).__init__(*args, **kwargs)

        if kwargs.get('instance', None) != None and kwargs['instance'].warehouse != None:
            rack_numbers = [(u'',u'------')]
            rack_numbers.extend([
                (
                    section.get('id'), 
                    section.get('index')
                ) for section in WarehouseSection.objects.filter(row__warehouse= kwargs['instance'].warehouse).order_by('id').values('id', 'index').iterator()
            ])

            self.fields['rack_number'].choices = rack_numbers

        if kwargs.get('instance', None) != None and kwargs['instance'].rack_number != None:

            height = WarehouseHeightLevel.objects.filter(section_id = kwargs['instance'].rack_number).values_list('id')
            depth = WarehouseDepthLevel.objects.filter(height_id__in= height).values_list('warehouse_location')

            locations = [(u'',u'------')]
            locations.extend([
                (
                    loc.get('id'), 
                    loc.get('location_number')
                ) for loc in WarehouseLocation.objects.filter(id__in= depth).order_by('id').values('id', 'location_number').iterator()
            ])

            self.fields['location'].choices = locations

        for field in self.fields: 
            if (field == 'exp_date'):
                self.fields[field].widget.attrs['class'] = 'form-control exp_date datepicker required-field'
                # self.fields[field].widget.attrs['required'] = True

       

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
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result


    # def save(self, commit=True):
    #     """
    #     Also save the nested formsets.
    #     """
    #     result = super(WarehouseEntrancePalletMFormset, self).save(commit=commit)
    #     ex = futures.ThreadPoolExecutor(max_workers=5)
    #     wait_for = [ex.submit(self.form_nested_save, form) for form in self.forms]

    #     for f in futures.as_completed(wait_for):
    #         print('main: result: {}'.format(f.result()))

    #     return result


    # def form_nested_save(self, form):
    #     if hasattr(form, 'nested'):
    #         if not self._should_delete_form(form):
    #             if form.nested.is_valid():
    #                 form.nested.save(commit=True)
    #                 return True
    #     return False

    def save(self, commit=True):
        for form in self.forms:
            form.save(commit=commit)
        result = super(WarehouseEntrancePalletMFormset, self).save(commit=commit)

        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result
        
# from nested_formset import nestedformset_factory
# WarehouseEntrancePalletFormSet = nestedformset_factory(
#             WarehouseEntrance,
#             WarehouseEntranceConfirmation,
#             nested_formset=WarehouseEntrancePalletForm,
#             form=WarehouseEntranceConfirmationForm,
#             exclude=('created_at', 'updated_at',),
#             extra=0,
#             can_delete=True
#         )
WarehouseEntrancePalletFormSet = inlineformset_factory(
                                WarehouseEntrance,
                                WarehouseEntranceConfirmation,
                                formset=WarehouseEntrancePalletMFormset,
                                form=WarehouseEntranceConfirmationForm,
                                extra=0,
                                can_delete=True
                            )

class WarehouseEntranceEditForm(forms.ModelForm):    
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )  
    carrier = forms.ModelChoiceField(
        queryset=Carrier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    ) 
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    cargo_type = forms.CharField(widget=forms.RadioSelect(attrs={'class': 'radio-inline'},choices=WarehouseEntrance.CARGO_TYPE), initial=0 )
    # CHOICES=((0,''),(1,''),(2 ,''))
    # vehicle_temograph= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    # temprature_cel= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    # cont_flr_sta= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    # fasteners= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    # container_clean= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    # inside_container_good= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    save_continue = forms.CharField(widget=forms.HiddenInput(), initial=0)

    def __init__(self, *args, **kwargs):
        super(WarehouseEntranceEditForm, self).__init__(*args, **kwargs)
        # self.fields['created_by'].required = False

    class Meta:
        model = WarehouseEntrance
        fields = ('id','customer','vehicle', 'cargo_type', 'carrier', 'status','boxes','total_kg', 'cargo_sender', 'cust_reference', 'entrance_date', 'entrance_hour', 'license_plate',)

        widgets={
                'cargo_sender': forms.TextInput(attrs={'class': 'form-control'}),
                'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
                'temp_front': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_middle': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_back': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'cust_reference': forms.TextInput(attrs={'class': 'form-control'}),
                }
    


class WProductEditMeasurementForm(forms.ModelForm):
    class Meta:
        model = WProductMeasurement
        fields=('id', 'product','product_description','boxes','total_kg',)
        widgets = {
           'product':forms.Select(attrs={'class': 'form-control select2 w_product_measurment whm_product ', 'required': 'true'}),
           'product_description': forms.TextInput(attrs={'class': 'form-control whm_p_description p_description','readonly': 'true'}),
           'boxes': forms.TextInput(attrs={'class': 'form-control price_calculation whm_boxes w_prod_boxes number_boxes only_int_value','onkeypress': " return ValidateInteger(event);", 'required': 'true'}),
           'total_kg': forms.TextInput(attrs={'class': 'form-control price_calculation whm_total_kg only_float_value','onkeypress': 'return isFloat(event)','onkeypress': " return checkDecimal(event, this, 5, 3);", 'required': 'true'}),
       }

    def __init__(self, *args, **kwargs):

        super(WProductEditMeasurementForm, self).__init__(*args, **kwargs)
        gp = GeneralParams.objects.filter(key="AllowPzEntry")
        for field in self.fields:
            self.fields[field].required = False
            if gp.exists():
                val = gp.first().value
                if (int(val) == 0):
                    if field == 'price' or field =='kg_per_price':
                        self.fields[field].widget.attrs['readonly'] = True             
                    
            
WProductMeasurementEditFormSet = inlineformset_factory(WarehouseEntrance, WProductMeasurement
    ,extra=1, max_num=1, form=WProductEditMeasurementForm,can_delete=True)


class NewWarehouseEntranceConfirmationForm(forms.ModelForm):    
    customer = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'disabled': "disabled"})
    )  
    carrier = forms.ModelChoiceField(
        queryset=Carrier.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    ) 
    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    cargo_type = forms.CharField(widget=forms.RadioSelect(attrs={'class': 'radio-inline'},choices=WarehouseEntrance.CARGO_TYPE), initial=0 )
    CHOICES=((0,''),(1,''),(2 ,''))
    vehicle_temograph= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    temprature_cel= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    cont_flr_sta= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    fasteners= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    container_clean= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)
    inside_container_good= forms.CharField(widget=forms.RadioSelect(choices=CHOICES), initial=0)

    def __init__(self, *args, **kwargs):
        super(NewWarehouseEntranceConfirmationForm, self).__init__(*args, **kwargs)
        # self.fields['created_by'].required = False

    class Meta:
        model = WarehouseEntrance
        fields = '__all__'
        
        exclude = ('created_by', 'sent_to_maniobras_by', 'confirmed_by',)
        widgets={
                'cargo_sender': forms.TextInput(attrs={'class': 'form-control'}),
                'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
                'temp_front': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_middle': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'temp_back': forms.NumberInput(attrs={'class': 'form-control', 'step': "0.01"}),
                'cust_reference': forms.TextInput(attrs={'class': 'form-control'}),
                'seal1': forms.TextInput(attrs={'class': 'form-control'}),
                'seal2': forms.TextInput(attrs={'class': 'form-control'}),
                }
    
class ConfirmationEditMeasurementForm(forms.ModelForm):
    class Meta:
        model = WProductMeasurement
        fields=('id', 'product','product_description','boxes','total_kg',)
        widgets = {
           'product':forms.Select(attrs={'class': 'form-control readonly_true ', 'required': 'false'}),
           'product_description': forms.TextInput(attrs={'class': 'form-control whm_p_description p_description','readonly': 'true'}),
           'boxes': forms.TextInput(attrs={'class': 'form-control','readonly': 'true','onkeypress': " ValidateInteger(event);"}),
           'total_kg': forms.TextInput(attrs={'class': 'form-control','readonly': 'true'}),
          
       }

    def __init__(self, *args, **kwargs):

        super(ConfirmationEditMeasurementForm, self).__init__(*args, **kwargs)


        gp = GeneralParams.objects.filter(key="AllowPzEntry")


        for field in self.fields:
            self.fields[field].required = False
            if gp.exists():
                val = gp.first().value
                if (int(val) == 0):
                    if field == 'price' or field =='kg_per_price':
                        self.fields[field].widget.attrs['readonly'] = True
            
            
ConfirmationPMeasurementEditFormSet = inlineformset_factory(WarehouseEntrance, WProductMeasurement, form=ConfirmationEditMeasurementForm,can_delete=False,max_num=1)

