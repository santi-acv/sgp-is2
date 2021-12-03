"""
Las pruebas unitarias utilizan el mecanismo de pruebas de Django. Para
realizar esta prueba, es necesario utilizar el siguiente comando.

.. code-block:: console

   (venv) $ python manage.py test

Las pruebas se encuentran agrupadas en clases según que componente evalúan.
"""
import datetime

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from guardian.shortcuts import assign_perm, get_perms_for_model

from .forms import ProyectoForm, UserStoryForm, ComentarioForm, SprintForm, \
    AgregarDesarrolladorForm, AgregarUserStoryForm, SprintReviewForm
from .models import Proyecto, User, UserStory, Comentario, Sprint, ParticipaSprint, Role, Incremento


class NavigationTest(TestCase):

    def test_inicio_respuesta_http(self):
        """
        Verifica si la pagina de inicio envía una respuesta apropiada.

        **Fecha:** 16/08/21

        **Artefacto:** Página de inicio

        |
        """
        response = self.client.get(reverse('sgp:index'))
        self.assertEqual(response.status_code, 200,
                         "La página de inicio retornó un error HTTP")

    def test_administrar_respuesta_http(self):
        """
        Verifica si la pagina de administración envía una respuesta apropiada.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de seguridad

        |
        """
        response = self.client.get(reverse('sgp:administrar'))
        self.assertEqual(response.status_code, 200,
                         "La página de administración retornó un error HTTP")

    def test_crear_proyecto_respuesta_http(self):
        """
        Verifica si la pagina de creación de proyecto envía una respuesta apropiada.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        response = self.client.get(reverse('sgp:crear_proyecto'))
        self.assertEqual(response.status_code, 200,
                         "La página de creación de proyecto retornó un error HTTP")

    def test_mostrar_proyecto_respuesta_http(self):
        """
        Verifica si la pagina de información de proyecto envía una respuesta apropiada.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        Proyecto.objects.create(nombre='Proyecto de prueba', fecha_inicio=datetime.date(2021, 12, 30),
                                fecha_fin=datetime.date(2021, 12, 31), duracion_sprint=1)
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        response = self.client.get(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proj.id}))
        self.assertEqual(response.status_code, 200,
                         "La página de información de proyecto retornó un error HTTP")

    def test_editar_proyecto_respuesta_http(self):
        """
        Verifica si la pagina de edición de proyecto envía una respuesta apropiada.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        Proyecto.objects.create(nombre='Proyecto de prueba')
        proj = Proyecto.objects.get(nombre='Proyecto de prueba')
        response = self.client.get(reverse('sgp:editar_proyecto', kwargs={'proyecto_id': proj.id}))
        self.assertEqual(response.status_code, 200,
                         "La página de edición de proyecto retornó un error HTTP")


class PermissionTest(TestCase):

    def test_otorgar_permisos(self):
        """
        Verifica si se otorgan permisos por instancia de objeto adecuadamente.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo django-guardian

        |
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
        Verifica el rol de scrum master otorga el permiso de gestión.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de proyecto

        |
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
        Verifica que asignar un rol diferente elimine permisos antiguos.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de proyecto

        |
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
        Verifica que la asociación participa conecte al usuario con el proyecto.

        **Fecha:** 03/09/21

        **Artefacto:** Módulo de proyecto

        |
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


