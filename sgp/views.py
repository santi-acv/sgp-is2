"""
Una vista en Django es una función que recibe una solicitud web y envía una
respuesta web. Cada vista corresponde a uno o más patrones de URLs, según el
archivo ``urls.py``.

.. literalinclude:: ../../sgp/urls.py

A continuación se documentan todas las vistas de la aplicación SGP.
"""
import json

from django.forms import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils.timezone import now
from guardian.shortcuts import get_objects_for_user

from .models import User, Proyecto, Role
from .forms import ProyectoForm, UserForm, RoleForm, UserRoleForm, AgregarMiembroForm, UploadFileForm


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
    if request.method == "POST":
        form = ProyectoForm(request.POST)
        if form.is_valid():
            form.instance.creador = request.user
            form.save()
            proyecto = form.instance
            proyecto.crear_roles_predeterminados()
            proyecto.asignar_rol(request.user, 'Scrum master')
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto.id}))
    else:
        form = ProyectoForm
    return render(request, 'sgp/crear_proyecto.html', {'form': form})


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
        proyecto.estado = proyecto.Estado.INICIADO
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
    crear roles nuevos, o eliminar roles existentes. También presenta opciones
    para exportar los roles actuales a un archivo JSON y para importar roles de
    un archivo

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    rol = Role.objects.get(proyecto=proyecto, participa__usuario=request.user)
    RoleFormSet = modelformset_factory(Role, form=RoleForm, extra=0, can_delete=True)

    # Si el request es de tipo POST, procesar los roles recibidos
    if request.method == 'POST':
        formset = RoleFormSet(request.POST, form_kwargs={'rol_actual': rol})

        # Si uno de los roles es nuevo, apuntarlo al proyecto actual
        for form in formset:
            if not form.instance.pk:
                form.instance.proyecto = proyecto

        # Guardar los roles
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))

    # Si el request es de tipo GET, enviar una lista de roles
    else:
        formset = RoleFormSet(queryset=Role.objects.filter(proyecto=proyecto_id),
                              form_kwargs={'rol_actual': rol})

    return render(request, 'sgp/administrar_roles.html',
                  {'proyecto': proyecto, 'formset': formset, 'rol': rol, 'file_form': UploadFileForm()})


def importar_roles(request, proyecto_id):
    """
    Permite importar roles desde un archivo JSON.

    Recibe un request POST con un atributo archivo que contenga los roles a
    importar.

    **Fecha:** 07/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        proyecto = Proyecto.objects.get(pk=proyecto_id)
        roles = json.load(request.FILES['archivo'])
        for rol in roles:
            proyecto.crear_rol(rol['nombre'], rol['permisos'])
    else:
        print(form)
    return HttpResponseRedirect(reverse('sgp:administrar_roles', kwargs={'proyecto_id': proyecto_id}))


def exportar_roles(request, proyecto_id):
    """
    Permite exportar roles hacia un archivo JSON.

    Retorna un archivo con los roles del proyecto que puede ser descargado.

    **Fecha:** 07/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    roles = []
    for instance in Role.objects.filter(proyecto=proyecto_id):
        rol = dict()
        rol['nombre'] = instance.nombre
        perms = []
        for perm in instance.permisos.all():
            perms.append(perm.codename)
        rol['permisos'] = perms
        roles.append(rol)
    print(json.dumps(roles))
    response = HttpResponse(json.dumps(roles), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=roles-proyecto-'+str(proyecto_id)+'.json'
    return response


def administrar_equipo(request, proyecto_id):
    """
    Permite modificar el equipo asociados a un proyecto.

    Muestra una lista de los miembros actuales del proyecto junto con sus
    respectivos roles. El usuario agregar miembros al equipo, removerlos, o
    asignarles roles diferentes.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    usuario = request.user
    UserRoleFormSet = modelformset_factory(User, form=UserRoleForm, extra=0, can_delete=True)

    # Si se agregó un nuevo miembro al equipo, registrarlo
    if 'agregar_usuario' in request.POST:
        lista = AgregarMiembroForm(request.POST, proyecto_id=proyecto)
        if lista.is_valid():
            lista.save()
            return HttpResponseRedirect(reverse('sgp:administrar_equipo',
                                                kwargs={'proyecto_id': proyecto_id}))
    else:
        lista = AgregarMiembroForm(proyecto_id=proyecto)

    # Si se modificaron los roles de los miembros, procesar los cambios
    if 'asignar_roles' in request.POST:
        formset = UserRoleFormSet(request.POST,
                                  form_kwargs={'usuario_actual': usuario, 'proyecto_actual': proyecto})
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('sgp:administrar_equipo',
                                                kwargs={'proyecto_id': proyecto_id}))
    else:
        # Enviar una lista de miembros
        formset = UserRoleFormSet(queryset=User.objects.filter(participa__proyecto=proyecto_id),
                                  form_kwargs={'usuario_actual': usuario, 'proyecto_actual': proyecto})

    return render(request, 'sgp/administrar_equipo.html',
                  {'proyecto': proyecto, 'formset': formset, 'usuario': usuario, 'lista': lista})
