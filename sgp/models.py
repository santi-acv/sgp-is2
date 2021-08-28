from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.forms import ModelForm


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


class proyecto(models.Model):
    """
    Crea proyectos nuevos, si el usuario tiene el permiso crear_proyecto.\n
    Fecha: 26/08/21\n
    Artefacto: Módulo de proyecto
    """
    nombre_proyecto = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=300)
    Duracion_sprint = models.DurationField
    fecha_inicio = models.DateTimeField('Fecha de inicio del proyecto')
    fecha_fin = models.DateTimeField('Fecha de fin del proyecto')


class equipo(models.Model):
    """
    Crea un equipo de trabajo asociado a un proyecto.\n
    Fecha: 28/08/21\n
    Artefacto: Módulo de proyecto
    """
    equipo = models.ManyToManyField(user)


class ProjectForm(ModelForm):
