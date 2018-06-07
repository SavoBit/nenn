import os.path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

ALLOWED_HOSTS = ['*']
SECRET_KEY = 'notsecret'
DEBUG = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'uwu.vulnerable',
)

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',

)

ROOT_URLCONF = 'uwu.urls'

TEMPLATES = [
    {
        # jinja2 for spicier template injection
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': ['uwu/templates'],
        'OPTIONS': {
            'environment': 'uwu.vulnerable.jinja2.environment',
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'uwu.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

FIXTURE_DIRS = [os.path.join(BASE_DIR, 'fixtures')]

# AUTH_USER_MODEL = 'vulnerable.Employee'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/profile'
# extremely contrived, combined example of security misconfig and broken auth
AUTHENTICATION_BACKENDS = [
    'uwu.vulnerable.auth.CrapAuthBackend',
]
PASSWORD_HASHERS = [
    'uwu.vulnerable.hashers.CrapHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static/'),
)

# TODO
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# for the xxe example but maybe others...
FILE_UPLOAD_HANDLERS = [
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
]
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MiB
