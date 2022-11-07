import os
from datetime import timedelta

from decouple import config
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', default='i')

DEBUG = False

ALLOWED_HOSTS = ['*', ]

ROOT_URLCONF = 'foodgram.urls'

WSGI_APPLICATION = 'foodgram.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_filters',
    'api.apps.ApiConfig',
    'recipes',
    'users',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': config(
            'DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config(
            'DB_NAME', default='postgres'),
        'USER': config(
            'POSTGRES_USER', default='postgres'),
        'PASSWORD': config(
            'POSTGRES_PASSWORD', default='12345678'),
        'HOST': config(
            'DB_HOST', default='db'),
        'PORT': config(
            'DB_PORT', default=5432, cast=int)
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME':
        ('django.contrib.auth.password_validation.'
         'UserAttributeSimilarityValidator'), },
    {'NAME':
        ('django.contrib.auth.password_validation.'
         'MinimumLengthValidator'), },
    {'NAME':
        ('django.contrib.auth.password_validation.'
         'CommonPasswordValidator'), },
    {'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS':
        ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6,
}
DJOSER = {
    'LOGIN_FIELD': 'email',
    'HIDE_USERS': False,
    'PERMISSIONS': {
        'resipe': ('api.permissions.AdminAuthorsReadOnly,',),
        'recipe_list': ('api.permissions.AdminAuthorsReadOnly',),
        'user': ('api.permissions.OwnerUserOrReadOnly',),
        'user_list': ('api.permissions.OwnerUserOrReadOnly',),
    },
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'user_list': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.UserSerializer',
        'user_create': 'api.serializers.UserSerializer',
    },
}
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Token',),
}

AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USERNAME_LENGTH = 150
EMAIL_LENGTH = 254
FIRST_NAME_LENGTH = 150
LAST_NAME_LENGTH = 150
PASSWORD_LENGTH = 150
TAG_NAME_LENGTH = 200
INGRIDIENT_NAME_LENGTH = 200
RECIPE_NAME_LENGTH = 200
MEASURMENT_COUNT_LENGTH = 200
ADD_METHODS = ('GET', 'POST',)
DEL_METHODS = ('DELETE',)
ACTION_METHODS = [s.lower() for s in (ADD_METHODS + DEL_METHODS)]