class CrearProyectoTest(TestCase):

    def test_campo_requerido(self):
        """
        Verifica los campos nombre, duración de sprint, fecha de inicio, y
        fecha de fin sean obligatorios.

        **Fecha:** 20/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        form = ProyectoForm(data={})
        for campo in form.fields:
            if campo in ['nombre', 'duracion_sprint', 'fecha_inicio', 'fecha_fin']:
                self.assertEqual(form.errors[campo], ['Este campo es obligatorio.'])

    def test_fecha_formato_valido(self):
        """
        Verifica que el formulario acepte fechas si y solo si están en formato
        dd/mm/aa.

        **Fecha:** 20/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        for fecha in ['12/31/2021', '2021/12/31', '31-dec-2021']:
            form = ProyectoForm(data={'fecha_inicio': fecha,
                                      'fecha_fin': fecha})
            self.assertEqual(form.errors['fecha_inicio'],
                             ['La fecha debe estar en formato dd/mm/aaaa.'])
            self.assertEqual(form.errors['fecha_fin'],
                             ['La fecha debe estar en formato dd/mm/aaaa.'])

        form = ProyectoForm(data={'nombre': 'Proyecto test',
                                  'fecha_inicio': '30/12/2037',
                                  'fecha_fin': '31/12/2037',
                                  'duracion_sprint': 1})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors.get('fecha_inicio'), None)
        self.assertEqual(form.errors.get('fecha_inicio'), None)

    def test_fechas_presente(self):
        """
        Verifica que las fechas de inicio y de fin no hayan ocurrido en el
        pasado, y que la fecha de fin ocura después de la fecha de inicio.

        **Fecha:** 20/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        form = ProyectoForm(data={'nombre': 'Proyecto test',
                                  'fecha_inicio': '30/12/2020',
                                  'fecha_fin': '31/12/2020',
                                  'duracion_sprint': 1})
        self.assertEqual(form.errors['fecha_inicio'],
                         ['La fecha de inicio no puede ser en el pasado.'])
        self.assertEqual(form.errors['fecha_fin'],
                         ['La fecha de fin no puede ser en el pasado.'])

        form = ProyectoForm(data={'nombre': 'Proyecto test',
                                  'fecha_inicio': '31/12/2021',
                                  'fecha_fin': '30/12/2021',
                                  'duracion_sprint': 1})
        self.assertEqual(form.errors['fecha_fin'],
                         ['La fecha de fin debe ser después de la fecha de inicio.'])

    def test_duracion_sprint(self):
        """
        Verifica que haya tiempo para por lo menos un sprint entre las fechas
        de inicio y de fin.

        **Fecha:** 20/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        form = ProyectoForm(data={'nombre': 'Proyecto test',
                                  'fecha_inicio': '30/12/2021',
                                  'fecha_fin': '31/12/2021',
                                  'duracion_sprint': 2})
        form.is_valid()
        self.assertEqual(form.errors['duracion_sprint'], ['El proyecto debe tener tiempo para al menos un sprint.'])

    def test_creacion_exitosa(self):
        """
        Verifica que ProyectoForm sea capaz de crear un proyecto.

        **Fecha:** 20/09/21

        **Artefacto:** Módulo de proyecto

        |
        """
        form = ProyectoForm(data={'nombre': 'Proyecto test',
                                  'fecha_inicio': '30/12/2021',
                                  'fecha_fin': '31/12/2021',
                                  'duracion_sprint': 1})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(Proyecto.objects.filter(nombre='Proyecto test').exists())


