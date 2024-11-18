import logging
from django import template
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from apis_ontology.models import Place, PlaceIsLocatedWithinPlace
from apis_core.relations.templatetags.relations import relations_from

register = template.Library()

logger = logging.getLogger(__name__)


@register.simple_tag
def relations_from_place(
    from_obj, relation_type: ContentType = None, include_places_within=False
):

    def locations_contained_in(place_id):
        try:
            nested_places = [
                rel.subj_object_id
                for rel in set(
                    (PlaceIsLocatedWithinPlace.objects.filter(obj_object_id=place_id))
                )
            ]
            for p in nested_places:
                nested_places.extend(locations_contained_in(p))
        except Place.DoesNotExist:
            pass
        return nested_places

    rels = relations_from(from_obj, relation_type)
    if not include_places_within:
        return rels

    nested_locs = locations_contained_in(from_obj.pk)
    if not nested_locs:
        return rels

    nested_rels = []
    for nested_loc in nested_locs:
        try:
            nested_rels.extend(
                relations_from(Place.objects.get(pk=nested_loc), relation_type)
            )
        except Place.DoesNotExist:
            pass
    return [*rels, *nested_rels]
