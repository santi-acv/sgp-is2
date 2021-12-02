from django.core.management.base import BaseCommand
from django.utils import timezone

from sgp.models import Proyecto
from sgp.utils import enviar_recordatorio


class Command(BaseCommand):
    help = 'Envía por correo recordatorios de los eventos del día de hoy.'

    def handle(self, *args, **options):
        hoy = timezone.localdate()

        for p in Proyecto.objects.filter(estado=Proyecto.Estado.PENDIENTE):
            if p.fecha_inicio == hoy:
                enviar_recordatorio(p, 'proyecto', 'inicio')

            if p.sprint_pendiente and p.sprint_pendiente.fecha_inicio == hoy:
                enviar_recordatorio(p.sprint_pendiente, 'sprint', 'inicio')

        for p in Proyecto.objects.filter(estado=Proyecto.Estado.INICIADO):
            if p.sprint_pendiente and p.sprint_pendiente.fecha_inicio == hoy:
                enviar_recordatorio(p.sprint_pendiente, 'sprint', 'inicio')

            if p.sprint_activo and p.sprint_activo.fecha_fin == hoy:
                enviar_recordatorio(p.sprint_activo, 'sprint', 'fin')

            if p.fecha_fin == hoy:
                enviar_recordatorio(p, 'proyecto', 'fin')
