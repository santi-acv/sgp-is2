
# import datetime
# from django.utils import timezone
from sgp.models import *

# Usuarios que pueden iniciar sesion
s1 = User.objects.create(user_id=107981716032077457293,
                         email='py.santi@fpuna.edu.py',
                         nombre='Santiago', apellido='Acevedo')
s2 = User.objects.create(user_id=110304737331718959098,
                         email='py.santi@gmail.com',
                         nombre='Santiago', apellido='Acevedo')
s3 = User.objects.create(user_id=110741015195322049227,
                         email='santiago.acevedo.paraguay@gmail.com',
                         nombre='Santiago', apellido='Acevedo')
assign_perm('sgp.administrar', s1)


# Usuarios de prueba
u1 = User.objects.create(user_id=1, email='correo1@test.com.py',
                         nombre='Maria', apellido='Gonzalez')
u2 = User.objects.create(user_id=2, email='correo2@test.com.py',
                         nombre='Ramon', apellido='Benitez')
u3 = User.objects.create(user_id=3, email='correo3@test.com.py',
                         nombre='Juan', apellido='Martinez')
u4 = User.objects.create(user_id=4, email='correo4@test.com.py',
                         nombre='Jose', apellido='Lopez')
u5 = User.objects.create(user_id=5, email='correo5@test.com.py',
                         nombre='Elizabeth', apellido='Gimenez')
u6 = User.objects.create(user_id=6, email='correo6@test.com.py',
                         nombre='Beatriz', apellido='Vera')


# Proyecto recien creado
proyecto = Proyecto.objects.create(nombre='Proyecto recien creado',
                                   duracion_sprint=7, estado=Proyecto.Estado.INICIADO,
                                   fecha_creacion=timezone.localdate() + datetime.timedelta(days=-1),
                                   fecha_inicio=timezone.localdate() + datetime.timedelta(days=0),
                                   fecha_fin=timezone.localdate() + datetime.timedelta(days=21))
proyecto.crear_roles_predeterminados()
sprint1 = Sprint.objects.create(nombre='Sprint de prueba',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=0),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=7),
                                estado=Sprint.Estado.PENDIENTE, proyecto=proyecto)
us = [UserStory.objects.create(numero=1, nombre='Primer User Story',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=3, horas_estimadas=30,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=2, nombre='Segundo User Story',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=4, horas_estimadas=10,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=3, nombre='Tercer User Story',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=2, horas_estimadas=40,
                               proyecto=proyecto, sprint=sprint1),
      UserStory.objects.create(numero=4, nombre='Cuarto User Story',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=5, horas_estimadas=10,
                               proyecto=proyecto),
      UserStory.objects.create(numero=5, nombre='Quinto User Story',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=1, horas_estimadas=50,
                               proyecto=proyecto)]
proyecto.asignar_rol(s1, 'Scrum master')
proyecto.asignar_rol(s2, 'Product owner')
proyecto.asignar_rol(s3, 'Desarrollador')
proyecto.asignar_rol(u1, 'Desarrollador')
proyecto.asignar_rol(u2, 'Desarrollador')
p1 = ParticipaSprint.objects.create(sprint=sprint1, usuario=s3, horas_diarias=6)
p2 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u1, horas_diarias=6)
p3 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u2, horas_diarias=5)
p1.user_stories.add(us[0])
p2.user_stories.add(us[1])
p2.user_stories.add(us[2])
p1.save()
p2.save()
p3.save()

# Proyecto durante la mitad de su duracion
proyecto = Proyecto.objects.create(nombre='Proyecto en curso',
                                   duracion_sprint=7, estado=Proyecto.Estado.INICIADO,
                                   fecha_creacion=timezone.localdate() + datetime.timedelta(days=-11),
                                   fecha_inicio=timezone.localdate() + datetime.timedelta(days=-10),
                                   fecha_fin=timezone.localdate() + datetime.timedelta(days=11))
proyecto.crear_roles_predeterminados()
sprint1 = Sprint.objects.create(nombre='Primer sprint',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=-10),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=-3),
                                estado=Sprint.Estado.FINALIZADO, proyecto=proyecto)
sprint2 = Sprint.objects.create(nombre='Segundo sprint',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=-3),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=4),
                                estado=Sprint.Estado.INICIADO, proyecto=proyecto)
sprint3 = Sprint.objects.create(nombre='Tercer sprint',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=4),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=11),
                                estado=Sprint.Estado.PENDIENTE, proyecto=proyecto)
us = [UserStory.objects.create(numero=1, nombre='Lunes',
                               estado=UserStory.Estado.FINALIZADO,
                               prioridad=3, horas_estimadas=20,
                               horas_trabajadas=20,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=2, nombre='Martes',
                               estado=UserStory.Estado.FASE_DE_QA,
                               prioridad=3, horas_estimadas=20,
                               horas_trabajadas=30,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=3, nombre='Miercoles',
                               estado=UserStory.Estado.FASE_DE_QA,
                               prioridad=3, horas_estimadas=20,
                               horas_trabajadas=15,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=4, nombre='Jueves',
                               estado=UserStory.Estado.INICIADO,
                               prioridad=3, horas_estimadas=30,
                               horas_trabajadas=15,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=5, nombre='Viernes',
                               estado=UserStory.Estado.INICIADO,
                               prioridad=2, horas_estimadas=30,
                               horas_trabajadas=35,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=6, nombre='Sabado',
                               estado=UserStory.Estado.INICIADO,
                               prioridad=2, horas_estimadas=50,
                               horas_trabajadas=25,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=7, nombre='Domingo',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=2, horas_estimadas=50,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=8, nombre='Asueto',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=4, horas_estimadas=40,
                               proyecto=proyecto, sprint=sprint2),
      UserStory.objects.create(numero=9, nombre='Feriado',
                               estado=UserStory.Estado.PENDIENTE,
                               prioridad=4, horas_estimadas=40,
                               proyecto=proyecto, sprint=sprint2)]
