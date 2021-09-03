
from django import forms
from django.forms import ModelForm
from guardian.shortcuts import assign_perm, remove_perm

from .models import User, Proyecto


class UserForm(ModelForm):
    crear_proyecto = forms.BooleanField(required=False)
    administrar = forms.BooleanField(required=False)
    auditar = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['crear_proyecto'].initial = kwargs['instance'].has_perm('sgp.crear_proyecto')
        self.fields['administrar'].initial = kwargs['instance'].has_perm('sgp.administrar')
        self.fields['auditar'].initial = kwargs['instance'].has_perm('sgp.auditar')

    def save(self, commit=True):
        permisos = ['crear_proyecto', 'administrar', 'auditar']
        for p in permisos:
            if self.cleaned_data[p]:
                assign_perm('sgp.' + p, self.instance)
            else:
                remove_perm('sgp.' + p, self.instance)
        super(UserForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'crear_proyecto', 'administrar', 'auditar']


# Create the form class
class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ('nombre_proyecto', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_sprint')
