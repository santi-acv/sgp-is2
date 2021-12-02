"""
Una vista en Django es una función que recibe una solicitud web y envía una
respuesta web. Cada vista corresponde a uno o más patrones de URLs, según el
archivo ``urls.py``.

.. literalinclude:: ../../sgp/urls.py

A continuación se documentan todas las vistas de la aplicación SGP.
"""
import datetime
import json

from django.db.models import Sum
from django.forms import modelformset_factory
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import get_objects_for_user

from .models import User, Proyecto, Role, Sprint, UserStory, Incremento
from .forms import ProyectoForm, UserForm, RoleForm, UserRoleForm, AgregarMiembroForm, UploadFileForm, SprintForm, \
    UserStoryForm, ComentarioForm, AgregarUserStoryForm, AgregarDesarrolladorForm, UserSprintForm, BacklogForm
from .utils import render_to_pdf, enviar_notificacion


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
        context = {'proyectos': get_objects_for_user(request.user, 'sgp.vista').order_by('fecha_creacion')}
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
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


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
        formset = UserFormSet(queryset=User.objects.exclude(user_id='AnonymousUser').order_by('fecha_registro'))
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
    Muestra la información principal del proyecto y permite cambiar su estado.
    Incluye una lista de sprints y enlaces para acceder a cada uno de ellos.

    Si el estado del proyecto es pendiente, verifica si es posible iniciarlo y
    muestra una lista de errores y advertencias. Si la lista de errores está
    vacía, permite iniciar el proyecto. Si el estado es iniciado, realiza el
    mismo procedimiento pero para finalizarlo en vez de iniciarlo.

    **Fecha:** 21/10/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    mensajes = None

    pendiente = Proyecto.Estado.PENDIENTE
    iniciado = Proyecto.Estado.INICIADO
    finalizado = Proyecto.Estado.FINALIZADO

    if proyecto.estado == pendiente:
        mensajes = proyecto.validar_inicio()
    elif proyecto.estado == iniciado:
        mensajes = proyecto.validar_fin()

    if request.method == 'POST' and not mensajes['errores']:
        if proyecto.estado == pendiente:
            proyecto.estado = iniciado
            proyecto.fecha_inicio = timezone.now()
            enviar_notificacion(proyecto, 'proyecto', 'iniciado')
        elif proyecto.estado == iniciado:
            proyecto.estado = finalizado
            proyecto.fecha_fin = timezone.now()
            enviar_notificacion(proyecto, 'proyecto', 'finalizado')
        proyecto.save()
        return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto.id}))
    context = {'proyecto': proyecto, 'mensajes': mensajes}
    return render(request, 'sgp/proyecto.html', context)


def editar_proyecto(request, proyecto_id):
    """
    Permite modificar los parámetros del proyecto o eliminarlo.

    Muestra una instancia de ProyectoForm. Si los datos recibidos a través del
    formulario son válidos, actualiza la entrada en la base de datos.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    if request.method == 'POST':
        if 'eliminar' in request.POST:
            proyecto.delete()
            return HttpResponseRedirect(reverse('sgp:index'))
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
    un archivo.

    Utiliza un formset con instancias de RoleForm para la lista de roles, y una
    instancia de UploadFileForm para importar roles.

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

    Utiliza un formset con instancias de UserRoleForm para la lista de usuarios
    que pertenecen al proyecto y una instancia de AgregarMiembroForm para los
    usuarios que no pertenecen.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    usuario = request.user
    UserRoleFormSet = modelformset_factory(User, form=UserRoleForm, extra=0, can_delete=True)

    # Si se agregó un nuevo miembro al equipo, registrarlo
    if 'agregar_usuario' in request.POST:
        lista = AgregarMiembroForm(request.POST, proyecto=proyecto)
        if lista.is_valid():
            lista.save()
            return HttpResponseRedirect(reverse('sgp:administrar_equipo',
                                                kwargs={'proyecto_id': proyecto_id}))
    else:
        lista = AgregarMiembroForm(proyecto=proyecto)

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
    formset = UserRoleFormSet(
        queryset=User.objects.filter(participa__proyecto=proyecto_id).order_by('participa__rol'),
        form_kwargs={'usuario_actual': usuario, 'proyecto_actual': proyecto})

    return render(request, 'sgp/proyecto-equipo.html',
                  {'proyecto': proyecto, 'formset': formset, 'usuario': usuario, 'lista': lista})


def product_backlog(request, proyecto_id):
    """
    Muestra el product backlog del proyecto.

    Coloca los user stories cancelados en una sección aparte de la lista, la
    cual solo es visible para usuarios con permisos de gestión de proyecto o de
    pila de producto.

    **Fecha:** 26/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)

    backlog = dict()

    backlog['activo'] = proyecto.product_backlog.exclude(estado=[UserStory.Estado.CANCELADO]).order_by('prioridad')
    if request.user.has_perm('gestionar_proyecto', proyecto) or request.user.has_perm('pila_producto', proyecto):
        backlog['cancelado'] = proyecto.product_backlog.filter(estado=UserStory.Estado.CANCELADO)

    context = {'proyecto': proyecto, 'backlog': backlog}
    return render(request, 'sgp/proyecto-backlog.html', context)


