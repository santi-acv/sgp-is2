from django.forms import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from guardian.shortcuts import get_objects_for_user

from .models import User, Proyecto, Role
from .forms import ProyectoForm, UserForm, RoleForm


def index(request):
    """
    Retorna la págino de inicio. Sujeto a cambios.\n
    Fecha: 15/08/21\n
    Artefacto: Página de inicio
    """
    context = None
    if request.user.is_authenticated:
        context = {'proyectos': get_objects_for_user(request.user, 'sgp.vista')}
    return render(request, 'sgp/index.html', context)


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
    UserFormSet = modelformset_factory(User, form=UserForm, extra=0, can_delete=True)
    if request.method == 'POST':
        formset = UserFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    return HttpResponseRedirect(reverse('sgp:administrar'))
            return HttpResponseRedirect(reverse('sgp:index'))
        else:
            return HttpResponse(str(formset))
    else:
        formset = UserFormSet(queryset=User.objects.exclude(user_id='AnonymousUser'))
    return render(request, 'sgp/administrar.html', {'formset': formset})


def crear_proyecto(request):
    """
    Muestra una página con los parámetros para crear un proyecto nuevo.\n
    Fecha: 25/08/21\n
    Artefacto: Módulo de proyecto
    """
    submitted = False
    # if they filled out the form and clicked the button, they posted it
    # if they did then take whatever they posted, request.POST, and pass it into our ProyectoFrom
    if request.method == "POST":
        form = ProyectoForm(request.POST)
        if form.is_valid():
            form.instance.creador = request.user
            form.save()
            proyecto = form.instance
            proyecto.crear_roles_predeterminados()
            proyecto.asignar_rol(request.user, 'Scrum master')
            return HttpResponseRedirect(reverse('sgp:index'))
        else:
            return HttpResponse(str(form))

    # if they didn't fill out the form, they just came to the web page
    # they are getting the web page
    else:
        form = ProyectoForm
        if 'submitted' in request.GET:
            submitted = True
    context = {'form': form, 'submitted': submitted}
    return render(request, 'sgp/crear_proyecto.html', context)


def mostrar_proyecto(request, proyecto_id):
    """
    Muestra una página con la información de un proyecto.\n
    Fecha: 02/09/21\n
    Artefacto: Módulo de proyecto
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    context = {'proyecto': proyecto}
    return render(request, 'sgp/mostrar_proyecto.html', context)


def editar_proyecto(request, proyecto_id):
    """
    Muestra una página con los parámetros modificables de un proyecto creado.\n
    Fecha: 02/09/21\n
    Artefacto: Módulo de proyecto
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    form = ProyectoForm(request.POST or None, instance=proyecto)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))
    context = {'proyecto': proyecto, 'form': form}
    return render(request, 'sgp/editar_proyecto.html', context)


def eliminar_proyecto(request, proyecto_id):
    """
    Elimina un proyecto creado de la base de datos del sistema.\n
    Fecha: 02/09/21\n
    Artefacto: Módulo de proyecto
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    proyecto.delete()
    return HttpResponseRedirect(reverse('sgp:index'))


def administrar_roles(request, proyecto_id, extra=0):
    """
    Muestra una página que permite controlar los roles y permisos de los usuarios que pertenecen a un proyecto.\n
    Fecha: 25/08/21\n
    Artefacto: Roles de proyecto
    """
    RoleFormSet = modelformset_factory(Role, form=RoleForm, extra=extra, can_delete=True)
    if request.method == 'POST':
        formset = RoleFormSet(request.POST)

        # Si uno de los roles es nuevo, apuntarlo al proyecto actual
        for form in formset:
            if not form.instance.pk:
                form.instance.proyecto = Proyecto.objects.get(pk=proyecto_id)

        # Valida los datos
        if formset.is_valid():
            formset.save()

            # Si se borró un rol, regresar a la misma página
            for form in formset:
                if form.cleaned_data.get('DELETE'):
                    return HttpResponseRedirect(reverse('sgp:administrar_roles', kwargs={'proyecto_id': proyecto_id}))

            # Si no, regresar a la página del proyecto
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))

        # Ocurrió un error
        else:
            return HttpResponse(str(formset))

    # Si el request es de tipo GET, mostrar la lista de permisos
    else:
        formset = RoleFormSet(queryset=Role.objects.filter(proyecto=proyecto_id))
        return render(request, 'sgp/administrar_roles.html',
                      {'proyecto_id': proyecto_id, 'formset': formset, 'extra': extra+1})
