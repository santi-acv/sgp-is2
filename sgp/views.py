from django.shortcuts import render


def index(request):
    """
    Retorna la págino de inicio. Sujeto a cambios.\n
    Fecha: 15/08/21\n
    Artefacto: Página de inicio
    """
    return render(request, 'sgp/index.html')
