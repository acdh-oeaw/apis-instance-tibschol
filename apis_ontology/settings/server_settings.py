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
]
