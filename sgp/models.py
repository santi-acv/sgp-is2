"""
Los modelos corresponden a tablas en la base de datos, y cada instancia
representa una entrada. A continuación se documentan los campos principales y
los métodos adicionales de los modelos en uso por la aplicación.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
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
    """Almacena los apellidos del usuario, obtenidos a partir de su cuenta de Google.
    
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
    """Si el proyecto aún no ha iniciado, almacena una hora tentativa en la que
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
        self.crear_rol('Scrum master', ['administrar_equipo', 'gestionar_proyecto', 'desarrollo'])
        self.crear_rol('Product owner', ['pila_producto'])
        self.crear_rol('Desarrollador', ['desarrollo'])
        self.crear_rol('Interesado', [])

    class Meta:
        default_permissions = ()
        permissions = [
            ('administrar_equipo', 'Permite asignar permisos a los usuarios'),
            ('gestionar_proyecto', 'Permite auditar la información del sistema'),
            ('pila_producto', 'Permite crear proyectos nuevos'),
            ('desarrollo', 'Permite crear proyectos nuevos'),
            ('vista', 'Permite ver información del proyecto'),
        ]

    def __str__(self):
        return self.nombre


class Role(models.Model):
    """
    Describe un rol dentro de un proyecto, con todos los permisos que lo
    acompañan.

    **Fecha:** 02/09/21

    **Artefacto:** Roles de proyecto
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
        return self.nombre + ' | ' + str(self.proyecto)


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
