from django import template
import logging
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from apis_core.relations.models import Relation
from apis_ontology.models import TibScholRelationMixin
from itertools import chain

from apis_ontology.tables import RelationsTableEdit, RelationsTableView
from django.db.models.query import QuerySet
from django_tables2 import RequestConfig
from django_tables2.tables import table_factory
from apis_core.relations import utils

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def related_entity_types(context):
    entity = context["object"]
    content_type = ContentType.objects.get_for_model(entity)
    models = TibScholRelationMixin.__subclasses__()
    relavent_models = set()
    for m in models:
        if ContentType.objects.get_for_model(m.subj_model) == content_type:
            relavent_models.add(ContentType.objects.get_for_model(m.obj_model))

        if ContentType.objects.get_for_model(m.obj_model) == content_type:
            relavent_models.add(ContentType.objects.get_for_model(m.subj_model))

    logger.debug("RELAVENT MODELS: %s", relavent_models)
    return relavent_models


@register.simple_tag(takes_context=True)
def entity_relations(context, with_type, edit=False):
    entity = context["object"]
    content_type = ContentType.objects.get_for_model(entity)
    models = TibScholRelationMixin.__subclasses__()
    forward_relations = []
    reverse_relations = []
    for m in models:
        if (
            ContentType.objects.get_for_model(m.subj_model) == content_type
            and ContentType.objects.get_for_model(m.obj_model) == with_type
        ):
            forward_relations.extend(m.objects.filter(subj=entity))
            logger.debug(m.objects.filter(subj=entity))

        if (
            ContentType.objects.get_for_model(m.obj_model) == content_type
            and ContentType.objects.get_for_model(m.subj_model) == with_type
        ):
            reverse_relations.extend(m.objects.filter(obj=entity))
            logger.debug(m.objects.filter(subj=entity))

    if edit:
        table = RelationsTableEdit
    else:
        table = RelationsTableView

    return table(forward_relations + reverse_relations)


@register.inclusion_tag("templatetags/relations_links.html")
def relations_links(instance=None, tocontenttype=None, htmx=False):
    """
    Provide a list of links to relation views; If `instance` is passed,
    it only links to relations where an `instance` type can be part of.
    If `contenttype` is passed, it links only to relations that can occur
    between the `instance` contenttype and the `contentttype`.
    """
    tomodel = None
    if tocontenttype:
        tomodel = tocontenttype.model_class()

    frommodel = None
    instancect = None
    if instance:
        frommodel = type(instance)
        instancect = ContentType.objects.get_for_model(instance)

    return {
        "relation_types": [
            (ct, ct.model_class())
            for ct in utils.relation_content_types(combination=(frommodel, tomodel))
        ],
        "relation_types_reverse": utils.relation_content_types(
            subj_model=tomodel, obj_model=frommodel
        ),
        "instance": instance,
        "instancect": instancect,
        "contenttype": tocontenttype,
        "htmx": htmx,
    }
