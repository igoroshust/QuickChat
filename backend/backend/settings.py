from pathlib import Path
import chat, api
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5qp^6&@ixr%%a!cyxa%q)mpfwm0f09!87_l6haujde*(#jjml4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'chat',
    'channels',
    'api',
    'rest_framework',
    'corsheaders',
    'django_extensions',
    'allauth',
    'allauth.account',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # статические файлы в продакш-среде (+daphne)
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

SITE_ID = 1

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'chat.CustomUser'

# Настройки Allauth
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Это нужно для аутентификации
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Настройки для Allauth
ACCOUNT_FORMS = {'signup': 'chat.forms.CustomSignupForm'}
ACCOUNT_SIGNUP_REDIRECT_URL = 'empty_main'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_EMAIL_VERIFICATION = 'optional'  # optional - подтверждение электронной почты необязательно (mandatory)
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Позволяет входить по имени пользователя или электронной почте
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_PASSWORD_MIN_LENGTH = 8  # Минимальная длина пароля
LOGIN_REDIRECT_URL = 'empty_main'  # URL, на который будет перенаправлен пользователь после входа


# Настройки SMTP
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_HOST = 'smtp.yandex.ru'
# EMAIL_PORT = 587  # Используйте 465 для SSL
# EMAIL_USE_TLS = True  # Установите на True, если используете порт 587
# # EMAIL_USE_SSL = True  # Установите на True, если используете порт 465
# EMAIL_HOST_USER = 'igoroshust@yandex.ru'  # Ваш адрес электронной почты на Яндексе
# EMAIL_HOST_PASSWORD = ''  # Ваш пароль от Яндекс.Почты

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'chat': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'api': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# WebSockets
ASGI_APPLICATION = 'backend.asgi.application'

# Настройка канала
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