def crear_user_story(request, proyecto_id):
    """
    Permite crear un user story.

    Muestra una instancia de UserStoryForm. Si los datos son válidos, agrega el
    user story al proyecto y lo guarda en la base de datos.

    **Fecha:** 26/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    if request.method == "POST":
        form = UserStoryForm(request.POST, usuario=request.user, proyecto=proyecto)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sgp:product_backlog', kwargs={'proyecto_id': proyecto_id}))
    else:
        form = UserStoryForm(usuario=request.user, proyecto=proyecto)
    return render(request, 'sgp/crear_user_story.html', {'form': form, 'proyecto': proyecto})


def mostrar_user_story(request, proyecto_id, us_numero):
    """
    Muestra los parámetros y comentarios del user story.

    Si el usuario tiene permisos de gestión de proyecto o pila de producto,
    muestra una opción para editar el user story.

    **Fecha:** 28/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    user_story = UserStory.objects.get(proyecto_id=proyecto_id, numero=us_numero)

    if request.method == 'POST':
        form = ComentarioForm(request.POST, usuario=request.user, user_story=user_story)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sgp:mostrar_user_story',
                                                kwargs={'proyecto_id': proyecto_id, 'us_numero': us_numero}))
    else:
        form = ComentarioForm()
    context = {'proyecto': proyecto, 'user_story': user_story, 'form': form}
    return render(request, 'sgp/user-story.html', context)


def editar_user_story(request, proyecto_id, us_numero):
    """
    Permite modificar los parámetros del user story o eliminarlo.

    Muestra una instancia de UserStoryForm. Si los datos recibidos a través del
    formulario son válidos, actualiza la entrada en la base de datos.

    **Fecha:** 28/09/21

    **Artefacto:** módulo de desarrollo

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
                user_story.sprint = None
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
    Permite crear un sprint.

    Muestra una instancia de SprintForm. Si los datos son válidos, agrega el
    sprint al proyecto y lo guarda en la base de datos.

    **Fecha:** 24/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    if request.method == "POST":
        form = SprintForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))
    else:
        form = SprintForm(proyecto=proyecto)
    return render(request, 'sgp/crear_sprint.html', {'form': form, 'proyecto': proyecto})


def mostrar_sprint(request, proyecto_id, sprint_id):
    """
    Muestra la información principal del sprint y permite cambiar su estado.

    Si el estado del sprint es pendiente, verifica si es posible iniciarlo y
    muestra una lista de errores y advertencias. Si la lista de errores está
    vacía, permite iniciar el sprint. Si el estado es iniciado, realiza el
    mismo procedimiento pero para finalizarlo en vez de iniciarlo.

    **Fecha:** 21/10/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    sprint = Sprint.objects.get(id=sprint_id)
    mensajes = None

    pendiente = Sprint.Estado.PENDIENTE
    iniciado = Sprint.Estado.INICIADO
    finalizado = Sprint.Estado.FINALIZADO

    if sprint.estado == pendiente:
        mensajes = sprint.validar_inicio()
    elif sprint.estado == iniciado:
        mensajes = sprint.validar_fin()

    if request.method == 'POST' and not mensajes['errores']:
        if sprint.estado == pendiente:
            sprint.estado = iniciado
            sprint.fecha_inicio = timezone.now()
            sprint.fecha_fin_original = sprint.fecha_fin
            enviar_notificacion(sprint, 'sprint', 'iniciado')
        elif sprint.estado == iniciado:
            sprint.concluir_user_stories()
            sprint.estado = finalizado
            sprint.fecha_fin = timezone.now()
            enviar_notificacion(sprint, 'sprint', 'finalizado')
        sprint.save()
        return HttpResponseRedirect(
            reverse('sgp:mostrar_sprint', kwargs={'proyecto_id': proyecto.id, 'sprint_id': sprint.id}))

    context = {'proyecto': proyecto, 'sprint': sprint, 'mensajes': mensajes}
    return render(request, 'sgp/sprint.html', context)


