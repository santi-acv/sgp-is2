
from is2.settings.default import *

ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1]']

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'is2-sgp-production',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
