"""
Los modelos corresponden a tablas en la base de datos, y cada instancia
representa una entrada. A continuación se documentan los campos principales y
los métodos adicionales de los modelos en uso por la aplicación.
"""
import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from guardian.shortcuts import assign_perm, get_perms_for_model, remove_perm


class UserManager(BaseUserManager):
    def create_user(self, user_id, email, nombre, apellido):
        user = self.model(
            user_id=user_id,
            email=email,
            nombre=nombre,
            apellido=apellido)
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, user_id, email, nombre, apellido):
        user = self.model(
            user_id=user_id,
            email=email,
            nombre=nombre,
            apellido=apellido)
        user.is_superuser = True
        user.set_unusable_password()
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Describe a un usuario. Su información personal se obtiene a partir de su
    cuenta de Google cuando este inicia sesión por primera vez.

    **Fecha:** 21/08/21

    **Artefacto:** Módulo de seguridad
    """
    user_id = models.CharField(max_length=150, unique=True, primary_key=True)
    """Número de identidad de la cuenta de Google de este usuario. Se utiliza
     como llave primaria."""

    email = models.EmailField(max_length=254, unique=True)
    """Correo electrónico del usuario, obtenido a partir de su cuenta de Google."""

    nombre = models.CharField(max_length=60)
    """Almacena el nombre del usuario, obtenido a partir de su cuenta de Google."""

    apellido = models.CharField(max_length=60)
    """Almacena los apellidos del usuario, obtenidos a partir de su cuenta de Google."""

    fecha_registro = models.DateTimeField("Fecha de registro", auto_now_add=True)
    """Almacena la fecha en la que el usuario fue registrado.
    
    |"""

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido']

    class Meta:
        default_permissions = ()
        permissions = [
            ('administrar', 'Permite asignar permisos a los usuarios'),
            ('auditar', 'Permite auditar la información del sistema'),
            ('crear_proyecto', 'Permite crear proyectos nuevos')
        ]

    def __str__(self):
        return str(self.nombre) + ' ' + str(self.apellido) + ' (' + str(self.email) + ')'

    @property
    def nombre_completo(self):
        return self.nombre + ' ' + self.apellido


class Proyecto(models.Model):
    """
    Describe un proyecto. Este debe ser creado por un usuario con el permiso
    apropiado.

    **Fecha:** 26/08/21

    **Artefacto:** Módulo de proyecto
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'P', 'Pendiente'
        INICIADO = 'I', 'Iniciado'
        FINALIZADO = 'F', 'Finalizado'
        CANCELADO = 'C', 'Cancelado'
    """Contiene los estados posibles del proyecto."""

    nombre = models.CharField(max_length=200)
    """Título del proyecto."""

    descripcion = models.TextField(blank=True, default='')
    """Descripción del proyecto."""

    creador = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="creador_set")
    """Almacena el usuario que creó el proyecto. Si el usuario es eliminado, el
     campo queda nulo."""

    duracion_sprint = models.IntegerField("Duración de los sprints", blank=True, null=True)
    """Indica la duración en días de cada sprint dentro del proyecto. Opcional."""

    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    """Almacena la hora a la que se creó el proyecto."""

    fecha_inicio = models.DateField("Fecha de inicio", null=True)
    """Si el proyecto aún no ha iniciado, almacena una hora tentativa en la que
    se planea iniciarlo. Una vez que este inicia, almacena la hora en la que 
    inició."""

    fecha_fin = models.DateField("Fecha de fin", auto_now_add=False, auto_now=False, null=True)
    """Si el proyecto aún no ha terminado, almacena una hora tentativa en la que
    se planea terminarlo. Una vez que este acabe, almacena la hora en la que 
    acabó."""

    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)
    """Indica en qué estado se encuentra el proyecto. Cuando este se crea, el
    estado predeterminado es pendiente."""

    equipo = models.ManyToManyField(User, through='Participa', related_name="equipo_set")
    """Indica qué usuarios forman parte del equipo de este proyecto. Para esto
    se utiliza la relación Participa, la cual almacena el rol al que el usuario 
    pertenece dentro del proyecto."""

    def asignar_rol(self, user, role):
        """
        Asigna a un usuario un rol dentro del proyecto, otorgandole todos los
        permisos que esto implica. Si el usuario ya tenía un rol anterior,
        revoca todos los permisos que le correspondían.

        :param user: El usuario al que se le asignará el rol.
        :param role: El nombre del rol que será asignado.
        :type user: User
        :type role: string
        """
        if self.equipo.filter(user_id=user.user_id).exists():
            self.quitar_rol(user)
        else:
            assign_perm('vista', user, self)

        participa = Participa.objects.create(usuario=user, proyecto=self, rol=self.role_set.get(nombre=role))
        for perm in participa.rol.permisos.all():
            assign_perm(perm.codename, user, self)

    def quitar_rol(self, user):
        """
        Revoca a un usuario un rol dentro del proyecto, quitandole todos los
        permisos que este incluye.

        :param user: El usuario al que se le revocará el rol.
        :type user: User
        """
        participa = user.participa_set.get(proyecto=self)
        for perm in participa.rol.permisos.all():
            remove_perm(perm.codename, user, self)
        participa.delete()

    def crear_rol(self, nombre, permisos):
        """
        Crea un rol dentro del proyecto.

        :param nombre: El nombre del rol a ser creado.
        :param permisos: Los permisos del rol a ser creado.
        :type nombre: string
        :type permisos: [string]"""
        rol = Role.objects.create(nombre=nombre, proyecto=self)
        perms = get_perms_for_model(Proyecto)
        for perm in permisos:
            rol.permisos.add(perms.get(codename=perm))
            rol.permisos.add(perms.get(codename=perm))
            rol.permisos.add(perms.get(codename=perm))

    def crear_roles_predeterminados(self):
        """
        Crea los roles de scrum master, product owner, desarrollador, e
        interesado dentro del proyecto con sus respectivos permisos.

        |
        """
        self.crear_rol('Scrum master', ['administrar_equipo', 'gestionar_proyecto'])
        self.crear_rol('Product owner', ['pila_producto'])
        self.crear_rol('Desarrollador', ['desarrollo'])
        self.crear_rol('Interesado', [])

    def validar_inicio(self):
        """
        Verifica si el proyecto puede iniciar y retorna un diccionario con
        dos listas: errores y advertencias. Los mensajes en la lista errores
        son lo suficientemente graves para que el proyecto no pueda iniciar,
        mientras que aquellos en la lista advertencias pueden ser ignorados.
        """
        msg = {'errores': [], 'advertencias': []}

        # verifica que ya sea la fecha de inicio
        if timezone.localdate() < self.fecha_inicio:
            msg['advertencias'].append('Todavía no ha llegado la fecha de inicio.')
        elif self.fecha_inicio < timezone.localdate():
            msg['advertencias'].append('Ya ha pasado la fecha de inicio.')

        # verifica que haya tiempo para al menos un sprint
        if self.fecha_fin < timezone.localdate():
            msg['errores'].append('La fecha de fin se encuentra en el pasado.')
        elif timezone.localdate()+datetime.timedelta(days=self.duracion_sprint) > self.fecha_fin:
            msg['errores'].append('No hay suficiente tiempo para realizar al menos un sprint.')

        # verifica que existe al menos un usuario con cada permiso
        for perm, desc in Proyecto._meta.permissions:
            for user in self.equipo.all():
                if user.has_perm(perm, self):
                    break
            else:
                msg['errores'].append('Falta al menos un usuario con el permiso de '+desc+'.')

        return msg

    def validar_fin(self):
        """
        Verifica si el proyecto puede finalizar y retorna un diccionario con
        dos listas: errores y advertencias. Los mensajes en la lista errores
        son lo suficientemente graves para que el proyecto no pueda iniciar,
        mientras que aquellos en la lista advertencias pueden ser ignorados.
        """
        msg = {'errores': [], 'advertencias': []}

        # verifica que ya sea la fecha de fin
        if timezone.localdate() < self.fecha_fin:
            msg['advertencias'].append('Todavía no ha llegado la fecha de fin.')
        elif self.fecha_fin < timezone.localdate():
            msg['advertencias'].append('Ya ha pasado la fecha de fin.')

        # verifica que todos los sprints hayan terminado
        if self.sprint_activo:
            msg['errores'].append('Existe un sprint activo.')
        if self.sprint_pendiente:
            msg['errores'].append('Existe un sprint pendiente.')

        # verifica que todos los user stories se encuentren completos o cancelados
            if self.product_backlog.filter(estado=UserStory.Estado.PENDIENTE).first():
                msg['errores'].append('Existen user stories pendientes.')

        return msg

    @property
    def sprint_activo(self):
        """Retorna el sprint activo del proyecto, si este existe."""
        return self.sprint_set.filter(estado=Sprint.Estado.INICIADO).first()

    @property
    def sprint_pendiente(self):
        """Retorna el sprint pendiente del proyecto, si este existe."""
        return self.sprint_set.filter(estado=Sprint.Estado.PENDIENTE).first()

    @property
    def sprints_finalizados(self):
        """Retorna el conjunto de sprints pendientes del proyecto."""
        return self.sprint_set.filter(estado=Sprint.Estado.FINALIZADO)

    class Meta:
        default_permissions = ()
        permissions = [
            ('administrar_equipo', 'administración de equipo'),
            ('gestionar_proyecto', 'gestión de proyecto'),
            ('pila_producto', 'gestión de pila de producto'),
            ('desarrollo', 'desarrollo'),
            ('vista', 'acceso al proyecto'),
        ]

    def __str__(self):
        return self.nombre


