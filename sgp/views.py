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
from django.utils import timezone
from django.utils.timezone import now
from guardian.shortcuts import get_objects_for_user

from .models import User, Proyecto, Role, Sprint, UserStory
from .forms import ProyectoForm, UserForm, RoleForm, UserRoleForm, AgregarMiembroForm, UploadFileForm, SprintForm, \
    UserStoryForm, ComentarioForm


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
        form = ProyectoForm()
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
    error = None
    if request.method == 'POST':
        error = proyecto.validar()
        if not error:
            proyecto.estado = proyecto.Estado.INICIADO
            proyecto.fecha_inicio = now()
            proyecto.save()
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto.id}))
    context = {'proyecto': proyecto, 'error': error}
    return render(request, 'sgp/proyecto.html', context)


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
    if request.method == 'POST':
        if 'eliminar' in request.POST:
            proyecto.delete()
            return HttpResponseRedirect(reverse('sgp:index', kwargs={'proyecto_id': proyecto_id}))
        else:
            form = ProyectoForm(request.POST, instance=proyecto)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))
    else:
        form = ProyectoForm(instance=proyecto)
    context = {'proyecto': proyecto, 'form': form}
    return render(request, 'sgp/proyecto-editar.html', context)


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

    return render(request, 'sgp/proyecto-roles.html',
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
    Permite modificar el equipo asociado a un proyecto.

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

            # Si se eliminó a un usuario del equipo, mostrar de nuevo la pagina
            for form in formset:
                if form.cleaned_data.get('borrar'):
                    return HttpResponseRedirect(reverse('sgp:administrar_equipo',
                                                        kwargs={'proyecto_id': proyecto.id}))

            # Si solo se cambiaron los roles, volver a la pagina de proyecto
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto',
                                                kwargs={'proyecto_id': proyecto_id}))

    # Enviar una lista de miembros
    formset = UserRoleFormSet(queryset=User.objects.filter(participa__proyecto=proyecto_id),
                              form_kwargs={'usuario_actual': usuario, 'proyecto_actual': proyecto})

    return render(request, 'sgp/proyecto-equipo.html',
                  {'proyecto': proyecto, 'formset': formset, 'usuario': usuario, 'lista': lista})


def product_backlog(request, proyecto_id):
    """
    **Fecha:** 26/09/21
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    backlog = proyecto.product_backlog.exclude(estado=UserStory.Estado.CANCELADO).order_by('prioridad')

    context = {'proyecto': proyecto, 'backlog': backlog}

    if request.user.has_perm('gestionar_proyecto', proyecto) or request.user.has_perm('pila_producto', proyecto):
        context['backlog_cancelado'] = proyecto.product_backlog.filter(estado=UserStory.Estado.CANCELADO)

    return render(request, 'sgp/proyecto-backlog.html', context)


def crear_user_story(request, proyecto_id):
    """
    **Fecha:** 26/09/21
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    if request.method == "POST":
        form = UserStoryForm(request.POST, usuario=request.user, proyecto=proyecto)
        if form.is_valid():
            form.instance.proyecto = proyecto
            form.instance.numero = UserStory.objects.filter(proyecto=proyecto).count() + 1
            form.save()
            return HttpResponseRedirect(reverse('sgp:product_backlog', kwargs={'proyecto_id': proyecto_id}))
    else:
        form = UserStoryForm(usuario=request.user, proyecto=proyecto)
    return render(request, 'sgp/crear_user_story.html', {'form': form, 'proyecto': proyecto})


def mostrar_user_story(request, proyecto_id, us_numero):
    """
    **Fecha:** 28/09/21
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    user_story = UserStory.objects.get(proyecto_id=proyecto_id, numero=us_numero)

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            form.instance.user_story = user_story
            form.instance.autor = request.user
            form.instance.fecha = timezone.localdate()
            form.save()
            return HttpResponseRedirect(reverse('sgp:mostrar_user_story',
                                                kwargs={'proyecto_id': proyecto_id, 'us_numero': us_numero}))
    else:
        form = ComentarioForm()
    context = {'proyecto': proyecto, 'user_story': user_story, 'form': form}
    return render(request, 'sgp/user-story.html', context)


def editar_user_story(request, proyecto_id, us_numero):
    """
    Permite modificar el user story.

    **Fecha:** 28/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    user_story = UserStory.objects.get(proyecto_id=proyecto_id, numero=us_numero)
    if request.method == 'POST':
        if 'guardar' in request.POST:
            form = UserStoryForm(request.POST, instance=user_story, usuario=request.user, proyecto=proyecto)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('sgp:mostrar_user_story',
                                                    kwargs={'proyecto_id': proyecto_id, 'us_numero': us_numero}))
        else:
            if 'eliminar' in request.POST:
                user_story.estado = UserStory.Estado.CANCELADO
            elif 'restaurar' in request.POST:
                user_story.estado = UserStory.Estado.PENDIENTE
            user_story.save()
            return HttpResponseRedirect(reverse('sgp:product_backlog', kwargs={'proyecto_id': proyecto_id}))
    else:
        form = UserStoryForm(instance=user_story, usuario=request.user, proyecto=proyecto)
    context = {'proyecto': proyecto, 'form': form, 'user_story': user_story}
    return render(request, 'sgp/user-story-editar.html', context)


def crear_sprint(request, proyecto_id):
    """
    **Fecha:** 24/09/21
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    if request.method == "POST":
        form = SprintForm(request.POST)
        if form.is_valid():
            form.instance.proyecto = proyecto
            form.save()
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))
    else:
        form = SprintForm()
    return render(request, 'sgp/crear_sprint.html', {'form': form, 'proyecto': proyecto})


def mostrar_sprint(request, proyecto_id, sprint_id):
    """
    **Fecha:** 24/09/21
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = Sprint.objects.get(id=sprint_id)
    context = {'proyecto': proyecto, 'sprint': sprint}
    return render(request, 'sgp/sprint.html', context)
