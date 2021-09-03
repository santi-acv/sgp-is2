from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from guardian.shortcuts import assign_perm, get_perms_for_model, remove_perm


class UserManager(BaseUserManager):
    def create_user(self, user_id, email, nombre, apellido):
        """
        Crea un usuario con los datos proveidos.\n
        Fecha: 21/08/21\n
        Artefacto: Usuario
        """
        user = self.model(
            user_id=user_id,
            email=email,
            nombre=nombre,
            apellido=apellido)
        user.set_unusable_password()
        user.save()
        return user

    def create_superuser(self, user_id, email, nombre, apellido):
        """
        Crea un administrador con los datos proveidos.\n
        Fecha: 21/08/21\n
        Artefacto: Usuario
        """
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
    Describe a un usuario con correo, nombre, y apellido.\n
    Fecha: 21/08/21\n
    Artefacto: Usuario
    """
    user_id = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    nombre = models.CharField(max_length=60)
    apellido = models.CharField(max_length=60)
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


class Proyecto(models.Model):
    """
    Crea proyectos nuevos, si el usuario tiene el permiso crear_proyecto.\n
    Fecha: 26/08/21\n
    Artefacto: Módulo de proyecto
    """
    STATUS = (
        ('pendiente', 'Pendiente'),
        ('iniciado', 'Iniciado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    creador = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name="creador_user")
    duracion_sprint = models.CharField(max_length=30, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, auto_now=False)
    fecha_inicio = models.DateField("Inicio (mm/dd/yy)", auto_now_add=False, auto_now=False, null=True)
    fecha_fin = models.DateField("Fin (mm/dd/yy)", auto_now_add=False, auto_now=False, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS, default='pendiente')
    equipo = models.ManyToManyField(User, through='Participa', related_name="equipo_users")

    def asignar_rol(self, user, rol):

        if user in self.equipo.all():
            participa = Participa.objects.get(usuario=user, proyecto=self)
            for perm in participa.rol.permisos.all():
                remove_perm(perm.codename, user, self)
            participa.delete()
        else:
            assign_perm('vista', user, self)

        participa = Participa.objects.create(usuario=user, proyecto=self, rol=self.role_set.get(nombre=rol))
        for perm in participa.rol.permisos.all():
            assign_perm(perm.codename, user, self)

    def __str__(self):
        return self.nombre

    def crear_roles_predeterminados(self):
        perms = get_perms_for_model(Proyecto)

        rol = Role.objects.create(nombre='Scrum master', proyecto=self)
        rol.permisos.add(perms.get(codename='administrar_equipo'))
        rol.permisos.add(perms.get(codename='gestionar_proyecto'))
        rol.permisos.add(perms.get(codename='desarrollo'))

        rol = Role.objects.create(nombre='Product owner', proyecto=self)
        rol.permisos.add(perms.get(codename='pila_producto'))

        rol = Role.objects.create(nombre='Desarrollador', proyecto=self)
        rol.permisos.add(perms.get(codename='desarrollo'))

        rol = Role.objects.create(nombre='Interesado', proyecto=self)

    class Meta:
        default_permissions = ()
        permissions = [
            ('administrar_equipo', 'Permite asignar permisos a los usuarios'),
            ('gestionar_proyecto', 'Permite auditar la información del sistema'),
            ('pila_producto', 'Permite crear proyectos nuevos'),
            ('desarrollo', 'Permite crear proyectos nuevos'),
            ('vista', 'Permite ver información del proyecto'),
        ]


class Role(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    permisos = models.ManyToManyField(Permission)

    def asignar_permiso(self, permiso):
        self.permisos.add(permiso)
        for p in self.participa_set.select_related('usuario'):
            assign_perm(permiso, p.usuario, self.proyecto)

    def quitar_permiso(self, permiso):
        self.permisos.remove(permiso)
        for p in self.participa_set.select_related('usuario'):
            remove_perm(permiso, p.usuario, self.proyecto)

    def __str__(self):
        return self.nombre + ' | ' + str(self.proyecto)


class Participa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    rol = models.ForeignKey(Role, on_delete=models.CASCADE)
