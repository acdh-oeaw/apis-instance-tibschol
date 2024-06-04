from django import template
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

register = template.Library()


@register.simple_tag
def tibschol_entity_types():
    models = [
        "person",
        "work",
        "instance",
        "place",
    ]
    ctypes = [
        ContentType.objects.get_for_model(apps.get_model("apis_ontology", m))
        for m in models
    ]
    return ctypes
