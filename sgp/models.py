from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group
from guardian.shortcuts import assign_perm


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
    creador = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    duracion_sprint = models.CharField(max_length=30, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, auto_now=False)
    fecha_inicio = models.DateField("Inicio (mm/dd/yy)", auto_now_add=False, auto_now=False, null=True)
    fecha_fin = models.DateField("Fin (mm/dd/yy)", auto_now_add=False, auto_now=False, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS, default='pendiente')

    def __str__(self):
        return self.nombre

    def crear_roles_predeterminados(self):

        rol = self.group_set.create(name='Scrum master')
        assign_perm('administrar_equipo', rol, self)
        assign_perm('gestionar_proyecto', rol, self)
        assign_perm('vista', rol, self)

        rol = self.group_set.create(name='Product owner')
        assign_perm('pila_producto', rol, self)
        assign_perm('vista', rol, self)

        rol = self.group_set.create(name='Desarrolador')
        assign_perm('desarrollo', rol, self)
        assign_perm('vista', rol, self)

        self.group_set.create(name='Interesado')
        assign_perm('vista', rol, self)

    class Meta:
        permissions = [
            ('administrar_equipo', 'Permite asignar permisos a los usuarios'),
            ('gestionar_proyecto', 'Permite auditar la información del sistema'),
            ('pila_producto', 'Permite crear proyectos nuevos'),
            ('desarrollo', 'Permite crear proyectos nuevos'),
            ('vista', 'Permite ver información del proyecto'),
        ]


if not hasattr(Group, 'proyecto'):
    field = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    field.contribute_to_class(Group, 'proyecto')


class Role(Group):
    class Meta:
        proxy = True

    def __str__(self):
        return self.name + ' | ' + str(self.proyecto)