proyecto.asignar_rol(s1, 'Desarrollador')
proyecto.asignar_rol(s2, 'Scrum master')
proyecto.asignar_rol(u3, 'Product owner')
p1 = ParticipaSprint.objects.create(sprint=sprint1, usuario=s1, horas_diarias=8)
p2 = ParticipaSprint.objects.create(sprint=sprint2, usuario=s1, horas_diarias=8)
p3 = ParticipaSprint.objects.create(sprint=sprint3, usuario=s1, horas_diarias=8)
for i in us:
    p2.user_stories.add(i)
p2.save()


# Proyecto por terminar
proyecto = Proyecto.objects.create(nombre='Proyecto por finalizar',
                                   duracion_sprint=7, estado=Proyecto.Estado.INICIADO,
                                   fecha_creacion=timezone.localdate() + datetime.timedelta(days=-22),
                                   fecha_inicio=timezone.localdate() + datetime.timedelta(days=-21),
                                   fecha_fin=timezone.localdate() + datetime.timedelta(days=0))
proyecto.crear_roles_predeterminados()
sprint1 = Sprint.objects.create(nombre='Primer sprint',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=-21),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=-14),
                                estado=Sprint.Estado.FINALIZADO, proyecto=proyecto)
sprint2 = Sprint.objects.create(nombre='Segundo sprint',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=-14),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=-7),
                                estado=Sprint.Estado.FINALIZADO, proyecto=proyecto)
sprint3 = Sprint.objects.create(nombre='Tercer sprint',
                                fecha_inicio=timezone.localdate() + datetime.timedelta(days=-7),
                                fecha_fin=timezone.localdate() + datetime.timedelta(days=0),
                                estado=Sprint.Estado.INICIADO, proyecto=proyecto)
nombres = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda',
           'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega']
us = []
for i in range(24):
    s = i // 24
    us.append(UserStory.objects.create(numero=i, nombre=nombres[i],
                                       estado=UserStory.Estado.FINALIZADO if i < 18
                                       else UserStory.Estado.FASE_DE_QA,
                                       prioridad=3, horas_estimadas=20 + i**2 % 10,
                                       horas_trabajadas=20 + i**2 % 10,
                                       proyecto=proyecto, sprint=sprint1 if i < 8
                                       else sprint2 if i < 16 else sprint3))
proyecto.asignar_rol(s1, 'Scrum master')
proyecto.asignar_rol(s2, 'Desarrollador')
proyecto.asignar_rol(s3, 'Desarrollador')
proyecto.asignar_rol(u5, 'Product owner')
proyecto.asignar_rol(u6, 'Desarrollador')
p1 = ParticipaSprint.objects.create(sprint=sprint1, usuario=s2, horas_diarias=5)
p2 = ParticipaSprint.objects.create(sprint=sprint1, usuario=s3, horas_diarias=4)
p3 = ParticipaSprint.objects.create(sprint=sprint1, usuario=u6, horas_diarias=7)
p4 = ParticipaSprint.objects.create(sprint=sprint2, usuario=s2, horas_diarias=7)
p5 = ParticipaSprint.objects.create(sprint=sprint2, usuario=s3, horas_diarias=5)
p6 = ParticipaSprint.objects.create(sprint=sprint2, usuario=u6, horas_diarias=4)
p7 = ParticipaSprint.objects.create(sprint=sprint3, usuario=s2, horas_diarias=4)
p8 = ParticipaSprint.objects.create(sprint=sprint3, usuario=s3, horas_diarias=7)
p9 = ParticipaSprint.objects.create(sprint=sprint3, usuario=u6, horas_diarias=5)
p1.user_stories.add(us[0])
p1.user_stories.add(us[1])
p2.user_stories.add(us[2])
p2.user_stories.add(us[3])
p3.user_stories.add(us[4])
p3.user_stories.add(us[5])
p4.user_stories.add(us[6])
p4.user_stories.add(us[7])
p5.user_stories.add(us[8])
p5.user_stories.add(us[9])
p6.user_stories.add(us[10])
p6.user_stories.add(us[11])
p7.user_stories.add(us[12])
p7.user_stories.add(us[13])
p8.user_stories.add(us[14])
p8.user_stories.add(us[15])
p9.user_stories.add(us[16])
p9.user_stories.add(us[17])
p9.user_stories.add(us[18])
p9.user_stories.add(us[19])
p7.user_stories.add(us[20])
p8.user_stories.add(us[21])
p7.user_stories.add(us[22])
p8.user_stories.add(us[23])
p1.save()
p2.save()
p3.save()
p4.save()
p5.save()
p6.save()
p7.save()
p8.save()
p9.save()
