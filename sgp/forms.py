
from django import forms
from django.forms import ModelForm
from guardian.shortcuts import assign_perm, remove_perm, get_perms_for_model

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
        fields = ('nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_sprint')


class RoleForm(ModelForm):
    administrar_equipo = forms.BooleanField(required=False)
    gestionar_proyecto = forms.BooleanField(required=False)
    pila_producto = forms.BooleanField(required=False)
    desarrollo = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
            for perm in permisos:
                self.fields[perm.codename].initial = self.instance.permisos.filter(id=perm.id).exists()

    def save(self, commit=True):
        permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
        if self.instance.pk:
            for perm in permisos:
                if self.cleaned_data[perm.codename]:
                    self.instance.asignar_permiso(perm)
                else:
                    self.instance.quitar_permiso(perm)
            super(RoleForm, self).save(commit)
        else:
            super(RoleForm, self).save(commit)
            for perm in permisos:
                if self.cleaned_data[perm.codename]:
                    self.instance.permisos.add(perm)

    class Meta:
        model = Role
        fields = ['nombre', 'administrar_equipo', 'gestionar_proyecto', 'pila_producto', 'desarrollo']
