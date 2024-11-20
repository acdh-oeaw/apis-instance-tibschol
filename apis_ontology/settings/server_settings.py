from apis_acdhch_default_settings.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

APIS_BASE_URI = "https://tibschol.acdh-ch.oeaw.ac.at/"

ROOT_URLCONF = "apis_ontology.urls"
CSRF_TRUSTED_ORIGINS = [
    "https://tibschol.acdh-ch.oeaw.ac.at",
    "https://tibschol.acdh-ch-dev.oeaw.ac.at",
]

INSTALLED_APPS += [
    "django.contrib.postgres",
    "apis_core.collections",
    "apis_core.history",
    "django_acdhch_functions",
    "django_select2",
]
INSTALLED_APPS.remove("apis_ontology")
INSTALLED_APPS.insert(0, "apis_ontology")
INSTALLED_APPS = ["apis_core.relations"] + INSTALLED_APPS
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
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 20,
}

MIDDLEWARE += [
    "simple_history.middleware.HistoryRequestMiddleware",
]


def apis_view_passes_test(view) -> bool:
    if view.request.user.is_authenticated:
        return True
    if view.permission_action_required == "view":
        # this is set when APIS_DETAIL_VIEWS_ALLOWED is True
        obj = view.get_object()
        return obj.review
    return False


def apis_list_view_object_filter(view, queryset):
    if view.request.user.is_authenticated:
        return queryset

    return queryset.filter(review=True)


APIS_LIST_VIEWS_ALLOWED = True
APIS_LIST_VIEW_OBJECT_FILTER = apis_list_view_object_filter

APIS_DETAIL_VIEWS_ALLOWED = True
APIS_VIEW_PASSES_TEST = apis_view_passes_test
