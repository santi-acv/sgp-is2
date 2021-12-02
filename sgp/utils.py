from io import BytesIO

from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa


def enviar_recordatorio(actividad, tipo, accion):
    """
    Envía un correo al equipo correspondiente a una actividad de cierto tipo
    recordándoles de una acción agendada para el día de hoy.

    **Fecha:** 2/12/21

    **Artefacto:** módulo de desarrollo

    :param actividad: El proyecto o sprint cuyo recordatorio se va a enviar
    :param tipo: Indica si la actividad es un proyecto o un sprint
    :param accion: Indica si se notificará acerca del inicio o el fin de la actividad
    :type actividad: Proyecto | Sprint
    :type tipo: string
    :type accion: string

    |
    """
    asunto = 'SGP: '+accion+' del '+tipo+' '+actividad.nombre
    cuerpo = '¡Buenos días!\n\n' \
             'Le recordamos que el %s del %s %s se encuentra agendado para hoy.\n\n' \
             'Atentamente,\n\n' \
             'Sistema Gestor de Proyectos' \
             % (accion, tipo, actividad.nombre)
    html = '<p>¡Buenos días!</p>' \
           '<p>Le recordamos que el %s del %s <strong>%s</strong> se encuentra agendado para hoy.</p>' \
           '<p>Atentamente,</p>' \
           '<p>Sistema Gestor de Proyectos</p>' \
           % (accion, tipo, actividad.nombre)
    send_mail(asunto, cuerpo, None,
              actividad.equipo.values_list('email', flat=True),
              fail_silently=False, html_message=html)


def enviar_notificacion(actividad, tipo, estado):
    """
    Envía un correo al equipo correspondiente a una actividad de cierto tipo
    notificandoles de una acción que se ha realizado.

    **Fecha:** 2/12/21

    **Artefacto:** módulo de desarrollo

    :param actividad: El proyecto o sprint cuya notificación se va a enviar
    :param tipo: Indica si la actividad es un proyecto o un sprint
    :param estado: Indica si la actividad ha iniciado o finalizado
    :type actividad: Proyecto | Sprint
    :type tipo: string
    :type estado: string

    |
    """
    asunto = 'SGP: El '+tipo+' '+actividad.nombre+' ha '+estado
    fecha_fin = (' Su fecha de fin se encuentra agendada para el %s.'
                 % actividad.fecha_fin) if estado == 'iniciado' else ''
    cuerpo = '¡Saludos!\n\n' \
             'Le informamos que el %s %s ha %s.%s\n\n' \
             'Atentamente,\n\n' \
             'Sistema Gestor de Proyectos' \
             % (tipo, actividad.nombre, estado, fecha_fin)
    html = '<p>¡Saludos!</p>' \
           '<p>Le informamos que el %s <strong>%s</strong> ha %s.%s</p>' \
           '<p>Atentamente,</p>' \
           '<p>Sistema Gestor de Proyectos</p>' \
           % (tipo, actividad.nombre, estado, fecha_fin)
    send_mail(asunto, cuerpo, None,
              actividad.equipo.values_list('email', flat=True),
              fail_silently=False, html_message=html)


def render_to_pdf(request, template_src, context=None):
    """
    Envía un correo al equipo correspondiente a una actividad de cierto tipo
    notificandoles de una acción que se ha realizado.

    **Fecha:** 2/12/21

    **Artefacto:** módulo de desarrollo

    :param request: La solicitud para la cual se generará una respuesta
    :param template_src: El nombre de la plantilla que será renderizada
    :param context: El contexto que será pasado a la plantilla
    :type request: Request
    :type template_src: string
    :type context: dict

    |
    """
    if context is None:
        context = {}
    else:
        context['request'] = request
        if not context.get('pagesize'):
            context['pagesize'] = 'A4'
    template = get_template(template_src)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if pdf.err:
        raise Exception("Ocurrió un error generando el PDF del reporte")
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    if context.get('filename'):
        response['Content-Disposition'] = 'filename='+context['filename']
    return response
