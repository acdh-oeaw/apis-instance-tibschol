from apis_acdhch_default_settings.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APIS_BASE_URI = "https://tibschol.acdh-ch.oeaw.ac.at/"

ROOT_URLCONF = "apis_ontology.urls"

INSTALLED_APPS += [
    "apis_core.relations",
    "apis_highlighter",
    "django.contrib.postgres",
    "apis_core.collections",
    "apis_core.history",
]

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
