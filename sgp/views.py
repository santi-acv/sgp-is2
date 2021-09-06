from django.forms import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils.timezone import now
from guardian.shortcuts import get_objects_for_user

from .models import User, Proyecto, Role
from .forms import ProyectoForm, UserForm, RoleForm


def index(request):
    """
    Representa la página de inicio.

    Para usuarios que no han iniciado sesión, da una bienvenida al sistema y
    muestra un botón de acceso con Google.

    Para usuarios que ya accedieron al sistema, muestra la lista de proyectos a
    los que estos pertenecen. Si el usuario cuenta con el permiso de creación
    de proyectos, presenta una opción para crear uno. Si el usuario cuenta con
    el permiso de administración de usuarios, presenta una opción para hacerlo.

    **Fecha:** 15/08/21

    **Artefacto:** página de inicio

    |
    """
    context = None
    if request.user.is_authenticated:
        context = {'proyectos': get_objects_for_user(request.user, 'sgp.vista')}
    return render(request, 'sgp/index.html', context)


def login_view(request):
    """
    Permite a los usuarios iniciar sesión.

    Debe recibir un request del tipo POST con un atributo ``idtoken`` que
    contenga el token de identidad retornado por el servicio de authenticación
    de Google.

    **Fecha:** 15/08/21

    **Artefacto:** módulo de seguridad

    |
    """
    user = authenticate(request, token=request.POST['idtoken'])
    if user is not None:
        login(request, user)
        return HttpResponse("User logged in")
    else:
        return HttpResponse("Login error!!!", status=401)


def logout_view(request):
    """
    Permite a los usuarios cerrar sesión.

    Si el usuario tiene una sesión abierta, la cierra.

    **Fecha:** 15/08/21

    **Artefacto:** módulo de seguridad

    |
    """
    logout(request)
    return HttpResponseRedirect(reverse('sgp:index'))


def administrar(request):
    """
    Permite administrar los permisos de los usuarios registrados y eliminarlos
    de la base de datos si es necesario.

    **Fecha:** 24/08/21

    **Artefacto:** módulo de seguridad

    |
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
    Permite crear un proyecto nuevo.

    Al acceder, muestra un formulario con los datos requeridos para crear un
    proyecto. Si estos son válidos, lo agrega a la base de datos con los roles
    predetermanidos y asigna el rol de Scrum Master al usuario que lo creó.

    **Fecha:** 25/08/21

    **Artefacto:** módulo de proyecto

    |
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
    Muestra una página con la información del proyecto, y además incluye
    opciones para iniciar, modificar, o eliminar el proyecto.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    if request.method == 'POST':
        proyecto.status = 'Iniciado'
        proyecto.fecha_inicio = now()
        proyecto.save()
        return HttpResponse("Proyecto iniciado")
    context = {'proyecto': proyecto}
    return render(request, 'sgp/mostrar_proyecto.html', context)


def editar_proyecto(request, proyecto_id):
    """
    Permite modificar el proyecto.

    Muestra un formulario similar al de creación de proyectos. Si los datos
    recibidos son válidos, actualiza la entrada en la base de datos.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
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
    Permite eliminar el proyecto.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    proyecto.delete()
    return HttpResponseRedirect(reverse('sgp:index'))


def administrar_roles(request, proyecto_id):
    """
    Permite modificar los roles asociados a un proyecto.

    Muestra una lista de los roles actuales del proyecto junto con sus
    respectivos nombres y permisos. El usuario puede modificar estos roles,
    crear roles nuevos, o eliminar roles existentes.

    Si la URL tiene el parámetro ``extra``, agrega ese número de campos vacíos
    a la lista. Esto se utiliza para crear nuevos roles.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    try:
        extra = int(request.GET.get('extra', ''))
    except ValueError:
        extra = 0
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