class FormulariosDesarrolloTest(TestCase):

    def setUp(self):
        self.proj = Proyecto.objects.create(nombre='Proyecto de prueba', fecha_fin=datetime.date(2022, 1, 1))
        self.proj.crear_roles_predeterminados()
        self.user = User.objects.create(
            nombre='Nombre', apellido='Apellido', email='test@test.com', is_superuser=True)

    def test_crear_user_story(self):
        """
        Verifica que UserStoryForm sea capaz de crear un user story.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """

        form = UserStoryForm(usuario=self.user, proyecto=self.proj,
                             data={'nombre': 'US de prueba', 'horas_estimadas': 10, 'prioridad': 3})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertTrue(UserStory.objects.filter(nombre='US de prueba', proyecto=self.proj).exists(),
                        "El user story no fue creado correctamente")

    def test_editar_user_story(self):
        """
        Verifica que UserStoryForm sea capaz de editar un user story.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """

        us = UserStory.objects.create(numero=1, nombre='US de prueba', proyecto=self.proj)
        form = UserStoryForm(usuario=self.user, proyecto=self.proj, instance=us,
                             data={'nombre': 'US modificado', 'horas_estimadas': 10, 'prioridad': 3})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertTrue(UserStory.objects.filter(nombre='US modificado', proyecto=self.proj,
                                                 horas_estimadas=10, prioridad=3).exists(),
                        "El user story no fue modificado correctamente")

    def test_agregar_comentario(self):
        """
        Verifica que ComentarioForm sea capaz de agregar un comentario a un proyecto.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """

        us = UserStory.objects.create(numero=1, nombre='US de prueba', proyecto=self.proj)
        form = ComentarioForm(usuario=self.user, user_story=us, data={'texto': 'Texto de comentario.'})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertEquals(Comentario.objects.get(user_story=us).texto, 'Texto de comentario.',
                          "El comentario no fue creado correctamente")

    def test_crear_sprint(self):
        """
        Verifica que SprintForm sea capaz de crear un sprint.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """

        form = SprintForm(proyecto=self.proj,
                          data={'nombre': 'Sprint de prueba', 'fecha_inicio': '12/12/2021', 'duracion': 10})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertTrue(Sprint.objects.filter(nombre='Sprint de prueba', proyecto=self.proj).exists(),
                        "El sprint no fue creado correctamente")

    def test_editar_sprint(self):
        """
        Verifica que SprintForm sea capaz de editar un sprint.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """
        sprint = Sprint.objects.create(nombre='Sprint de prueba', fecha_inicio=datetime.date(2021, 12, 20),
                                       fecha_fin=datetime.date(2021, 12, 10), proyecto=self.proj)
        form = SprintForm(proyecto=self.proj, instance=sprint,
                          data={'nombre': 'Sprint modificado', 'fecha_inicio': '2021-12-25', 'duracion': 7})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertEquals(Sprint.objects.get(nombre='Sprint modificado', proyecto=self.proj).fecha_fin,
                          datetime.date(2022, 1, 1), "El sprint no fue modificado correctamente")

    def test_agregar_user_story(self):
        """
        Verifica que AgregarUserStoryForm sea capaz de agregar un user story a un sprint.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """

        sprint = Sprint.objects.create(nombre='Sprint de prueba', fecha_inicio='2021-12-20',
                                       fecha_fin='2021-12-30', proyecto=self.proj)
        self.proj.asignar_rol(self.user, Role.objects.get(nombre='Desarrollador'))

        ParticipaSprint.objects.create(sprint=sprint, usuario=self.user, horas_diarias=0)

        us = UserStory.objects.create(numero=1, nombre='US de prueba', proyecto=self.proj)
        form = AgregarUserStoryForm(proyecto=self.proj, sprint=sprint,
                                    data={'user_story': us, 'usuario': self.user})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertTrue(us in sprint.sprint_backlog.all(), "El user story no aparece en el sprint backlog")
        self.assertTrue(us in ParticipaSprint.objects.get(usuario=self.user, sprint=sprint).user_stories.all(),
                        "El user story no aparece asignado al desarrollador")

    def test_agregar_desarrollador(self):
        """
        Verifica que AgregarDesarrolladorForm sea capaz de agregar un desarrollador a un sprint.

        **Fecha:** 10/10/21

        **Artefacto:** Módulo de proyecto

        |
        """

        sprint = Sprint.objects.create(nombre='Sprint de prueba', fecha_inicio=datetime.date(2021, 12, 20),
                                       fecha_fin=datetime.date(2021, 12, 30), proyecto=self.proj)
        self.proj.asignar_rol(self.user, Role.objects.get(nombre='Desarrollador'))
        form = AgregarDesarrolladorForm(proyecto=self.proj, sprint=sprint, data={'usuario': self.user, 'horas': 10})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertEquals(ParticipaSprint.objects.get(usuario=self.user, sprint=sprint).horas_diarias, 10,
                          "El desarrollador no fue agregado al equipo con las horas disponibles indicadas")
        self.assertEquals(sprint.capacidad_diaria, 10, "La capacidad del equipo difiere de la del desarrollador")


class ScriptPoblarTest(TestCase):

    def setUp(self):
        import scripts.poblar_base_de_datos

    def test_script_poblar_base_datos(self):
        """Verifica que el script para poblar la base de datos se ejecute
        adecuadamente."""
        self.assertEquals(Proyecto.objects.filter().count(), 3, "El script no pobló la base de datos")


