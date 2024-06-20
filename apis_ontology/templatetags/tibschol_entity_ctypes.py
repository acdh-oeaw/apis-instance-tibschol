from django import template
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from apis_core.relations.utils import relation_content_types

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


@register.simple_tag
def tibschol_relation_types():
    relation_groups = [
        "Person - Person",
        "Person - Work",
        "Person - Instance",
        "Person - Place",
        "Work - Work",
        "Work - Instance",
        "Work - Place",
        "Instance - Instance",
        "Instance - Place",
        "Place - Place",
    ]
    ctypes = {}
    for rel_grp in relation_groups:
        m1, m2 = [
            apps.get_model("apis_ontology", m.strip()) for m in rel_grp.split("-")
        ]
        ctypes[rel_grp] = relation_content_types(m1, m2)

    return ctypes
