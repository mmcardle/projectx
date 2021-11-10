"""
Django settings for projectx project.

For more information on this file, see
https://docs.djangoproject.com/

"""

import warnings
from pathlib import Path

import environ

# See https://github.com/mpdavis/python-jose/issues/221
warnings.filterwarnings(action="ignore", module="jose.backends.cryptography_backend")

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "SECRET_KEY"),
    JWT_SECRET=(str, "JWT_SECRET"),
    PUBLIC_IP=(str, "localhost"),
    DATABASE_URL=(str, "psql://postgres:mysecretpassword@localhost:5432/postgres"),
    CACHE_URL=(str, "redis://@localhost:6379/0"),
    CHANNELS_REDIS_URL=(str, "redis://localhost:6379/1"),
    TEMPLATE_DIR=(str, "/home/user/frontend/"),
    LOG_FILE=(str, None),
)

SECRET_KEY = env.str("SECRET_KEY")
JWT_SECRET = env.str("JWT_SECRET")
DEBUG = env("DEBUG")
PUBLIC_IP = env.str("PUBLIC_IP")

ALLOWED_HOSTS = [PUBLIC_IP]

if DEBUG:  # pragma: no cover
    ALLOWED_HOSTS.append("projectx")  # Allows connections from internal docker services

# Application definition
INSTALLED_APPS = [
    "django_su",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "projectx.users",
    "projectx.common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "projectx.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [env.str("TEMPLATE_DIR")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "projectx.wsgi.application"

AUTH_USER_MODEL = "users.User"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {"default": env.db()}

# Cache
CACHES = {"default": env.cache()}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    # Custom validators
    {"NAME": "projectx.users.validation.NumberValidator", "OPTIONS": {"minimum": 1}},
    {"NAME": "projectx.users.validation.UppercaseValidator", "OPTIONS": {"minimum": 1}},
    {"NAME": "projectx.users.validation.LowercaseValidator", "OPTIONS": {"minimum": 1}},
    {"NAME": "projectx.users.validation.SymbolValidator", "OPTIONS": {"minimum": 1}},
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/site_media/static/"

STATIC_ROOT = Path("/") / "var" / "www" / "site_media" / "static"

# Django Channels
ASGI_APPLICATION = "projectx.channels.application"

CHANNELS_REDIS_URL = env.url("CHANNELS_REDIS_URL")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(CHANNELS_REDIS_URL.hostname, CHANNELS_REDIS_URL.port)],
            "capacity": 500,  # default 100
            "expiry": 20,
        },
    },
}

# Email setup
DEFAULT_FROM_EMAIL = "noreply@example.com"
if DEBUG:  # pragma: no cover
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    DEFAULT_FROM_EMAIL = "projectx@example.com"
    SERVER_EMAIL = "projectx@example.com"
    EMAIL_USE_SSL = True
    EMAIL_CONFIG = env.email("EMAIL_URL", default="smtp://mail_user:mail_user_password@127.0.0.1:456")
    vars().update(EMAIL_CONFIG)

handlers = {}
if DEBUG:  # pragma: no cover
    handlers["stream_handler"] = {"class": "logging.StreamHandler", "formatter": "simple"}

if log_file := env.str("LOG_FILE"):  # pragma: no cover
    handlers["file_handler"] = {"class": "logging.FileHandler", "formatter": "simple", "filename": log_file}

handler_names = list(handlers.keys())

# Logging setup
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s %(name)s:%(lineno)s %(message)s"},
    },
    "handlers": handlers,
    "loggers": {
        "": {
            "handlers": handler_names,
            "level": "INFO",
        },
        "django.request": {
            "handlers": handler_names,
            "level": "ERROR",
        },
        "asyncio": {
            "handlers": handler_names,
            "level": "WARNING",  # Reduce asyncio INFO spam
        },
        "projectx": {
            "handlers": handler_names,
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "common": {
            "handlers": handler_names,
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "api": {
            "handlers": handler_names,
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "users": {
            "handlers": handler_names,
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
        "daphne": {
            "handlers": handler_names,
            "level": "INFO",
            "propagate": False,
        },
    },
}
