
from django import forms
from django.forms import ModelForm
from guardian.shortcuts import assign_perm, remove_perm, get_group_perms

from .models import User, Proyecto, Role


class UserForm(ModelForm):
    crear_proyecto = forms.BooleanField(required=False)
    administrar = forms.BooleanField(required=False)
    auditar = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for permiso in self.Meta.fields:
            self.fields[permiso].initial = self.instance.has_perm('sgp.' + permiso)

    def save(self, commit=True):
        for permiso in ['crear_proyecto', 'administrar', 'auditar']:
            if self.cleaned_data[permiso]:
                assign_perm('sgp.' + permiso, self.instance)
            else:
                remove_perm('sgp.' + permiso, self.instance)
        super(UserForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'crear_proyecto', 'administrar', 'auditar']


class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ('nombre_proyecto', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_sprint')


class RoleForm(ModelForm):
    administrar_equipo = forms.BooleanField(required=False)
    gestionar_proyecto = forms.BooleanField(required=False)
    pila_producto = forms.BooleanField(required=False)
    desarrollo = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        for permiso in self.Meta.fields:
            self.fields[permiso].initial = permiso in get_group_perms(self.instance, self.instance.proyecto)

    def save(self, commit=True):
        for permiso in ['administrar_equipo', 'gestionar_proyecto', 'pila_producto', 'desarrollo']:
            if self.cleaned_data[permiso]:
                assign_perm(permiso, self.instance, self.instance.proyecto)
            else:
                remove_perm(permiso, self.instance, self.instance.proyecto)
        super(RoleForm, self).save(commit)

    class Meta:
        model = Role
        fields = ['name', 'administrar_equipo', 'gestionar_proyecto', 'pila_producto', 'desarrollo']