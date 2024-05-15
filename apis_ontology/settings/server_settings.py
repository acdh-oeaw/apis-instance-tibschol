from apis_acdhch_default_settings.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APIS_BASE_URI = "https://tibschol.acdh-ch.oeaw.ac.at/"

ROOT_URLCONF = "apis_ontology.urls"
CSRF_TRUSTED_ORIGINS = [
    "https://tibschol.acdh-ch.oeaw.ac.at",
    "https://tibschol-test.acdh-ch-dev.oeaw.ac.at",
]

INSTALLED_APPS += [
    "apis_core.relations",
    "apis_highlighter",
    "django.contrib.postgres",
    "apis_core.collections",
    "apis_core.history",
    "django_action_logger",
    "django_acdhch_functions",
    "django_select2",
]
INSTALLED_APPS.remove("apis_ontology")
INSTALLED_APPS.insert(0, "apis_ontology")


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
SIMPLE_HISTORY_ENABLED = False  # disable for now

SELECT2_CACHE_BACKEND = "default"  # Specify your cache backend here
SELECT2_CACHE_TIMEOUT = 3600  # Set cache timeout in seconds (e.g., 1 hour)
