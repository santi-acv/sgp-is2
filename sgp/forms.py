from django import forms
from django.forms import ModelForm
from .models import Proyecto

# Create a Project Form

class ProyectoForm(ModelForm):
    class Meta:
        model = Proyecto
        fields = ('nombre_proyecto', 'fecha_inicio', 'fecha_fin')