def editar_sprint(request, proyecto_id, sprint_id):
    """
    Permite modificar los parámetros del sprint o eliminarlo.

    Muestra una instancia de SprintForm. Si los datos recibidos a través del
    formulario son válidos, actualiza la entrada en la base de datos.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(pk=proyecto_id)
    sprint = Sprint.objects.get(pk=sprint_id)
    if request.method == 'POST':
        if 'eliminar' in request.POST:
            sprint.delete()
            return HttpResponseRedirect(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto_id}))
        else:
            form = SprintForm(request.POST, proyecto=proyecto, instance=sprint)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(
                    reverse('sgp:mostrar_sprint', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))
    else:
        form = SprintForm(proyecto=proyecto, instance=sprint)
    context = {'proyecto': proyecto, 'sprint': sprint, 'form': form}
    return render(request, 'sgp/sprint-editar.html', context)


def equipo_sprint(request, proyecto_id, sprint_id):
    """
    Permite modificar el equipo asociado a un sprint.

    Muestra una lista de los miembros actuales del proyecto junto con sus
    respectivas horas disponibles diarias. El usuario agregar miembros al
    equipo, removerlos, o asignarles una cantidad diferente de horas.

    Utiliza un formset con instancias de UserSprintForm para la lista de
    usuarios que pertenecen al sprint y una instancia de
    AgregarDesarrolladorForm para los usuarios que no pertenecen.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = Sprint.objects.get(id=sprint_id)
    UserSprintFormSet = modelformset_factory(User, form=UserSprintForm, extra=0, can_delete=True)

    if 'agregar_usuario' in request.POST:
        form = AgregarDesarrolladorForm(request.POST, proyecto=proyecto, sprint=sprint)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('sgp:equipo_sprint', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))
    else:
        form = AgregarDesarrolladorForm(proyecto=proyecto, sprint=sprint)

    if 'editar_usuarios' in request.POST:
        formset = UserSprintFormSet(request.POST, form_kwargs={'sprint': sprint})
        if formset.is_valid():
            formset.save()

            for form in formset:
                if form.cleaned_data.get('borrar'):
                    return HttpResponseRedirect(
                        reverse('sgp:equipo_sprint', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))

            return HttpResponseRedirect(
                reverse('sgp:mostrar_sprint', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))

    else:
        formset = UserSprintFormSet(queryset=sprint.equipo.all(), form_kwargs={'sprint': sprint})

    return render(request, 'sgp/sprint-equipo.html',
                  {'proyecto': proyecto, 'sprint': sprint, 'formset': formset, 'form': form})


