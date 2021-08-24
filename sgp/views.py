from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse


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
