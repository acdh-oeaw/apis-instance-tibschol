from django import template
import logging
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from apis_core.relations.models import Relation
from apis_ontology.models import TibScholRelationMixin
from itertools import chain

from apis_ontology.tables import RelationsTable
from django.db.models.query import QuerySet
from django_tables2 import RequestConfig

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
def entity_relations(context, with_type):
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
            logger.debug("MATCH! %s", m)
            logger.debug(
                "%s - %s", ContentType.objects.get_for_model(m.subj_model), content_type
            )

            forward_relations.extend(m.objects.filter(subj=entity))
            logger.debug(m.objects.filter(subj=entity))

        if (
            ContentType.objects.get_for_model(m.obj_model) == content_type
            and ContentType.objects.get_for_model(m.subj_model) == with_type
        ):
            reverse_relations.extend(m.objects.filter(obj=entity))
            logger.debug(m.objects.filter(subj=entity))

        #     relations.append({"label": "name", "obj": m})
        # if (
        #     ContentType.objects.get_for_model(m.obj_model) == content_type
        #     and ContentType.objects.get_for_model(m.subj_model) == with_type
        # ):
        #     relations.append({"label": "reverse_name", "obj": m})
    table = RelationsTable(forward_relations, reverse_relations, "Relations")
    request = context["request"]
    RequestConfig(request, paginate=False).configure(
        table
    )  # Adjust pagination as needed

    return table.as_html(request)
