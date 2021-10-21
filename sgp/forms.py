"""
Los formularios son un método de intercambio de información entre la aplicación
y el usuario. Cada formulario corresponde a un modelo, por lo que un formulario
en blanco permite instanciarlo mientras que uno ya ligado a una instancia
permite modificarla.

Para todos los formularios, los argumentos de los constructores son los mismos
que para su clase base.
"""

import datetime

from django import forms
from django.forms import ModelForm
from django.utils import timezone
from guardian.shortcuts import assign_perm, remove_perm, get_perms_for_model

from .models import User, Proyecto, Role, Sprint, UserStory, Comentario, ParticipaSprint


class UserForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de administración, donde se pueden modificar
    propiedades o permisos.

    Posee campos correspondientes a los atributos de nombre, apellido, y correo
    electrónico. Además, posee tres campos adicionales para los permisos de
    creación de proyecto, administración de usuarios, y auditación del sistema.

    **Fecha:** 24/08/21

    **Artefacto:** módulo de seguridad

    |
    """
    email = forms.CharField(disabled=True)
    crear_proyecto = forms.BooleanField(required=False)
    administrar = forms.BooleanField(required=False)
    auditar = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for permiso in self.Meta.fields:
            self.fields[permiso].initial = self.instance.has_perm('sgp.' + permiso)

    def save(self, commit=True):
        for permiso in ['crear_proyecto', 'administrar', 'auditar']:
            if self.cleaned_data[permiso]:
                assign_perm('sgp.' + permiso, self.instance)
            else:
                remove_perm('sgp.' + permiso, self.instance)
        super(UserForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'crear_proyecto', 'administrar', 'auditar']


class ProyectoForm(ModelForm):
    """
    Corresponde al modelo Proyecto. Este formulario se muestra en las páginas
    de creación y de edición de proyectos.

    Posee campos correspondientes a los atributos de nombre, descripción, fecha
    de inicio, fecha de fin, y duración predeterminada de los sprints.

    **Fecha:** 06/09/21

    **Artefacto:** módulo de proyecto
    """
    fecha_inicio = forms.DateField(label="Fecha de inicio",
                                   error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    fecha_fin = forms.DateField(label="Fecha de fin",
                                error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    duracion_sprint = forms.IntegerField(label="Duración de los sprints (en días)", min_value=0)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            if self.instance.estado == Proyecto.Estado.INICIADO:
                self.fields['fecha_inicio'].initial = self.instance.fecha_inicio
                self.fields['fecha_inicio'].disabled = True

    def clean(self):
        """
        Valida las fechas y la duración predeterminada del sprint.

        Para que el formulario sea válido, las fechas no pueden haber ocurrido
        en el pasado y la duración del sprint debe ser positiva. Además, debe
        haber suficiente tiempo entre la fecha de inicio la fecha de fin para
        realizar al menos un sprint.

        |
        """
        cleaned_data = super(ModelForm, self).clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        duracion_sprint = cleaned_data.get('duracion_sprint')

        if fecha_inicio and fecha_inicio < timezone.localdate():
            self.add_error('fecha_inicio', 'La fecha de inicio no puede ser en el pasado.')
            fecha_inicio = None
        if fecha_fin and fecha_fin < timezone.localdate():
            self.add_error('fecha_fin', 'La fecha de fin no puede ser en el pasado.')
            fecha_fin = None
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_fin', 'La fecha de fin debe ser después de la fecha de inicio.')
            fecha_inicio = None
            fecha_fin = None
        if fecha_inicio and fecha_fin and duracion_sprint and \
                fecha_inicio + datetime.timedelta(days=duracion_sprint) > fecha_fin:
            self.add_error('duracion_sprint', 'El proyecto debe tener tiempo para al menos un sprint.')

        return cleaned_data

    class Meta:
        model = Proyecto
        fields = ('nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion_sprint')


class RoleForm(ModelForm):
    """
    Corresponde al modelo Role. Se muestra un formulario por cada rol dentro
    de la página de administración de roles, donde se pueden crear nuevos
    roles, modificar sus permisos, o eliminarlos.

    Posee un campo correspondiente al nombre. Además, posee un campo adicional
    para cada permiso posible dentro de un proyecto. Estos son cuatro:
    administración de equipo, gestión de proyecto, modificación de la pila de
    producto, y desarrollo.

    Posee un parámetro para el rol actual del usuario. Este rol no podrá ser
    eliminado ni se le podrá revocar el permiso de administración de equipo,
    para evitar una situación en la que no se pueda modificar la configuración
    del proyecto.

    **Fecha:** 02/09/21

    **Artefacto:** módulo de proyecto

    :param rol_actual: El rol actual del usuario.
    :type rol_actual: Role

    |
    """
    administrar_equipo = forms.BooleanField(required=False)
    gestionar_proyecto = forms.BooleanField(required=False)
    pila_producto = forms.BooleanField(required=False)
    desarrollo = forms.BooleanField(required=False)

    def __init__(self, *args, rol_actual, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
            for perm in permisos:
                self.fields[perm.codename].initial = self.instance.permisos.filter(id=perm.id).exists()
            self.rol_actual = rol_actual
            if self.instance == rol_actual:
                self.fields['administrar_equipo'].disabled = True

    def save(self, commit=True):
        permisos = get_perms_for_model(Proyecto).exclude(codename='vista')
        if self.instance.pk:
            if self.instance == self.rol_actual:
                self.cleaned_data['administrar_equipo'] = True
            for perm in permisos:
                if self.cleaned_data[perm.codename]:
                    self.instance.asignar_permiso(perm)
                else:
                    self.instance.quitar_permiso(perm)
            super(RoleForm, self).save(commit)
        else:
            super(RoleForm, self).save(commit)
            for perm in permisos:
                if self.cleaned_data[perm.codename]:
                    self.instance.permisos.add(perm)

    class Meta:
        model = Role
        fields = ['nombre', 'administrar_equipo', 'gestionar_proyecto', 'pila_producto', 'desarrollo']


class UserRoleForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de administrar equipo, donde muestra la información
    principal y se puede asignar un rol a cada usuario.

    Posee campos desactivados correspondientes a los atributos de nombre,
    apellido, y correo electrónico. Además, posee un campo activado para
    seleccionar el rol del usuario.

    Posee un parámetro para el usuario actual. Este usuario no se podrá asignar
    un rol sin el permiso de administración de equipo para evitar una situación
    donde no pueda acceder a la vista de administración de equipo.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    :param proyecto_actual: El proyecto cuyos roles se muestran.
    :param usuario_actual: El usuario accediendo a la vista.
    :type proyecto_actual: Proyecto
    :type usuario_actual: User
    """

    borrar = forms.BooleanField(required=False)

    def __init__(self, *args, usuario_actual, proyecto_actual, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)

        if self.instance == usuario_actual:
            perm = get_perms_for_model(Proyecto).get(codename='administrar_equipo')
            queryset = Role.objects.filter(proyecto=proyecto_actual, permisos__in=[perm])
        else:
            queryset = Role.objects.filter(proyecto=proyecto_actual)

        self.fields['rol'] = forms.ModelChoiceField(
            queryset=queryset,
            initial=self.instance.participa_set.get(proyecto=proyecto_actual).rol
        )
        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['email'].disabled = True

        self.usuario_actual = usuario_actual
        self.proyecto_actual = proyecto_actual

    def clean(self):
        """
        Además de validar los datos, se asegura de que al marcar un formulario
        para borrarlo, esto quite al usuario del equipo en vez de eliminarlo.

        |
        """
        cleaned_data = super(ModelForm, self).clean()
        if cleaned_data.get('borrar'):
            self.proyecto_actual.quitar_rol(self.instance)
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get('rol'):
            self.proyecto_actual.asignar_rol(self.instance, self.cleaned_data['rol'].nombre)
        super(UserRoleForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'borrar']