class FlujoKanbanTest(TestCase):
    def setUp(self):
        user = User.objects.create(user_id=1, email='correo@test.com.py',
                                   nombre='Nombre', apellido='Apellido')
        self.client.login(token=1, test=True)
        proyecto = Proyecto.objects.create(nombre='Proyecto de prueba', fecha_inicio=datetime.date(2021, 12, 30),
                                           fecha_fin=datetime.date(2021, 12, 31), duracion_sprint=1)
        proyecto.crear_roles_predeterminados()
        rol = proyecto.role_set.get(nombre='Scrum master')
        perms = get_perms_for_model(Proyecto)
        rol.asignar_permiso(perms.get(codename='pila_producto'))
        rol.asignar_permiso(perms.get(codename='desarrollo'))
        proyecto.asignar_rol(user, 'Scrum master')
        sprint = Sprint.objects.create(nombre='Sprint de prueba', proyecto=proyecto, estado=Sprint.Estado.INICIADO,
                                       fecha_inicio=datetime.date(2021, 12, 30), fecha_fin=datetime.date(2021, 12, 31))
        us = UserStory.objects.create(numero=1, nombre='US de prueba', proyecto=proyecto, sprint=sprint,
                                      horas_estimadas=10)
        ParticipaSprint.objects.create(sprint=sprint, usuario=user, horas_diarias=10).user_stories.add(us)

    def test_iniciar_proyecto(self):
        """Verifica que el proyecto inicie sin errores."""
        proyecto = Proyecto.objects.get()
        self.client.post(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': proyecto.id}))
        proyecto = Proyecto.objects.get()
        self.assertEquals(proyecto.estado, Proyecto.Estado.INICIADO,
                          "El proyecto no ha iniciado: " + str(proyecto.validar_inicio()['errores']))

    def test_iniciar_sprint(self):
        """Verifica que el sprint inicie sin errores."""
        proyecto = Proyecto.objects.get()
        proyecto.estado = Proyecto.Estado.INICIADO
        proyecto.save()
        sprint = Sprint.objects.get()
        sprint.estado = Sprint.Estado.PENDIENTE
        sprint.save()
        self.client.post(reverse('sgp:mostrar_sprint', kwargs={'proyecto_id': proyecto.id, 'sprint_id': sprint.id}))
        sprint = proyecto.sprint_activo
        self.assertEquals(sprint.estado, Sprint.Estado.INICIADO,
                          "El sprint no ha iniciado: " + str(sprint.validar_inicio()['errores']))

    def test_registrar_horas(self):
        """Verifica que el tablero kanban registre las horas trabajadas."""
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'trabajar', 'horas': 5})
        us = UserStory.objects.get()
        self.assertEquals(us.horas_trabajadas, 5, "Las horas trabajadas no se han registrado")

    def test_iniciar_user_story(self):
        """Verifica que el tablero kanban pueda iniciar un user story."""
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'iniciar'})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.INICIADO, "El user story no ha podido iniciar")

    def test_mandar_user_story_a_qa(self):
        """Verifica que el tablero kanban pueda enviar un user story a QA."""
        us = UserStory.objects.get()
        us.estado = UserStory.Estado.INICIADO
        us.save()
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'enviar_qa'})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.FASE_DE_QA, "El user story no ha llegado a QA")

    def test_aprobar_user_story(self):
        """Verifica que el tablero kanban pueda aprobar un user story en QA."""
        us = UserStory.objects.get()
        us.estado = UserStory.Estado.FASE_DE_QA
        us.save()
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'aprobar'})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.FINALIZADO, "El user story no ha sido aprobado")

    def test_rechazar_user_story(self):
        """Verifica que el tablero kanban pueda rechazar un user story en QA."""
        us = UserStory.objects.get()
        us.estado = UserStory.Estado.FASE_DE_QA
        us.save()
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'rechazar'})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.PENDIENTE, "El user story no ha sido rechazado")

    def test_cancelar_user_story(self):
        """Verifica que el tablero kanban cancele un user story."""
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'cancelar'})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.CANCELADO, "El user story no ha sido cancelado")

    def test_restaurar_user_story(self):
        """Verifica que el tablero kanban restaure un user story cancelado."""
        us = UserStory.objects.get()
        us.estado = UserStory.Estado.CANCELADO
        us.save()
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'restaurar'})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.PENDIENTE, "El user story no ha sido restaurado")

    def test_inicio_automatico(self):
        """Verifica que un user story pendiente al que se le agreguen horas
        inicie automáticamente."""
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'trabajar', 'horas': 5})
        us = UserStory.objects.get()
        self.assertEquals(us.estado, UserStory.Estado.INICIADO, "El user story no ha iniciado automáticamente")

    def test_registro_horas_trabajadas(self):
        """Verifica que las horas trabajadas aparezcan en el registro."""
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'trabajar', 'horas': 5})
        response = self.client.get(reverse('sgp:registro_kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}))
        self.assertContains(response, "5 horas", msg_prefix="Las horas trabajadas no aparecen en el registro")

    def test_registro_cambio_de_estado(self):
        """Verifica que el cambio de estado aparezca en el registro."""
        self.client.post(reverse('sgp:kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}),
                         {'us': 1, 'accion': 'iniciar'})
        response = self.client.get(reverse('sgp:registro_kanban', kwargs={'proyecto_id': Proyecto.objects.get().id}))
        self.assertContains(response, "Iniciado", msg_prefix="El nuevo estado no aparece en el registro")


class CierreProyectoTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(user_id=1, email='correo@test.com.py',
                                        nombre='Nombre', apellido='Apellido')
        self.client.login(token=1, test=True)
        self.proyecto = Proyecto.objects.create(nombre='Proyecto de prueba', fecha_inicio=datetime.date(2021, 10, 30),
                                                fecha_fin=datetime.date(2021, 12, 31), duracion_sprint=1,
                                                estado=Proyecto.Estado.INICIADO)
        self.sprint = Sprint.objects.create(nombre='Sprint de prueba', proyecto=self.proyecto,
                                            estado=Sprint.Estado.FINALIZADO, fecha_inicio=datetime.date(2021, 11, 1),
                                            fecha_fin=datetime.date(2021, 11, 7))
        self.us = UserStory.objects.create(numero=1, nombre='US de prueba', proyecto=self.proyecto, sprint=self.sprint,
                                           horas_estimadas=10, horas_trabajadas=10, estado=UserStory.Estado.FINALIZADO)
        self.proyecto.crear_roles_predeterminados()
        self.proyecto.asignar_rol(self.user, 'Scrum master')
        ParticipaSprint.objects.create(sprint=self.sprint, usuario=self.user,
                                       horas_diarias=10).user_stories.add(self.us)

    def test_registrar_review(self):
        """Verifica que el sprint review sea registrado correctamente."""
        form = SprintReviewForm(instance=self.sprint, data={'review': 'El sprint ha finalizado sin inconvenientes.'})
        self.assertTrue(form.is_valid(), "El formulario no es válido")
        form.save()
        self.assertEquals(Sprint.objects.first().review, 'El sprint ha finalizado sin inconvenientes.',
                          "El sprint review no fue registrado correctamente.")

    def test_burndown_chart(self):
        """Verifica que el burndown chart se genere correctamente."""
        for i in range(8):
            Incremento.objects.create(user_story=self.us, usuario=self.user,
                                      fecha=datetime.date(2021, 11, 1+i), horas=i+1)
        response = self.client.get(reverse('sgp:burndown_chart',
                                           kwargs={'proyecto_id': self.proyecto.id, 'sprint_id': self.sprint.id}))
        self.assertContains(response, str(list(range(9))),
                            msg_prefix="El burndown chart no contiene los datos de los incrementos")

    def test_cerrar_sprint(self):
        """Verifica que el sprint finalice sin errores."""
        sprint = Sprint.objects.get()
        sprint.estado = Sprint.Estado.INICIADO
        sprint.save()
        self.client.post(reverse('sgp:mostrar_sprint',
                                 kwargs={'proyecto_id': self.proyecto.id, 'sprint_id': self.sprint.id}))
        sprint = Sprint.objects.get()
        self.assertEquals(sprint.estado, Sprint.Estado.FINALIZADO,
                          "El sprint no ha finalizado: " + str(sprint.validar_inicio()['errores']))

    def test_cerrar_proyecto(self):
        """Verifica que el proyecto finalice sin errores."""
        self.client.post(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': self.proyecto.id}))
        proyecto = Proyecto.objects.get()
        self.assertEquals(proyecto.estado, Proyecto.Estado.FINALIZADO,
                          "El proyecto no ha finalizado: " + str(proyecto.validar_inicio()['errores']))

    def test_enviar_notificaciones(self):
        """Verifica que se coloquen las notificaciones por correo en la bandeja
        de salida del sistema."""
        self.client.post(reverse('sgp:mostrar_proyecto', kwargs={'proyecto_id': self.proyecto.id}))
        self.assertTrue(len(mail.outbox) > 0, "No se ha generado ningún correo")
        self.assertEquals(mail.outbox[0].subject, 'SGP: El proyecto Proyecto de prueba ha finalizado',
                          "La notificación por correo no se ha generado correctamente")

    def test_generar_reporte_proyecto(self):
        """Verifica que se genere el informe del product backlog."""
        response = self.client.get(reverse('sgp:reporte_proyecto', kwargs={'proyecto_id': self.proyecto.id}))
        self.assertEquals(response.get('Content-Disposition'), "filename=Reporte - Product Backlog")

    def test_generar_reporte_sprint(self):
        """Verifica que se genere el informe del sprint backlog."""
        response = self.client.get(reverse('sgp:reporte_sprint',
                                           kwargs={'proyecto_id': self.proyecto.id, 'sprint_id': self.sprint.id}))
        self.assertEquals(response.get('Content-Disposition'), "filename=Reporte - Sprint Backlog")

    def test_generar_reporte_us_prioridad(self):
        """Verifica que se genere el informe de los user stories con prioridad."""
        sprint = Sprint.objects.get()
        sprint.estado = Sprint.Estado.INICIADO
        sprint.save()
        response = self.client.get(reverse('sgp:reporte_us_prioridad', kwargs={'proyecto_id': self.proyecto.id}))
        self.assertEquals(response.get('Content-Disposition'), "filename=Reporte - US - Prioridad")