def sprint_backlog(request, proyecto_id, sprint_id):
    """
    Muestra el backlog asociado a ese sprint.

    Permite asiginar una prioridad, una estimación de horas, y un desarrollador
    a cada sprint mediante un formset con instancias de BacklogForm. También
    permite quitar sprints o agregarlos al backlog mediante una instancia de
    AgregarUserStoryForm.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = Sprint.objects.get(id=sprint_id)
    BacklogFormSet = modelformset_factory(UserStory, form=BacklogForm, extra=0, can_delete=True)

    if 'agregar_user_story' in request.POST:
        form = AgregarUserStoryForm(request.POST, proyecto=proyecto, sprint=sprint)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('sgp:sprint_backlog', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))
    else:
        form = AgregarUserStoryForm(proyecto=proyecto, sprint=sprint)

    if 'editar_user_stories' in request.POST:
        formset = BacklogFormSet(request.POST, form_kwargs={'proyecto': proyecto, 'sprint': sprint})
        if formset.is_valid():
            formset.save()
            if sprint.estado == Sprint.Estado.INICIADO:
                return HttpResponseRedirect(
                    reverse('sgp:sprint_backlog', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))
            for form in formset:
                if form.cleaned_data.get('borrar'):
                    return HttpResponseRedirect(
                        reverse('sgp:sprint_backlog', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))

            return HttpResponseRedirect(
                reverse('sgp:mostrar_sprint', kwargs={'proyecto_id': proyecto_id, 'sprint_id': sprint_id}))
    else:
        formset = BacklogFormSet(queryset=sprint.sprint_backlog.all().order_by('prioridad'),
                                 form_kwargs={'proyecto': proyecto, 'sprint': sprint})

    context = {'proyecto': proyecto, 'sprint': sprint, 'form': form, 'formset': formset}
    return render(request, 'sgp/sprint-backlog.html', context)


def planificacion(request, proyecto_id):
    """
    Muestra una lista de eventos pendientes con sus respectivas fechas. Incluye
    una columna indicando qué eventos se deben realizar el día de hoy y cuales
    fueron completados.

    **Fecha:** 21/10/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    eventos = [{
        'tipo': 'proyecto',
        'fecha': proyecto.fecha_inicio,
        'evento': 'Inicio',
        'done': proyecto.estado != Proyecto.Estado.PENDIENTE,
    }]

    for sprint in proyecto.sprint_set.all():
        eventos.append({
            'fecha': sprint.fecha_inicio,
            'evento': 'Inicio',
            'sprint': sprint,
            'done': sprint.estado != Sprint.Estado.PENDIENTE,
        })
        eventos.append({
            'fecha': sprint.fecha_fin,
            'evento': 'Fin',
            'sprint': sprint,
            'done': sprint.estado == Sprint.Estado.FINALIZADO,
        })

    eventos.append({
        'tipo': 'proyecto',
        'fecha': proyecto.fecha_fin,
        'evento': 'Fin',
        'done': proyecto.estado == Proyecto.Estado.FINALIZADO,
    })

    context = {'proyecto': proyecto, 'eventos': eventos}
    return render(request, 'sgp/proyecto-planificacion.html', context)


