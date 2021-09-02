from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm

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
        ct = ContentType.objects.get_for_model(User)
        permisos = ['crear_proyecto', 'administrar', 'auditar']
        up = self.instance.user_permissions
        for p in permisos:
            if self.cleaned_data[p]:
                up.add(Permission.objects.get(content_type=ct, codename=p))
            else:
                up.remove(Permission.objects.get(content_type=ct, codename=p))
        super(UserForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'crear_proyecto', 'administrar', 'auditar']


# Create a Project Form

class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ('nombre_proyecto', 'fecha_inicio', 'fecha_fin')