class Role(models.Model):
    """
    Describe un rol dentro de un proyecto, con todos los permisos que lo
    acompañan.

    **Fecha:** 02/09/21

    **Artefacto:** Módulo de proyecto
    """
    nombre = models.CharField(max_length=100)
    """Nombre del rol."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    """Proyecto al que el rol pertenece."""

    permisos = models.ManyToManyField(Permission)
    """Permisos que otorga el rol con respecto al proyecto."""

    def asignar_permiso(self, permiso):
        """Asigna un permiso al rol y a todos los usuarios que forman parte de
        él."""
        self.permisos.add(permiso)
        for p in self.participa_set.select_related('usuario'):
            assign_perm(permiso, p.usuario, self.proyecto)

    def quitar_permiso(self, permiso):
        """Quita un permiso al rol y a todos los usuarios que forman parte de
        él.

        |"""
        self.permisos.remove(permiso)
        for p in self.participa_set.select_related('usuario'):
            remove_perm(permiso, p.usuario, self.proyecto)

    def __str__(self):
        return self.nombre


class Participa(models.Model):
    """
    Describe la relación de pertenencia de un usuario dentro de un rol.

    **Fecha:** 02/09/21

    **Artefacto:** Roles de proyecto
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    """Usuario que pertenece al rol."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    """Proyecto al que pertenece el rol."""

    rol = models.ForeignKey(Role, on_delete=models.CASCADE)
    """Rol al que pertenece el usuario.
    
    |"""


class Sprint(models.Model):
    """
    Describe un sprint. Este debe ser creado por un usuario con el permiso
    apropiado.

    **Fecha:** 24/09/21

    **Artefacto:** Módulo de desarrollo
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'P', 'Pendiente'
        INICIADO = 'I', 'Iniciado'
        FINALIZADO = 'F', 'Finalizado'
    """Contiene los estados posibles del sprint."""

    nombre = models.CharField(max_length=200)
    """Título del sprint."""

    descripcion = models.TextField(blank=True, default='')
    """Descripción del sprint."""

    fecha_inicio = models.DateField("Fecha de inicio")
    """Si el sprint aún no ha iniciado, almacena una hora tentativa en la que
    se planea iniciarlo. Una vez que este inicia, almacena la hora en la que 
    inició."""

    fecha_fin = models.DateField("Fecha de fin")
    """Si el sprint aún no ha terminado, almacena una hora tentativa en la que
    se planea terminarlo. Una vez que este acabe, almacena la hora en la que 
    acabó."""

    fecha_fin_original = models.DateField(null=True)
    """Almacena la fecha en la que se originalmente se planeó terminar el
    sprint. Esta información es necesaria para generar el burndown chart."""

    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)
    """Indica en qué estado se encuentra el sprint. Cuando este se crea, el
    estado predeterminado es pendiente."""

    equipo = models.ManyToManyField(User, through='ParticipaSprint')
    """Indica qué usuarios participan de este sprint."""

    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    """Indica a qué proyecto pertenece el sprint."""

    def validar_inicio(self):
        """
        Verifica si el sprint puede iniciar y retorna un diccionario con
        dos listas: errores y advertencias. Los mensajes en la lista errores
        son lo suficientemente graves para que el sprint no pueda iniciar,
        mientras que aquellos en la lista advertencias pueden ser ignorados.
        """
        msg = {'errores': [], 'advertencias': []}

        # verifica que el proyecto ya haya iniciado y no haya otro sprint en curso
        if self.proyecto.estado == Proyecto.Estado.PENDIENTE:
            msg['errores'].append('El proyecto aún no ha iniciado.')
        elif self.proyecto.sprint_activo:
            msg['errores'].append('Ya existe un sprint en curso.')
            if self.fecha_inicio < self.proyecto.sprint_activo.fecha_fin:
                msg['advertencias'].append('El inicio de este sprint se solapa con el fin del sprint activo.')

        # verifica que ya sea la fecha de inicio
        if timezone.localdate() < self.fecha_inicio:
            msg['advertencias'].append('Todavía no ha llegado la fecha de inicio.')
        elif self.fecha_inicio < timezone.localdate():
            msg['advertencias'].append('Ya ha pasado la fecha de inicio.')

        # verifica que las fechas de inicio y de fin entren en el proyecto
        if self.fecha_inicio < self.proyecto.fecha_inicio:
            msg['advertencias'].append('El sprint no puede iniciar antes que el proyecto.')
        elif self.fecha_fin > self.proyecto.fecha_fin:
            msg['advertencias'].append('El sprint no puede terminar después que el proyecto.')

        # verifica que haya al menos un desarrollador
        if not self.equipo.first():
            msg['errores'].append('El sprint necesita al menos un desarrollador.')

        # verifica que exista al menos un user story
        if not self.sprint_backlog.first():
            msg['errores'].append('El sprint necesta al menos un user story.')

        # verifica que cada user story tenga un desarrollador asociado
        for us in self.sprint_backlog.all():
            if not ParticipaSprint.objects.filter(sprint=self, user_stories__in=[us]).exists():
                msg['errores'].append('US-'+str(us.numero)+' no tiene un desarrollador asociado.')

        # verifica que cada user story tenga un costo estimado
        for us in self.sprint_backlog.all():
            if not us.horas_estimadas:
                msg['errores'].append('US-'+str(us.numero)+' aún no tiene un costo estimado en horas.')

        # verifica que la capacidad del equipo sea suficiente para el costo del backlog
        if self.capacidad_equipo < self.costo_backlog:
            msg['advertencias'].append('El costo total del backlog es mayor que la capacidad del equipo.')

        return msg

    def validar_fin(self):
        """
        Verifica si el sprint puede finalizar y retorna un diccionario con
        dos listas: errores y advertencias. Los mensajes en la lista errores
        son lo suficientemente graves para que el sprint no pueda iniciar,
        mientras que aquellos en la lista advertencias pueden ser ignorados.
        """
        msg = {'errores': [], 'advertencias': []}

        # verifica que ya sea la fecha de fin
        if timezone.localdate() < self.fecha_fin:
            msg['advertencias'].append('Todavía no ha llegado la fecha de fin.')
        elif self.fecha_fin < timezone.localdate():
            msg['advertencias'].append('Ya ha pasado la fecha de fin.')

        # verifica que la fecha de fin sea válida
        if self.fecha_fin > self.proyecto.fecha_fin:
            msg['advertencias'].append('El sprint no puede terminar después que el proyecto.')

        for user_story in self.sprint_backlog.all():
            if user_story.estado != UserStory.Estado.FINALIZADO:
                msg['advertencias'].append('El sprint tiene user stories sin terminar.')

        return msg

    @property
    def capacidad_diaria(self):
        """Calcula el número de horas disponibles de los miembros del sprint en un día."""

        capacidad = 0
        for miembro in self.participasprint_set.all():
            capacidad = capacidad + miembro.horas_diarias
        return capacidad

    @property
    def capacidad_equipo(self):
        """Calcula el número de horas disponibles de los miembros del sprint en total."""

        return self.capacidad_diaria * (self.fecha_fin - self.fecha_inicio).days

    @property
    def costo_backlog(self):
        """Calcula el costo total en horas del sprint backlog.

        |"""

        costo = 0
        for us in self.sprint_backlog.all():
            if us.horas_estimadas:
                costo = costo + us.horas_estimadas
        return costo

    def __str__(self):
        return self.nombre


