from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa


def render_to_pdf(request, template_src, context=None):
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
