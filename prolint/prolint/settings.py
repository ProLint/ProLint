import os
from os.path import abspath, dirname, join
from pathlib import Path
from bokeh.settings import bokehjsdir

# Build paths inside the project like this: join(BASE_DIR, ...)
MODULE_DIR = dirname(abspath(__file__))
BASE_DIR = dirname(MODULE_DIR)
BASE_PATH = Path(BASE_DIR)

# A semi-random - absolutely not secure - key
SECRET_KEY = 'uwibp$#$fzo4Besian)085(7^z@60w@)9kt-eSejdiumm2n#xt'
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'allauth',
    'allauth.account',
    'crispy_forms',
    'material',
    'debug_toolbar',
    'channels',
    'bokeh.server.django',
    'multiselectfield',
    'storages',

    # Local
    'users.apps.UsersConfig',
    'pages',
    'uploads',
    'results',
    'explore',
    'calcul',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'prolint.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

ASGI_APPLICATION = 'results.routing.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'dummypass',
        'HOST': 'db',
        'PORT': 5432,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Edmonton'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_TASK_TRACK_STARTED = True

################################################################
################################################################
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"), bokehjsdir()
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# User uploaded content
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
USER_DATA = os.path.join(MEDIA_ROOT, 'user-data')

CRISPY_TEMPLATE_PACK = 'bootstrap4'

INTERNAL_IPS = ['127.0.0.1']

# accounts are not used
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = 'home'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1
ACCOUNT_FORMS = {'signup': 'users.forms.CustomUserCreationForm'}
THEMES_DIR = join(MODULE_DIR, "themes")
CELERY_IMPORTS = ['calcul', 'calcul.tasks']

# Email configuration. Define the options below and
# set EMAIL_CONFIGURED to True for it to take effect.
EMAIL_CONFIGURED = False
FROM_SENDER = ''
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 000
EMAIL_USE_TLS = True
