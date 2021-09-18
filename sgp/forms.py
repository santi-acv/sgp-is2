"""
Los formularios son un método de intercambio de información entre la aplicación
y el usuario. Cada formulario corresponde a un modelo, por lo que un formulario
en blanco permite instanciarlo mientras que uno ya ligado a una instancia
permite modificarla.

Para todos los formularios, los argumentos de los constructores son los mismos
que para su clase base.
"""

import datetime

from django import forms
from django.forms import ModelForm
from django.utils import timezone
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
    email = forms.CharField(disabled=True)
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

    **Fecha:** 06/09/21

    **Artefacto:** módulo de proyecto
    """
    fecha_inicio = forms.DateField(label="Fecha de inicio",
                                   error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    fecha_fin = forms.DateField(label="Fecha de fin",
                                error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    duracion_sprint = forms.IntegerField(label="Duración de los sprints (en días)", min_value=0)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Valida las fechas y la duración predeterminada del sprint.

        Para que el formulario sea válido, las fechas no pueden haber ocurrido
        en el pasado y la duración del sprint debe ser positiva. Además, debe
        haber suficiente tiempo entre la fecha de inicio la fecha de fin para
        realizar al menos un sprint.

        |
        """
        cleaned_data = super(ModelForm, self).clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        duracion_sprint = cleaned_data.get('duracion_sprint')

        if fecha_inicio and fecha_inicio < timezone.localdate():
            self.add_error('fecha_inicio', 'La fecha de inicio no puede ser en el pasado.')
            fecha_inicio = None
            if fecha_fin and fecha_fin < timezone.localdate():
                self.add_error('fecha_fin', 'La fecha de fin no puede ser en el pasado.')
        elif fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', 'La fecha de fin debe ser después de la fecha de inicio.')
            fecha_fin = None

        if duracion_sprint and duracion_sprint < 0:
            self.add_error('duracion_sprint', 'La duración de los sprints debe ser positiva.')
        elif fecha_inicio and fecha_fin and fecha_inicio+datetime.timedelta(days=duracion_sprint) > fecha_fin:
            self.add_error('duracion_sprint', 'El proyecto debe tener tiempo para al menos un sprint.')

        return cleaned_data

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

    def __init__(self, *args, rol_actual, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
            for perm in permisos:
                self.fields[perm.codename].initial = self.instance.permisos.filter(id=perm.id).exists()
            self.rol_actual = rol_actual
            if self.instance == rol_actual:
                self.fields['administrar_equipo'].disabled = True

    def save(self, commit=True):
        permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
        if self.instance.pk:
            print(self.instance, '==', self.rol_actual)
            if self.instance == self.rol_actual:
                self.cleaned_data['administrar_equipo'] = True
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


class UserRoleForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de administrar equipo, donde se pueden modificar qué
    usuarios pertenecen a un proyecto y cuales son sus roles.

    Posee campos correspondientes a los atributos de nombre, apellido, y correo
    electrónico. Además, posee un campo adicional para el rol del usuario.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    |
    """

    def __init__(self, *args, usuario_actual, proyecto_actual, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)
        self.fields['rol'] = forms.ModelChoiceField(
            queryset=Role.objects.filter(proyecto=proyecto_actual),
            initial=self.instance.participa_set.get(proyecto=proyecto_actual).rol,
            disabled=self.instance == usuario_actual
        )
        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['email'].disabled = True

        self.usuario_actual = usuario_actual
        self.proyecto_actual = proyecto_actual

    def clean(self):
        cleaned_data = super(ModelForm, self).clean()
        if cleaned_data.get('DELETE'):
            cleaned_data['DELETE'] = False
            self.proyecto_actual.quitar_rol(self.instance)
            cleaned_data.pop('rol')
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get('rol'):
            self.proyecto_actual.asignar_rol(self.instance, self.cleaned_data['rol'].nombre)
        super(UserRoleForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email']


class AgregarMiembroForm(forms.Form):

    def __init__(self, *args, proyecto_id, **kwargs):
        self.proyecto = proyecto_id
        super().__init__(*args, **kwargs)
        self.fields['usuarios'] = \
            forms.ModelChoiceField(queryset=User.objects.exclude(participa__proyecto=proyecto_id)
                                   .exclude(pk='AnonymousUser'))
        self.fields['roles'] = \
            forms.ModelChoiceField(queryset=Role.objects.filter(proyecto=proyecto_id))

    def save(self):
        self.proyecto.asignar_rol(self.cleaned_data['usuarios'], self.cleaned_data['roles'].nombre)


class UploadFileForm(forms.Form):
    """
    Permite enviar archivos al servidor.

    **Fecha:** 07/09/21

    |
    """
    archivo = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
