
from is2.settings.default import *

ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '[::1]']

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'is2_sgp_production',
        'USER': 'is2_sgp',
        'PASSWORD': 'is2_sgp',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

STATIC_ROOT = BASE_DIR / 'static'

MEDIA_ROOT = BASE_DIR / 'media'
