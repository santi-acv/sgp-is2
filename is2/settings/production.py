
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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'sgp.is2.fpuna'
EMAIL_HOST_PASSWORD = 'agkqwnhcntlizdwx'
DEFAULT_FROM_EMAIL = 'Sistema Gestor de Proyectos'

STATIC_ROOT = BASE_DIR / 'static'

MEDIA_ROOT = BASE_DIR / 'media'