class UserStory(models.Model):
    """
    Describe un user story. Este pertenece a un Proyecto y contiene un
    conjunto de instancias de Comentario.

    **Fecha:** 26/09/21

    **Artefacto:** Módulo de desarrollo
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'P', 'Pendiente'
        INICIADO = 'I', 'Iniciado'
        FASE_DE_QA = 'Q', 'Q&A'
        FINALIZADO = 'F', 'Finalizado'
        CANCELADO = 'C', 'Cancelado'
    """Contiene los estados posibles del user story."""

    numero = models.IntegerField()
    """Número de user story dentro del proyecto."""

    nombre = models.CharField(max_length=200)
    """Título del user story."""

    descripcion = models.TextField(blank=True, default='')
    """Descripción del user story."""

    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)
    """Indica en qué estado se encuentra el user story. Cuando este se crea, el
    estado predeterminado es pendiente."""

    prioridad = models.IntegerField(choices=[
        (1, 'Muy Alta'),
        (2, 'Alta'),
        (3, 'Normal'),
        (4, 'Baja'),
        (5, 'Muy baja'),
    ], default=3)
    """Indica la prioridad del user story en una escala del 1 al 5, donde 1
    representa la prioridad máxima."""

    horas_estimadas = models.IntegerField(null=True)
    """Número de horas estimadas que tomará completar el stream"""

    horas_trabajadas = models.IntegerField(default=0)
    """Número de horas que se han trabajado en el user story"""

    proyecto = models.ForeignKey(Proyecto, related_name='product_backlog', on_delete=models.CASCADE)
    """Indica a qué proyecto pertenece el user story."""

    sprint = models.ForeignKey(Sprint, related_name='sprint_backlog', on_delete=models.SET_NULL, null=True)
    """Indica a qué sprint pertenece el user story.
    
    |"""

    def __str__(self):
        return self.nombre


class Comentario(models.Model):
    """
    Describe un comentario en un user story.

    **Fecha:** 26/09/21

    **Artefacto:** Módulo de desarrollo
    """

    texto = models.TextField()
    """Contenido del comentario"""

    fecha = models.DateTimeField(auto_now_add=True)
    """Fecha en la que se realizó el comentario"""

    autor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    """Usuario que agregó el comentario"""

    user_story = models.ForeignKey(UserStory, on_delete=models.CASCADE)
    """User story al que pertenece el comentario
    
    |"""


class ParticipaSprint(models.Model):
    """
    Describe la relación de pertenencia de un usuario dentro de un sprint.

    **Fecha:** 30/09/21

    **Artefacto:** Módulo de desarrollo
    """
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    """Sprint en el que participa el usuario."""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    """Usuario que participa en el sprint."""

    horas_diarias = models.IntegerField()
    """Horas disponibles cada día por el usuario para este sprint"""

    user_stories = models.ManyToManyField(UserStory)
    """Indica que user stories tiene asignado el usuario
    
    |"""


class Incremento(models.Model):
    """
    **Fecha:** 23/10/21

    **Artefacto:** módulo de desarrollo

    |
    """
    participasprint = models.ForeignKey(ParticipaSprint, null=True, on_delete=models.SET_NULL)
    """Indica que usuario realizó el incremento en qué sprint"""

    fecha = models.DateField(default=datetime.date.today)
    """Fecha en la que se registró el incremento"""

    horas = models.IntegerField(default=0)
    """Horas que se trabajaron ese día"""