def kanban(request, proyecto_id):
    """
    Muestra un tablero kanban.

    Si el usuario tiene permisos de gestión de proyecto, muestra una entrada
    para cada user story y permite cancelarlos o aprobar aquellos que se
    encuentren en fase de QA. Si el usuario es un desarrollador, muestra los
    user stories que se le asignaron y permite trabajar horas o avanzar a la
    siguiente fase de desarrollo.

    **Fecha:** 23/10/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = proyecto.sprint_activo
    if request.method == 'POST':
        user_story = UserStory.objects.get(proyecto=proyecto, numero=request.POST['us'])

        pendiente = UserStory.Estado.PENDIENTE
        iniciado = UserStory.Estado.INICIADO
        fase_de_qa = UserStory.Estado.FASE_DE_QA
        finalizado = UserStory.Estado.FINALIZADO
        cancelado = UserStory.Estado.CANCELADO

        # si se han actualizado las horas
        if request.POST['accion'] == 'trabajar' and user_story.estado in [pendiente, iniciado]:
            horas = int(request.POST['horas'])
            if not horas:
                return HttpResponse(status=400)

            # registra el incremento
            Incremento.objects.create(user_story=user_story, usuario=request.user, horas=horas)

            # actualiza la información del user story
            user_story.horas_trabajadas += horas
            if user_story.estado == pendiente:
                user_story.estado = iniciado

        # marca el user story como iniciado
        else:
            if request.POST['accion'] == 'iniciar' and user_story.estado == pendiente:
                user_story.estado = iniciado

            # envía el user story a la fase de qa
            elif request.POST['accion'] == 'enviar_qa' and user_story.estado == iniciado:
                user_story.estado = fase_de_qa

            # marca el user story como finalizado
            elif request.POST['accion'] == 'aprobar' and user_story.estado == fase_de_qa:
                user_story.estado = finalizado

            # retorna el user story a la fase de trabajo
            elif request.POST['accion'] == 'rechazar' and user_story.estado == fase_de_qa:
                if user_story.horas_trabajadas == 0:
                    user_story.estado = pendiente
                else:
                    user_story.estado = iniciado

            # cancela el user story
            elif request.POST['accion'] == 'cancelar' and user_story.estado != finalizado:
                user_story.estado = cancelado

            # restaura el user story a la fase de trabajo
            elif request.POST['accion'] == 'restaurar' and user_story.estado == cancelado:
                if user_story.horas_trabajadas == 0:
                    user_story.estado = pendiente
                else:
                    user_story.estado = iniciado
            else:
                return HttpResponse(status=405)
            Incremento.objects.create(user_story=user_story, usuario=request.user, estado=user_story.estado)

        user_story.save()

        return HttpResponseRedirect(reverse('sgp:kanban', kwargs={'proyecto_id': proyecto.id}))

    # calcula las horas trabajadas y disponibles.
    participasprint = sprint.participasprint_set.filter(usuario=request.user).first()
    horas = {}
    if participasprint:
        horas['trabajadas'] = 0
        horas['disponibles'] = participasprint.horas_diarias
        for incremento in Incremento.objects.filter(user_story__in=participasprint.user_stories.all(),
                                                    usuario=request.user, fecha=timezone.localdate()):
            horas['trabajadas'] += incremento.horas
        horas['porcentaje'] = horas['trabajadas'] / horas['disponibles']

    # obtiene matriz de user stories
    tablero = dict()
    for estado in UserStory.Estado.values:
        tablero[estado] = []

    # si el usuario tiene permisos de gestion, muestra todas las user stories
    if request.user.has_perm('gestionar_proyecto', proyecto):
        for user_story in sprint.sprint_backlog.all():
            if participasprint and user_story in participasprint.user_stories.all():
                user_story.asignado = True
            tablero[str(user_story.estado)].append(user_story)

    # si no, muestra los user stories que tiene asignado
    else:
        for user_story in sprint.participasprint_set.get(usuario=request.user).user_stories.all():
            tablero[str(user_story.estado)].append(user_story)

    # agrega ordena las user stories en filas
    count = len(tablero[max(tablero, key=lambda e: len(tablero[e]))])
    for estado, lista in tablero.items():
        lista.extend([None for i in range(count-len(lista))])
    tablero = [*zip(*tablero.values())]

    context = {'proyecto': proyecto, 'sprint': sprint, 'horas': horas,
               'estados': UserStory.Estado.labels, 'tablero': tablero}
    return render(request, 'sgp/kanban.html', context)


def registro_kanban(request, proyecto_id):
    """
    Muestra el registro de actividad del flujo kanban.

    Obtiene cada instancia de la clase Incremento que pertenezca a un user
    story en el sprint backlog del sprint activo.

    **Fecha:** 19/11/21

    **Artefacto:** módulo de desarrollo

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = proyecto.sprint_activo
    registro = Incremento.objects.filter(user_story__sprint=sprint).order_by('fecha')
    context = {'proyecto': proyecto, 'sprint': sprint, 'registro': registro}
    return render(request, 'sgp/kanban-registro.html', context)


