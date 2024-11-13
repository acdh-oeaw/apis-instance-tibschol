from django import template
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from apis_core.relations.utils import relation_content_types
from apis_core.apis_entities.utils import get_entity_classes

register = template.Library()


@register.simple_tag
def tibschol_entity_types():
    custom_order = [
        "Persons",
        "Works",
        "Instances",
        "Places",
    ]
    ent_classes = {
        entity._meta.verbose_name_plural: entity.get_listview_url()
        for entity in get_entity_classes()
    }
    sorted_entities = [
        (key, ent_classes[key]) for key in custom_order if key in ent_classes
    ]

    return sorted_entities


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
