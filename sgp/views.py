from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

from .models import User
from .models import Proyecto
from .forms import ProyectoForm



def index(request):
    """
    Retorna la págino de inicio. Sujeto a cambios.\n
    Fecha: 15/08/21\n
    Artefacto: Página de inicio
    """
    return render(request, 'sgp/index.html')


def login_view(request):
    """
    Inicia la sesión del usuario.\n
    Fecha: 20/08/21\n
    Artefacto: Página de inicio
    """
    user = authenticate(request, token=request.POST['idtoken'])
    if user is not None:
        login(request, user)
        return HttpResponse("User logged in")
    else:
        return HttpResponse("Login error!!!", status=401)


def logout_view(request):
    """
    Cierra la sesión del usuario.\n
    Fecha: 20/08/21\n
    Artefacto: Página de inicio
    """
    logout(request)
    return HttpResponseRedirect(reverse('sgp:index'))


def administrar(request):
    """
    Muestra una página que permite controlar los permisos de los usuarios registrados.\n
    Fecha: 24/08/21\n
    Artefacto: Módulo de seguridad
    """
    if request.method == 'POST':
        return render(request, 'sgp/administrar.html', {'users': User.objects.all()})
    else:
        return render(request, 'sgp/administrar.html', {'users': User.objects.all()})


def proyecto(request):
    """
    Muestra una página con los parámetros para crear un proyecto nuevo.\n
    Fecha: 25/08/21\n
    Artefacto: Módulo de proyecto
    """
    submitted = False
    #if they filled out the form and clicked the button, they posted it
    #if they did then take whatever they posted, request.POST, and pass it into our ProyectoFrom
    if request.method == "POST":
        form = ProyectoForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/proyecto?submitted=True')
    #if they didn't fill out the form, they just came to the web page
    #they are getting the web page
    else:
        form = ProyectoForm
        if 'submitted' in request.GET:
            submitted = True
    context = {'form': form, 'submitted': submitted}
    return render(request, 'sgp/proyecto.html', context)