def burndown(request, proyecto_id, sprint_id):
    """
    Muestra el burndown chart del sprint.

    Calcula las horas que deben ser trabajadas cada día para cubrir el costo
    total del sprint backlog durante la duración original del sprint. Si este
    se extendie más allá de la fecha de fin originalmente planeada, la
    estimación permanece igual pero el gráfico se exitende hasta la fecha
    actual si el sprint se encuentra activo, o hasta la fecha real de fin si
    este ya terminó.

    También calcula las horas que se trabajaron en el sprint cada día contando
    instancias del modelo Incremento. Si se trabajaron más horas en el sprint
    que el costo estimado del backlog, la línea de horas restantes solamente
    disminuye hasta cero.

    |
    """
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = Sprint.objects.get(id=sprint_id)

    chart = {'fechas': [], 'ideal': [], 'restante': []}

    # agrega las fechas planeadas del sprint
    duracion = ((sprint.fecha_fin_original if sprint.fecha_fin_original else sprint.fecha_fin)
                - sprint.fecha_inicio).days
    for dias in range(duracion + 1):
        fecha = sprint.fecha_inicio + datetime.timedelta(days=dias)
        chart['fechas'].append(str(fecha))
        chart['ideal'].append(sprint.costo_backlog * (1 - dias / duracion))

    # agrega las fechas luego del final planeado del sprint
    if sprint.estado != Sprint.Estado.PENDIENTE:
        fecha_fin = timezone.localdate() if sprint.estado == Sprint.Estado.INICIADO else sprint.fecha_fin
        for dias in range((fecha_fin - sprint.fecha_fin).days):
            fecha = sprint.fecha_fin + datetime.timedelta(days=dias + 1)
            chart['fechas'].append(str(fecha))

    # calcula las horas trabajadas en cada día
    anterior = sprint.costo_backlog
    for dias in range(len(chart['fechas'])):
        fecha = sprint.fecha_inicio + datetime.timedelta(days=dias)
        incremento = Incremento.objects.filter(user_story__sprint=sprint,
                                               fecha=fecha).aggregate(Sum('horas'))['horas__sum']

        anterior = anterior - (int(incremento) if incremento else 0)
        if anterior <= 0 or fecha > timezone.localdate():
            if anterior <= 0:
                chart['restante'].append(0)
            break
        chart['restante'].append(anterior)

    context = {'proyecto': proyecto, 'sprint': sprint, 'chart': chart}
    return render(request, 'sgp/sprint-burndown.html', context=context)


def reporte_proyecto(request, proyecto_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    context = {'proyecto': proyecto,
               'filename': 'Reporte - Product Backlog'}
    return render_to_pdf(request, 'sgp/reporte-product-backlog.html', context=context)


def reporte_sprint(request, proyecto_id, sprint_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    sprint = Sprint.objects.get(id=sprint_id)

    backlog = {'terminados': sprint.sprint_backlog.filter(estado=UserStory.Estado.FINALIZADO),
               'pendientes': sprint.sprint_backlog.filter(estado=UserStory.Estado.PENDIENTE),
               'cancelados': sprint.sprint_backlog.filter(estado=UserStory.Estado.CANCELADO),
               'por terminar': sprint.sprint_backlog.filter(
                   estado__in=[UserStory.Estado.INICIADO, UserStory.Estado.FASE_DE_QA])}
    context = {'proyecto': proyecto, 'sprint': sprint, 'backlog': backlog,
               'filename': 'Reporte - Sprint Backlog'}
    return render_to_pdf(request, 'sgp/reporte-sprint-backlog.html', context=context)


def reporte_us_prioridad(request, proyecto_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
    backlog = proyecto.sprint_activo.sprint_backlog.all().order_by('prioridad')
    for user_story in backlog:
        user_story.desarrollador = proyecto.sprint_activo.equipo.filter(
            participasprint__user_stories__in=[user_story]).first().nombre_completo
    context = {'proyecto': proyecto, 'backlog': backlog,
               'filename': 'Reporte - US - Prioridad'}
    return render_to_pdf(request, 'sgp/reporte-us-prioridad.html', context=context)