class AgregarMiembroForm(forms.Form):
    """
    Permite seleccionar un usuario que no forma parte del equipo del proyecto y
    un rol existente dentro del proyecto. Agrega al usuario al equipo con ese
    rol.

    **Fecha:** 18/09/21

    **Artefacto:** módulo de proyecto

    :param proyecto: El proyecto al que se le agrega un usuario.
    :type proyecto: Proyecto

    |
    """

    def __init__(self, *args, proyecto, **kwargs):
        self.proyecto = proyecto
        super().__init__(*args, **kwargs)
        self.fields['usuarios'] = forms.ModelChoiceField(
            queryset=User.objects.exclude(participa__proyecto=proyecto).exclude(pk='AnonymousUser'))
        self.fields['roles'] = forms.ModelChoiceField(
            queryset=Role.objects.filter(proyecto=proyecto))

    def save(self):
        self.proyecto.asignar_rol(self.cleaned_data['usuarios'], self.cleaned_data['roles'].nombre)


class UploadFileForm(forms.Form):
    """
    Permite enviar archivos al servidor.

    Posee un solo campo, el cual recibe el archivo.

    **Fecha:** 07/09/21

    |
    """
    archivo = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class UserStoryForm(ModelForm):
    """
    Corresponde al modelo UserStory. Este formulario se muestra en las páginas
    de creación y de edición de user stories.

    Posee campos correspondientes a los atributos de nombre, descripción,
    prioridad, y horas estimadas. Los campos de nombre y descripción solo son
    accesibles a usuarios con el permiso de pila de producto, mientras que el
    campo de costo estimada solo es accesible a usuarios con el permiso de
    gestión de proyecto. El campo de proridad es accesible para cualquiera.

    **Fecha:** 26/09/21

    **Artefacto:** Módulo de desarrollo

    :param usuario: El usuario accediendo al formulario.
    :param proyecto: El proyecto al que pertenece el user story.
    :type usuario: Usuario
    :type proyecto: Proyecto

    |
    """

    def __init__(self, *args, usuario=None, proyecto=None, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        if usuario:
            if not usuario.has_perm('gestionar_proyecto', proyecto):
                self.fields.pop('horas_estimadas')
            else:
                self.fields['horas_estimadas'] = forms.IntegerField(label="Costo estimado (en horas)",
                                                                    min_value=0, required=False)
            if not usuario.has_perm('pila_producto', proyecto):
                self.fields.pop('nombre')
                self.fields.pop('descripcion')

    def save(self, commit=True):
        self.instance.proyecto = self.proyecto
        if not self.instance.pk:
            self.instance.numero = UserStory.objects.filter(proyecto=self.proyecto).count() + 1
        super(ModelForm, self).save(commit)

    class Meta:
        model = UserStory
        fields = ('nombre', 'descripcion', 'prioridad', 'horas_estimadas')


class ComentarioForm(ModelForm):
    """
    Corresponde al modelo Comentario. Este formulario se muestra en la página
    principal de cada user story, y permite agregarle comentarios.

    Posee un solo campo, el cual lee el texto del comentario.

    **Fecha:** 28/09/21

    **Artefacto:** Módulo de desarrollo

    |
    """
    def __init__(self, *args, usuario=None, user_story=None, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.usuario = usuario
        self.user_story = user_story

    def save(self, commit=True):
        self.instance.user_story = self.user_story
        self.instance.autor = self.usuario
        self.instance.fecha = timezone.localdate()
        super(ModelForm, self).save(commit)

    class Meta:
        model = Comentario
        fields = ('texto',)


class SprintForm(ModelForm):
    """
    Corresponde al modelo Sprint. Este formulario se muestra en las páginas de
    creación y de edición de sprints.

    Posee campos correspondientes a los atributos de nombre, descripcion,
    duracion, fecha de inicio, y fecha de fin. El campo de fecha de fin se
    encuentra desactivado, por lo que esta fecha es calculada a partir de la
    fecha de inicio y la duración.

    **Fecha:** 24/09/21

    **Artefacto:** Módulo de desarrollo

    :param proyecto: El proyecto al que pertenece el sprint.
    :type proyecto: Proyecto
    """
    duracion = forms.IntegerField(label="Duración (en días)", min_value=0,
                                  widget=forms.NumberInput(attrs={'onchange': 'actualizar_fecha_fin()'}))
    fecha_inicio = forms.DateField(label="Fecha de inicio",
                                   widget=forms.DateInput(attrs={'onchange': 'actualizar_fecha_fin()'}),
                                   error_messages={'invalid': 'La fecha debe estar en formato dd/mm/aaaa.'})
    fecha_fin = forms.DateField(label="Fecha de fin", disabled=True, required=False)

    def __init__(self, *args, proyecto=None, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.proyecto = proyecto
        if not self.instance.pk:
            self.fields['duracion'].initial = proyecto.duracion_sprint
        else:
            self.fields['duracion'].initial = (self.instance.fecha_fin - self.instance.fecha_inicio).days

    def clean(self):
        """
        Verifica que el campo de fecha de inicio sea una fecha en el presente o
        futuro, y calcula la fecha de inicio a partir de esta primera fecha y
        la duración del sprint.

        |
        """
        cleaned_data = super(ModelForm, self).clean()

        fecha_inicio = cleaned_data.get('fecha_inicio')
        duracion = cleaned_data.get('duracion')

        if fecha_inicio and fecha_inicio < timezone.localdate():
            self.add_error('fecha_inicio', 'La fecha de inicio no puede ser en el pasado.')
            fecha_inicio = None
        if fecha_inicio and duracion:
            cleaned_data['fecha_fin'] = fecha_inicio + datetime.timedelta(days=duracion)

        return cleaned_data

    def save(self, commit=True):
        self.instance.proyecto = self.proyecto
        super(ModelForm, self).save(commit)

    class Meta:
        model = Sprint
        fields = ('nombre', 'descripcion', 'duracion', 'fecha_inicio', 'fecha_fin')


class BacklogForm(ModelForm):
    """
    Corresponde al modelo UserStory. Se muestra un formulario por cada user
    story dentro de la página de sprint backlog, donde muestra la información
    principal y se pueden modificar parámetros de los user stories.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    :param sprint: El sprint cuyos user stories se muestran.
    :type sprint: Sprint
    """

    borrar = forms.BooleanField(required=False)

    def __init__(self, *args, proyecto, sprint, **kwargs):
        super(BacklogForm, self).__init__(*args, **kwargs)

        self.sprint = sprint

        self.fields['n'] = forms.CharField(initial='US-'+str(self.instance.numero), disabled=True)
        self.fields['nombre'].disabled = True
        self.fields['prioridad'].required = False
        self.fields['horas_estimadas'].required = False
        queryset = sprint.equipo.filter(participa__rol__permisos__codename__in=['desarrollo'])
        initial = sprint.equipo.filter(participasprint__user_stories__in=[self.instance]).first()
        self.nombre_desarrollador = str(initial)
        self.fields['desarrollador'] = forms.ModelChoiceField(queryset=queryset, initial=initial, required=False)

    def clean(self):
        """
        Se asegura de que al marcar un formulario para borrarlo, esto quite al
        usuario del equipo en vez de eliminarlo.

        |
        """
        cleaned_data = super(ModelForm, self).clean()
        if not cleaned_data.get('prioridad'):
            cleaned_data['prioridad'] = self.instance.prioridad
        if not cleaned_data.get('horas_estimadas'):
            cleaned_data['horas_estimadas'] = self.instance.horas_estimadas
        if cleaned_data.get('borrar'):
            p = ParticipaSprint.objects.filter(sprint=self.sprint, user_stories__in=[self.instance]).first()
            if p:
                p.user_stories.remove(self.instance)
                p.save()
            if self.cleaned_data.get('desarrollador'):
                cleaned_data.pop('desarrollador')
            self.instance.sprint = None
            self.instance.save()
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get('horas'):
            self.participa.horas_diarias = self.cleaned_data['horas']
            self.participa.save()

        # actualiza el desarrollador del user story
        p = ParticipaSprint.objects.filter(sprint=self.sprint, user_stories__in=[self.instance]).first()
        if p:
            p.user_stories.remove(self.instance)
            p.save()
        if self.cleaned_data.get('desarrollador'):
            p = self.sprint.participasprint_set.get(usuario=self.cleaned_data['desarrollador'])
            p.user_stories.add(self.instance)
            p.save()
        super(BacklogForm, self).save(commit)

    class Meta:
        model = UserStory
        fields = ['nombre', 'prioridad', 'horas_estimadas']


class AgregarUserStoryForm(forms.Form):
    """
    Permite seleccionar un user story que no forma parte de ningún sprint.
    Agrega el user story al sprint con esa estimación.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    :param proyecto: El proyecto del cual se obtienen los user stories.
    :param sprint: El sprint al que se le agrega un user story.
    :type proyecto: Proyecto
    :type sprint: Sprint

    |
    """

    def __init__(self, *args, proyecto, sprint, **kwargs):
        self.sprint = sprint
        self.proyecto = proyecto
        super().__init__(*args, **kwargs)
        self.fields['user_story'] = forms.ModelChoiceField(
            queryset=proyecto.product_backlog.filter(sprint__isnull=True, estado=UserStory.Estado.PENDIENTE),
            required=True)
        self.fields['usuario'] = forms.ModelChoiceField(queryset=sprint.equipo.all(), required=False)

    def save(self):
        # agrega el user story al sprint backlog
        user_story = self.cleaned_data['user_story']
        user_story.sprint = self.sprint
        self.sprint.sprint_backlog.add(user_story)

        # asigna el user story al desarrollador
        if self.cleaned_data.get('usuario'):
            p = self.sprint.participasprint_set.get(usuario=self.cleaned_data['usuario'])
            p.user_stories.add(user_story)
            p.save()


class UserSprintForm(ModelForm):
    """
    Corresponde al modelo User. Se muestra un formulario por cada usuario
    dentro de la página de equipo de sprint, donde muestra la información
    principal y se pueden cargar las horas disponibles de cada usuario.

    Posee campos desactivados correspondientes a los atributos de nombre,
    apellido, y correo electrónico. Además, posee un campo activado para
    las horas disponibles.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    :param sprint: El sprint cuyos roles se muestran.
    :type sprint: Sprint
    """

    borrar = forms.BooleanField(required=False)

    def __init__(self, *args, sprint, **kwargs):
        super(UserSprintForm, self).__init__(*args, **kwargs)

        self.sprint = sprint
        self.participa = ParticipaSprint.objects.get(sprint=sprint, usuario=self.instance)

        self.fields['nombre'].disabled = True
        self.fields['apellido'].disabled = True
        self.fields['email'].disabled = True
        self.fields['horas'] = forms.IntegerField(min_value=1, required=False,
                                                  initial=self.participa.horas_diarias)

    def clean(self):
        """
        Se asegura de que al marcar un formulario para borrarlo, esto quite al
        usuario del equipo en vez de eliminarlo.

        |
        """
        cleaned_data = super(ModelForm, self).clean()
        if cleaned_data.get('borrar'):
            self.participa.delete()
            if cleaned_data.get('horas'):
                cleaned_data.pop('horas')
        return cleaned_data

    def save(self, commit=True):
        if self.cleaned_data.get('horas'):
            self.participa.horas_diarias = self.cleaned_data['horas']
            self.participa.save()
        super(UserSprintForm, self).save(commit)

    class Meta:
        model = User
        fields = ['nombre', 'apellido', 'email', 'borrar']


class AgregarDesarrolladorForm(forms.Form):
    """
    Permite seleccionar un desarrollador que no forma parte del equipo del
    sprint y una disponibilidad de horas. Agrega al usuario al equipo con ese
    número de horas disponibles.

    **Fecha:** 30/09/21

    **Artefacto:** módulo de desarrollo

    :param proyecto: El proyecto del cual se obtienen los usuarios.
    :param sprint: El sprint al que se le agrega un usuario.
    :type proyecto: Proyecto
    :type sprint: Sprint

    |
    """

    def __init__(self, *args, proyecto, sprint, **kwargs):
        self.sprint = sprint
        super().__init__(*args, **kwargs)
        queryset = proyecto.equipo \
            .filter(participa__rol__permisos__codename__in=['desarrollo']) \
            .exclude(user_id__in=sprint.equipo.all())
        self.fields['usuario'] = forms.ModelChoiceField(queryset=queryset, required=True)
        self.fields['horas'] = forms.IntegerField(min_value=1, required=True)

    def save(self):
        if not self.cleaned_data.get('horas'):
            self.cleaned_data['horas'] = 0
        ParticipaSprint.objects.create(sprint=self.sprint, usuario=self.cleaned_data['usuario'],
                                       horas_diarias=self.cleaned_data['horas'])
