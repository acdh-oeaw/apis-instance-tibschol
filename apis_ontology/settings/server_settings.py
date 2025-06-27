from apis_acdhch_default_settings.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = [
        "127.0.0.1",
    ]


ROOT_URLCONF = "apis_ontology.urls"
CSRF_TRUSTED_ORIGINS = [
    "https://tibschol.acdh-ch.oeaw.ac.at",
    "https://tibschol.acdh-ch-dev.oeaw.ac.at",
]

INSTALLED_APPS += [
    "django.contrib.postgres",
    "django_select2",
    "django_interval",
]
INSTALLED_APPS.append("apis_core.documentation")


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(levelname)-8s %(asctime)s] %(name)-6s %(message)s",
            "datefmt": "%y-%m-%d %H:%M %Z",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

LOG_LIST_NOSTAFF_EXCLUDE_APP_LABELS = ["admin", "sessions", "auth"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 60 * 60 * 24,  # Timeout set to 1 day (in seconds)
    },
}

SELECT2_CACHE_BACKEND = "select2"

MIDDLEWARE += [
    "simple_history.middleware.HistoryRequestMiddleware",
]

GIT_REPOSITORY_URL = "https://github.com/acdh-oeaw/apis-instance-tibschol"
APIS_ANON_VIEWS_ALLOWED = False
EXPORT_FORMATS = ("csv", "xlsx")
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap5-responsive.html"
DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-striped table-hover",
}
