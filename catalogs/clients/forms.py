from django import forms
from .models import Client
from django.utils.translation import ugettext_lazy as _
from catalogs.price_list.models import PriceList
from users.models import UserProfile
from django.core.exceptions import ValidationError


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ResetPasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        if self.cleaned_data['password'] != "" and self.cleaned_data['current_password'] != "":
            if self.cleaned_data['current_password'] and not self.user.check_password(self.cleaned_data['current_password']):
                raise ValidationError('Por favor ingrese su contrasena actual valida.')

            if self.cleaned_data['current_password'] and not (self.cleaned_data['password'] or self.cleaned_data['confirm_password']):
                raise ValidationError('Por favor ingrese una nueva contrasena y una confirmacion para actualizar.')

            return self.cleaned_data['current_password']
        else:
            raise ValidationError('Por favor ingrese los detalles de su contrasena')



    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')

        if password1 != password2:
            raise forms.ValidationError("Su nueva contrasena y la contrasena de confirmacion no coinciden.")

        return self.cleaned_data.get('confirm_password')

class ClientForm(forms.ModelForm):
    price_list = forms.ModelChoiceField(
        queryset=PriceList.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    barcoderead = forms.BooleanField( required=False )

    class Meta:
        model = Client
        fields = ('name', 'client_code', 'contact_name', 'contact_phone', 'email', 'username', 'password', 'barcoderead')
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'client_code': forms.TextInput(attrs={'class': 'form-control'}),
        'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
        'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.TextInput(attrs={'class': 'form-control'}),
        'username': forms.TextInput(attrs={'class': 'form-control'}),
        'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        print(self.cleaned_data)
        exists_username = UserProfile.objects.filter(username=self.cleaned_data['username'])
        if exists_username.exists():
            raise forms.ValidationError(_("User name already exists."))
        import ast
        email_list = ast.literal_eval(self.cleaned_data['email'])
        if len(email_list) == 0:
            raise forms.ValidationError(_("Email address should not blank."))
        
        return self.cleaned_data

class ClientUpdateForm(forms.ModelForm):
    price_list = forms.ModelChoiceField(
        queryset=PriceList.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    barcoderead = forms.BooleanField(required=False )


    class Meta:
        model = Client
        fields = ('name', 'client_code', 'contact_name', 'contact_phone', 'email', 'username', 'password', 'barcoderead')
        widgets = {
        'name': forms.TextInput(attrs={'class': 'form-control'}),
        'client_code': forms.TextInput(attrs={'class': 'form-control'}),
        'contact_name': forms.TextInput(attrs={'class': 'form-control'}),
        'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.TextInput(attrs={'class': 'form-control'}),
        'username': forms.TextInput(attrs={'class': 'form-control'}),
        'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }