
# import datetime
# from django.utils import timezone
from sgp.models import *

# Usuarios de prueba
u1 = User.objects.create(user_id=107981716032077457293,
                         email='py.santi@fpuna.edu.py',
                         nombre='Santiago', apellido='Acevedo')
u2 = User.objects.create(user_id=110304737331718959098,
                         email='py.santi@gmail.com',
                         nombre='Sofia', apellido='Martinez')
u3 = User.objects.create(user_id=110741015195322049227,
                         email='santiago.acevedo.paraguay@gmail.com',
                         nombre='Matias', apellido='Rodriguez')
u4 = User.objects.create(user_id=112525045848524405851,
                         email='sgp.iu2.fpuna@gmail.com',
                         nombre='Maria', apellido='Garcia')
assign_perm('sgp.administrar', u1)


# Proyecto por terminar
proyecto = Proyecto.objects.create(nombre='Trabajo final ML',
                                   duracion_sprint=7, estado=Proyecto.Estado.INICIADO,
                                   fecha_creacion=timezone.localdate() + timedelta(days=-22),
                                   fecha_inicio=timezone.localdate() + timedelta(days=-21),
                                   fecha_fin=timezone.localdate() + timedelta(days=0))
proyecto.crear_roles_predeterminados()
proyecto.asignar_rol(u1, 'Scrum master')
proyecto.asignar_rol(u2, 'Product owner')
proyecto.asignar_rol(u3, 'Desarrollador')
proyecto.asignar_rol(u4, 'Interesado')
sprint1 = Sprint.objects.create(nombre='Primera exposicion',
                                fecha_inicio=timezone.localdate() + timedelta(days=-21),
                                fecha_fin=timezone.localdate() + timedelta(days=-14),
                                estado=Sprint.Estado.FINALIZADO, proyecto=proyecto)
sprint2 = Sprint.objects.create(nombre='Segunda exposicion',
                                fecha_inicio=timezone.localdate() + timedelta(days=-14),
                                fecha_fin=timezone.localdate() + timedelta(days=-7),
                                estado=Sprint.Estado.FINALIZADO, proyecto=proyecto)
sprint3 = Sprint.objects.create(nombre='Defensa final',
                                fecha_inicio=timezone.localdate() + timedelta(days=-7),
                                fecha_fin=timezone.localdate() + timedelta(days=0),
                                estado=Sprint.Estado.INICIADO, proyecto=proyecto)
us = [UserStory.objects.create(numero=1, nombre='Leer papers',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=5,
                               horas_trabajadas=5,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=2, nombre='Armar presentacion',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=2,
                               horas_trabajadas=2,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=3, nombre='Examinar bibliografia',
                               estado=UserStory.Estado.CANCELADO,
                               prioridad=3, horas_estimadas=7,
                               horas_trabajadas=2,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=4, nombre='Construir prototipo',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=8,
                               horas_trabajadas=8,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=5, nombre='Proponer mejoras',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=5,
                               horas_trabajadas=5,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=6, nombre='Comparar librerias',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=2,
                               horas_trabajadas=2,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=7, nombre='Implementar algoritmo',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=16,
                               horas_trabajadas=16,
                               proyecto=proyecto, sprint=sprint3),
      UserStory.objects.create(numero=8, nombre='Redactar informe',
                               estado=UserStory.Estado.FASE_DE_QA,
                               prioridad=3, horas_estimadas=4,
                               horas_trabajadas=4,
                               proyecto=proyecto, sprint=sprint3),
      UserStory.objects.create(numero=9, nombre='Defender trabajo',
                               estado=UserStory.Estado.FASE_DE_QA,
                               prioridad=3, horas_estimadas=1,
                               horas_trabajadas=1,
                               proyecto=proyecto, sprint=sprint3)]
p1 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u3, horas_diarias=1)
p2 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u3, horas_diarias=2)
p3 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u3, horas_diarias=3)
p1.user_stories.add(us[0])
p1.user_stories.add(us[1])
p2.user_stories.add(us[3])
p2.user_stories.add(us[4])
p2.user_stories.add(us[5])
p3.user_stories.add(us[6])
p3.user_stories.add(us[7])
p3.user_stories.add(us[8])
p1.save()
p2.save()
p3.save()
h = [[1, 2, 1, 0, 1, 0, 0],
     [0, 0, 0, 0, 0, 0, 2],
     [0, 1, 1, 0, 0, 0, 0],
     [0, 0, 3, 1, 0, 0, 4],
     [0, 0, 1, 0, 3, 2, 0],
     [2, 0, 0, 0, 0, 0, 0],
     [2, 5, 6, 0, 3, 0, 0],
     [0, 0, 0, 0, 1, 3, 0],
     [0, 0, 0, 0, 0, 0, 1]]
for i in range(7):
    for j in range(9):
        if h[j][i]:
            Incremento.objects.create(user_story=us[j], usuario=u3, horas=h[j][i],
                                      fecha=timezone.localdate() + timedelta(days=-21+7*(j//3)+i))
h = [4, 6, -1, 6, 7, 0, 4, 5, 6]
for i in range(7):
    for j in range(9):
        if h[j] == i:
            Incremento.objects.create(user_story=us[j], usuario=u3, estado=UserStory.Estado.FASE_DE_QA,
                                      fecha=timezone.localdate() + timedelta(days=-21+7*(j//3)+i))
            if j < 7:
                Incremento.objects.create(user_story=us[j], usuario=u1, estado=UserStory.Estado.FINALIZADO,
                                          fecha=timezone.localdate() + timedelta(days=-21 + 7 * (j // 3) + i))
Incremento.objects.create(user_story=us[2], usuario=u1, estado=UserStory.Estado.CANCELADO,
                          fecha=timezone.localdate() + timedelta(days=-17))

# Proyecto durante la mitad de su duracion
proyecto = Proyecto.objects.create(nombre='Curso de noviembre a diciembre',
                                   duracion_sprint=7, estado=Proyecto.Estado.INICIADO,
                                   fecha_creacion=timezone.localdate() + timedelta(days=-11),
                                   fecha_inicio=timezone.localdate() + timedelta(days=-10),
                                   fecha_fin=timezone.localdate() + timedelta(days=11))
proyecto.crear_roles_predeterminados()
proyecto.asignar_rol(u1, 'Scrum master')
proyecto.asignar_rol(u2, 'Product owner')
proyecto.asignar_rol(u3, 'Desarrollador')
proyecto.asignar_rol(u4, 'Interesado')
sprint1 = Sprint.objects.create(nombre='Modulo basico',
                                fecha_inicio=timezone.localdate() + timedelta(days=-10),
                                fecha_fin=timezone.localdate() + timedelta(days=-3),
                                estado=Sprint.Estado.FINALIZADO, proyecto=proyecto)
sprint2 = Sprint.objects.create(nombre='Modulo intermedio',
                                fecha_inicio=timezone.localdate() + timedelta(days=-3),
                                fecha_fin=timezone.localdate() + timedelta(days=4),
                                estado=Sprint.Estado.INICIADO, proyecto=proyecto)
sprint3 = Sprint.objects.create(nombre='Modulo avanzado',
                                fecha_inicio=timezone.localdate() + timedelta(days=4),
                                fecha_fin=timezone.localdate() + timedelta(days=11),
                                estado=Sprint.Estado.PENDIENTE, proyecto=proyecto)
us = [UserStory.objects.create(numero=1, nombre='Tareas introductorias',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=10,
                               horas_trabajadas=10,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=2, nombre='Tomar notas',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=3, horas_estimadas=5,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=3, nombre='Escribir conclusion',
                               estado=UserStory.Estado.INICIADO,
                               prioridad=4, horas_estimadas=5,
                               horas_trabajadas=2,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=4, nombre='Resolver ejercicios',
                               estado=UserStory.Estado.FASE_DE_QA,
                               prioridad=2, horas_estimadas=5,
                               horas_trabajadas=5,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=5, nombre='Leer capitulo principal',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=1, horas_estimadas=5,
                               horas_trabajadas=5,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=6, nombre='Leer capitulo opcional',
                               estado=UserStory.Estado.CANCELADO,
                               prioridad=5, horas_estimadas=5,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=7, nombre='Consultar otras fuentes',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=3, horas_estimadas=5,
                               proyecto=proyecto)]
p1 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u3, horas_diarias=2)
p2 = ParticipaSprint.objects.create(sprint=sprint2, usuario=u3, horas_diarias=4)
p3 = ParticipaSprint.objects.create(sprint=sprint3, usuario=u3, horas_diarias=4)
p1.user_stories.add(us[0])
p2.user_stories.add(us[1])
p2.user_stories.add(us[2])
p2.user_stories.add(us[3])
p2.user_stories.add(us[4])
p2.user_stories.add(us[5])
p3.user_stories.add(us[6])
p1.save()
p2.save()
p3.save()
h = [1, 3, 0, 3, 1, 2, 0]
for i in range(7):
    Incremento.objects.create(user_story=us[0], usuario=u3, horas=h[i],
                              fecha=timezone.localdate() + timedelta(days=-10+i))
Incremento.objects.create(user_story=us[0], usuario=u3, estado=UserStory.Estado.FASE_DE_QA,
                          fecha=timezone.localdate() + timedelta(days=-3))
Incremento.objects.create(user_story=us[0], usuario=u1, estado=UserStory.Estado.FINALIZADO,
                          fecha=timezone.localdate() + timedelta(days=-3))
h = [[0, 0, 2, 0],
     [1, 1, 0, 3],
     [2, 1, 2, 0]]
for i in range(4):
    for j in range(3):
        if h[0][i]:
            Incremento.objects.create(user_story=us[j], usuario=u3, horas=h[j][i],
                                      fecha=timezone.localdate() + timedelta(days=-3+i))
Incremento.objects.create(user_story=us[3], usuario=u3, estado=UserStory.Estado.FASE_DE_QA,
                          fecha=timezone.localdate() + timedelta(days=0))
Incremento.objects.create(user_story=us[4], usuario=u3, estado=UserStory.Estado.FASE_DE_QA,
                          fecha=timezone.localdate() + timedelta(days=-1))
Incremento.objects.create(user_story=us[4], usuario=u1, estado=UserStory.Estado.FINALIZADO,
                          fecha=timezone.localdate() + timedelta(days=-1))


# Proyecto recien creado
proyecto = Proyecto.objects.create(nombre='Startup 2022',
                                   duracion_sprint=7, estado=Proyecto.Estado.INICIADO,
                                   fecha_creacion=timezone.localdate() + timedelta(days=-1),
                                   fecha_inicio=timezone.localdate() + timedelta(days=0),
                                   fecha_fin=timezone.localdate() + timedelta(days=21))
proyecto.crear_roles_predeterminados()
proyecto.asignar_rol(u1, 'Scrum master')
proyecto.asignar_rol(u2, 'Product owner')
proyecto.asignar_rol(u3, 'Desarrollador')
proyecto.asignar_rol(u4, 'Desarrollador')
sprint1 = Sprint.objects.create(nombre='Semana de brainstorming',
                                fecha_inicio=timezone.localdate() + timedelta(days=0),
                                fecha_fin=timezone.localdate() + timedelta(days=7),
                                estado=Sprint.Estado.PENDIENTE, proyecto=proyecto)
us = [UserStory.objects.create(numero=1, nombre='Definir objetivos',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=1, horas_estimadas=5,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=2, nombre='Establecer metas',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=3, horas_estimadas=10,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=3, nombre='Investigar cosas',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=4, horas_estimadas=15,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=4, nombre='Proponer ideas',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=2, horas_estimadas=5,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=5, nombre='Adquirir recursos',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=5, horas_estimadas=30,
                               proyecto=proyecto)]
p1 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u3, horas_diarias=3)
p2 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u4, horas_diarias=2)
p1.user_stories.add(us[0])
p2.user_stories.add(us[1])
p1.user_stories.add(us[2])
p2.user_stories.add(us[3])
p1.save()
p2.save()
