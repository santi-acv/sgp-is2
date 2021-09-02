from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin



class UserManager(BaseUserManager):
    def create_user(self, user_id, email, nombre, apellido, password=None):
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
        user.save()
        return user

    def create_superuser(self, user_id, email, nombre, apellido, password=None):
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
    nombre_proyecto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    creador = models.CharField(max_length=200, blank=True)
    duracion_sprint = models.CharField(max_length=30, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, null=True)
    fecha_inicio = models.DateTimeField(blank=True, null=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)

    def __str__(self):
        return self.nombre_proyecto







