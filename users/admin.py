from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auditlog.registry import auditlog
from .models import UserProfile
from .forms import UserChangeForm, UserCreationForm

class UsersAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('username', 'email', 'role', 'date_joined','last_login',)

    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password', 'role', 'is_active', 'is_staff', 'is_superuser',)}
         ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password', 'role', 'is_active', 'is_staff', 'is_superuser', )}
         ),
    )

    search_fields = ('username',)
    readonly_fields =('last_login', 'date_joined',)
    exclude = ('groups',)


admin.site.register(UserProfile, UsersAdmin)
auditlog.register(UserProfile)
