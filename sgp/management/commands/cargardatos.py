from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Puebla las tablas de la base de datos.'

    def handle(self, *args, **options):
        exec(open('scripts/poblar_base_de_datos.py').read())
