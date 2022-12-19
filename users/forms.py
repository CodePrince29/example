from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(), required=True, max_length=100)


class UserProfileForm(forms.ModelForm):
    
    role = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
    )
   
    password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'})
    )
    password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'})
    )

    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

        widgets={
                'username': forms.TextInput(attrs={'class': 'form-control','required': True}),
                'first_name': forms.TextInput(attrs={'class': 'form-control','required': True}),
                'last_name': forms.TextInput(attrs={'class': 'form-control','required': True}),
                'email': forms.EmailInput(attrs={'class': 'form-control','id': 'user_email','required': True}),
                }
    def clean(self):
        """
        Overridden to verify that the values entered into the password fields match
        :return:
        """
        cleaned_data = super(UserProfileForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2'] and self.cleaned_data['password1'] != "":
                raise forms.ValidationError(_("Passwords don't match. Please enter both fields again."))
        return self.cleaned_data

    def save(self, commit=True):
        """
        Saves user object and updates password, if given
        :param commit: defaults to True
        :return:
        """
        user = super(UserProfileForm, self).save(commit=False)
        if self.cleaned_data['password1'] != "":
            user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


# Admin panel form
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    class Meta:
        model = UserProfile
        fields = '__all__'

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(
        label=_('Password'),
        help_text=("Raw passwords are not stored, so there is no way to see "
                   "this user's password, but you can change the password "
                   "using <a href=\"../password/\">this form</a>.")
    )

    class Meta:
        model = UserProfile
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def clean(self):
        username = self.cleaned_data.get('username')
        if username == manager.username:
            raise forms.ValidationError("No puedes tu propio manager.")
        return self.cleaned_data
