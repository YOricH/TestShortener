# Django settings.

import environ
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')


# Security

SECRET_KEY = env(
    'SECRET_KEY',
    default='django-insecure-bdmvw1%zbrd1@6760ok)9k4mc3o+t39m_56(pc!e=5g#*g_2vb',
)
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '0.0.0.0', '127.0.0.1'])


# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'project.shortener',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database & cache

DATABASES = {'default': env.db('DATABASE_URI')}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_CACHE = env.bool('USE_CACHE', True)
CACHES = {
    'default': env.cache(
        'CACHE_URL', backend='django.core.cache.backends.redis.RedisCache'
    )
}


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'


# REDIS related settings

BROKER_URL = env('BROKER_URL')
RESULT_BACKEND = env('RESULT_BACKEND')


# Logging settings
LOG_LEVEL = env.str('LOG_LEVEL', 'INFO')
LOG_FILE_NAME = env.str('LOG_FILE_NAME', default=BASE_DIR / 'shortener.log')
USE_LOG_FILE = env.bool('USE_LOG_FILE', False)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '{levelname}|{asctime}|{filename}:{lineno} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'project.shortener': {
            'level': LOG_LEVEL,
            'handlers': ['console'],
        }
    },
}

if USE_LOG_FILE:
    file_handler = {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE_NAME,
            'formatter': 'default',
        }
    LOGGING.get('handlers')['file'] = file_handler  # noqa
    LOGGING.get('loggers').get('project.shortener').get('handlers', []).append('file')


# Django Rest Framework
PAGINATION_PAGE_SIZE = env.int('PAGINATION_PAGE_SIZE', default=20)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': PAGINATION_PAGE_SIZE,
}


# Shortener settings
BASE_ENCODING = env.str(
    'BASE_ENCODING', '23456789abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'
)
SUBPART_HASH_LEN = env.int('SUBPART_HASH_LEN', 11)
SESSION_COOKIE_AGE = env.int('SESSION_COOKIE_AGE', 1209600)  # Two weeks
DIRECTION_LIFETIME_SEC = env.int('DIRECTION_LIFETIME_SEC', SESSION_COOKIE_AGE)
CACHE_ON_CREATE = env.bool('CACHE_ON_CREATE', True)
SCHEDULE_CLEAR_DATA_MINUTES = env.int('SCHEDULE_CLEAR_DATA_MINUTES', 60)
LINES_ON_PAGE = env.int('LINES_ON_PAGE', PAGINATION_PAGE_SIZE)
LAST_TRY_NUM = env.int('LAST_TRY_NUM', 10)
