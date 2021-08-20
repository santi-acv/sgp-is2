
from is2.settings.default import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'is2_sgp_development',
        'USER': 'is2_sgp',
        'PASSWORD': 'is2_sgp',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
