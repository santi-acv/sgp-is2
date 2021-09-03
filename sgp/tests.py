from django.test import TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm

from .models import Proyecto, User


class NavigationTest(TestCase):

    def test_inicio_respuesta_http(self):
        """
        Verifica si la pagina de inicio envía una respuesta apropiada.\n
        Fecha: 16/08/21\n
        Artefacto: Página de inicio
        """
        response = self.client.get(reverse('sgp:index'))
        self.assertEqual(response.status_code, 200,
                         "La página de inicio retornó un error HTTP")

    def test_administrar_respuesta_http(self):
        """
        Verifica si la pagina de administración envía una respuesta apropiada.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de seguridad
        """
        response = self.client.get(reverse('sgp:administrar'))
        self.assertEqual(response.status_code, 200,
                         "La página de administración retornó un error HTTP")

    def test_crear_proyecto_respuesta_http(self):
        """
        Verifica si la pagina de creación de proyecto envía una respuesta apropiada.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        response = self.client.get(reverse('sgp:crear_proyecto'))
        self.assertEqual(response.status_code, 200,
                         "La página de creación de proyecto retornó un error HTTP")

    def test_mostrar_proyecto_respuesta_http(self):
        """
        Verifica si la pagina de información de proyecto envía una respuesta apropiada.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        response = self.client.get(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proj.id}))
        self.assertEqual(response.status_code, 200,
                         "La página de información de proyecto retornó un error HTTP")
        proj.delete()

    def test_editar_proyecto_respuesta_http(self):
        """
        Verifica si la pagina de edición de proyecto envía una respuesta apropiada.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        response = self.client.get(reverse('sgp:editar_proyecto', kwargs={'proyecto_id': proj.id}))
        self.assertEqual(response.status_code, 200,
                         "La página de edición de proyecto retornó un error HTTP")
        proj.delete()

    def test_administrar_roles_respuesta_http(self):
        """
        Verifica si la pagina de administración de roles envía una respuesta apropiada.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        response = self.client.get(reverse('sgp:administrar_roles', kwargs={'proyecto_id': proj.id}))
        self.assertEqual(response.status_code, 200,
                         "La página de administración de roles retornó un error HTTP")
        proj.delete()


class PermissionTest(TestCase):

    def test_otorgar_permisos(self):
        """
        Verifica si se otorgan permisos por instancia de objeto adecuadamente.\n
        Fecha:03/09/21\n
        Artefacto: Módulo django-guardian
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        user = User.objects.create(
            user_id=1,
            email='ejemplo@fpuna.edu.py',
            nombre='Nombre',
            apellido='Apellido')
        assign_perm('vista', user, obj=proj)
        self.assertEqual(user.has_perm('vista', obj=proj), True,
                         "El usuario no tiene el permiso otorgado.")
        user.delete()
        proj.delete()

    def test_rol_predeterminado(self):
        """
        Verifica el rol de scrum master otorga el permiso de gestión.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        user = User.objects.create(
            user_id=1,
            email='ejemplo@fpuna.edu.py',
            nombre='Nombre',
            apellido='Apellido')
        proj.crear_roles_predeterminados()
        proj.asignar_rol(user, 'Scrum master')
        self.assertEqual(user.has_perm('gestionar_proyecto', obj=proj), True,
                         "El rol de scrum master no otorga al usuario el permiso de gestión.")
        user.delete()
        proj.delete()

    def test_cambio_de_rol(self):
        """
        Verifica que asignar un rol diferente elimine permisos antiguos.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        user = User.objects.create(
            user_id=1,
            email='ejemplo@fpuna.edu.py',
            nombre='Nombre',
            apellido='Apellido')
        proj.crear_roles_predeterminados()
        proj.asignar_rol(user, 'Scrum master')
        proj.asignar_rol(user, 'Interesado')
        self.assertEqual(user.has_perm('gestionar_proyecto', obj=proj), False,
                         "El usuario interesado aún tiene el permiso de gestión.")
        user.delete()
        proj.delete()

    def test_participa_set(self):
        """
        Verifica que la asociación participa conecte el usuario con el proyecto.\n
        Fecha: 03/09/21\n
        Artefacto: Módulo de proyecto
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        user = User.objects.create(
            user_id=1,
            email='ejemplo@fpuna.edu.py',
            nombre='Nombre',
            apellido='Apellido')
        proj.crear_roles_predeterminados()
        proj.asignar_rol(user, 'Interesado')
        self.assertEqual(user.participa_set.filter(proyecto=proj).exists(), True,
                         "No se puede acceder al proyecto a través del usuario")
        user.delete()
        proj.delete()
