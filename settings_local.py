# Local settings that change on a per application / per environment basis
import os

PGSQLAPI_PASSWORD = os.getenv('PGSQL_PASSWORD', 'pw')
PGSQLAPI_USER = os.getenv('PGSQL_USER', 'postgres')
PGSQLAPI_HOST = os.getenv('PGSQLAPI_HOST', 'pgsqlapi')
POD_NAME = os.getenv('POD_NAME', 'pod')
ORGANIZATION_URL = os.getenv('ORGANIZATION_URL', 'example.com')

PAM_NAME = os.getenv('PAM_NAME', 'pam')
PAM_ORGANIZATION_URL = os.getenv('PAM_ORGANIZATION_URL', 'example.com')

ALLOWED_HOSTS = (
    f'iaas.{POD_NAME}.{ORGANIZATION_URL}',
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'iaas': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'iaas',
        'USER': PGSQLAPI_USER,
        'PASSWORD': PGSQLAPI_PASSWORD,
        'HOST': PGSQLAPI_HOST,
        'PORT': '5432',
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_default',
        'USER': PGSQLAPI_USER,
        'PASSWORD': PGSQLAPI_PASSWORD,
        'HOST': PGSQLAPI_HOST,
        'PORT': '5432',
    },
}

DATABASE_ROUTERS = [
    'iaas.db_router.IaasRouter',
]

DEBUG = False

INSTALLED_APPS = [
    'iaas',
]

# Small flag for whether or not this is a production deployment
PRODUCTION_DEPLOYMENT = os.getenv('PRODUCTION_DEPLOYMENT', 'true').lower() == 'true'

# Default is False
TESTING = os.getenv('TESTING', 'false').lower() == 'true'

# Localisation
USE_I18N = False
USE_L10N = False

ORG = ORGANIZATION_URL.split('.')[0]

APPLICATION_NAME = os.getenv('APPLICATION_NAME', f'{POD_NAME}_{ORG}_iaas')
LOGSTASH_ENABLE = os.getenv('LOGSTASH_ENABLE', 'false').lower() == 'true'

if f'{PAM_NAME}.{PAM_ORGANIZATION_URL}' == 'support.cloudcix.com' or LOGSTASH_ENABLE:

    CLOUDCIX_INFLUX_TAGS = {
        'service_name': APPLICATION_NAME,
    }

    # Tracing settings
    TRACER_CONFIG = {
        'logging': True,
        'sampler': {
            'type': 'probabilistic',
            'param': 1,
        },
        'local_agent': {
            'reporting_host': 'jaeger-agent',
        },
    }

    RAVEN_CONFIG = {
        'dsn': os.getenv('SENTRY_URL', None),
        'string_max_length': 100000,
        'processors': (
            'raven.processors.SanitizePasswordsProcessor',
        ),
        'release': 'stable',
    }
else:
    TRACER_CONFIG = {
        'logging': False,
        'sampler': {
            'type': 'const',
            'param': 0,
        },
    }
