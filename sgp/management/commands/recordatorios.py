from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from sgp.models import Proyecto


class Command(BaseCommand):
    help = 'Envía por correo recordatorios de los eventos del día de hoy.'

    def handle(self, *args, **options):
        hoy = timezone.localdate()

        for p in Proyecto.objects.filter(estado=Proyecto.Estado.PENDIENTE):
            if p.fecha_inicio == hoy:
                enviar_correo(p, 'proyecto', 'inicio')

            if p.sprint_pendiente and p.sprint_pendiente.fecha_inicio == hoy:
                enviar_correo(p.sprint_pendiente, 'sprint', 'inicio')

        for p in Proyecto.objects.filter(estado=Proyecto.Estado.INICIADO):
            if p.sprint_pendiente and p.sprint_pendiente.fecha_inicio == hoy:
                enviar_correo(p.sprint_pendiente, 'sprint', 'inicio')

            if p.sprint_activo and p.sprint_activo.fecha_fin == hoy:
                enviar_correo(p.sprint_activo, 'sprint', 'fin')

            if p.fecha_fin == hoy:
                enviar_correo(p, 'proyecto', 'fin')


def enviar_correo(actividad, tipo, estado):

    asunto = 'SGP: '+estado+' del '+tipo+' '+actividad.nombre

    cuerpo = '¡Buenos días!\n\n' \
             'Le recordamos que el %s del %s %s se encuentra agendado para hoy.\n\n' \
             'Atentamente,\n\n' \
             'Sistema Gestor de Proyectos' \
             % (estado, tipo, actividad.nombre)

    html = '<p>¡Buenos días!</p>' \
           '<p>Le recordamos que el %s del %s <strong>%s</strong> se encuentra agendado para hoy.</p>' \
           '<p>Atentamente,</p>' \
           '<p>Sistema Gestor de Proyectos</p>' \
           % (estado, tipo, actividad.nombre)

    send_mail(asunto, cuerpo, None,
              actividad.equipo.values_list('email', flat=True),
              fail_silently=False, html_message=html)
