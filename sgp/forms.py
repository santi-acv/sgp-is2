"""
Los formularios son un método de intercambio de información entre la aplicación
y el usuario. Cada formulario corresponde a un modelo, por lo que un formulario
en blanco permite instanciarlo mientras que uno ya ligado a una instancia
permite modificarla.

Para todos los formularios, los argumentos de los constructores son los mismos
que para su clase base.
"""

from django import forms
from django.forms import ModelForm
from guardian.shortcuts import assign_perm, remove_perm, get_perms_for_model

from .models import User, Proyecto, Role


class UserForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de administración, donde se pueden modificar
    propiedades o permisos.

    Posee campos correspondientes a los atributos de nombre, apellido, y correo
    electrónico. Además, posee tres campos adicionales para los permisos de
    creación de proyecto, administración de usuarios, y auditación del sistema.

    **Fecha:** 24/08/21

    **Artefacto:** módulo de seguridad

    |
    """
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
    """
    Corresponde al modelo Proyecto. Este formulario se muestra en las páginas
    de creación y de edición de proyectos.

    Posee campos correspondientes a los atributos de nombre, descripción, fecha
    de inicio, fecha de fin, y duración predeterminada de los sprints.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_sprint')


class RoleForm(ModelForm):
    """
    Corresponde al modelo Role. Se muestra un formulario por cada rol dentro
    de la página de administración de roles, donde se pueden crear nuevos
    roles, modificar sus permisos, o eliminarlos.

    Posee un campo correspondiente al nombre. Además, posee un campo adicional
    para cada permiso posible dentro de un proyecto. Estos son cuatro:
    administración de equipo, gestión de proyecto, modificación de la pila de
    producto, y desarrollo.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
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
