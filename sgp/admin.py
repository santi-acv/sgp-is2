from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .models import Proyecto


class UserCreationForm(forms.ModelForm):
    """Permite crear usuarios nuevos. Incluye todos los campos requeridos.\n
    Fecha: 20/08/2021\n
    Artefacto: Página de administración"""

    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Permite actualizar usuarios. Incluye todos los campos requeridos.\n
    Fecha: 20/08/2021\n
    Artefacto: Página de administración"""

    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido', 'is_active', 'is_staff')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'nombre', 'apellido', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('nombre', 'apellido')}),
        ('Permissions', {'fields': ('is_staff',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido'),
        }),
    )
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email', 'nombre', 'apellido')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Proyecto)