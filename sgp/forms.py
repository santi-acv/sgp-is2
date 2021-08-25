from django import forms
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm

from .models import User


class UserForm(ModelForm):
    crear_proyecto = forms.BooleanField()
    administrar = forms.BooleanField()
    auditar = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['crear_proyecto'].initial = kwargs['instance'].has_perm('sgp.crear_proyecto')
        self.fields['administrar'].initial = kwargs['instance'].has_perm('sgp.administrar')
        self.fields['auditar'].initial = kwargs['instance'].has_perm('sgp.auditar')

    def save(self, commit=True):
        ct = ContentType.objects.get_for_model(User)
        p = self.instance.user_permissions
        if self.fields['crear_proyecto']:
            p.add(Permission.objects.get(content_type=ct, codename='crear_proyecto'))
        if self.fields['administrar']:
            p.add(Permission.objects.get(content_type=ct, codename='administrar'))
        if self.fields['auditar']:
            p.add(Permission.objects.get(content_type=ct, codename='auditar'))
        super(UserForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'crear_proyecto', 'administrar', 'auditar']
