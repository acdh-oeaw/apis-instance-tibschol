from apis_core.apis_entities.filtersets import AbstractEntityFilterSet
import django_filters
from apis_core.apis_entities.models import RootObject
from apis_core.relations.filtersets import RelationFilterSet
from apis_core.relations.models import Relation
from django.apps import apps
from django.db import models
from django_interval.fields import FuzzyDateParserField
from django_interval.filters import YearIntervalRangeFilter

from apis_ontology.forms import (
    PersonSearchForm,
    PlaceSearchForm,
    RelationSearchForm,
    WorkSearchForm,
    InstanceSearchForm,
)


ABSTRACT_ENTITY_FILTERS_EXCLUDE = [
    "start_date_sort",
    "start_date_from",
    "start_date_to",
    "end_date_sort",
    "end_date_from",
    "end_date_to",
]


def filter_related_property(queryset, name, value):
    rel_class = apps.get_model("apis_ontology", value)
    referenced_ids = rel_class.objects.values_list("subj", flat=True).union(
        rel_class.objects.values_list("obj", flat=True)
    )

    queryset = queryset.filter(pk__in=referenced_ids)
    return queryset


def filter_related_entity(queryset, name, value):
    queryset_pks = queryset.values_list("pk", flat=True)
    relations = Relation.objects.filter(
        models.Q(subj__pk__in=queryset_pks) | models.Q(obj__pk__in=queryset_pks)
    )

    related_entities_match_pks = []
    for r in relations:
        ent_id = r.subj.id
        rel_ent_id = r.obj.id
        if r.subj.id not in queryset_pks:
            ent_id = r.obj.id
            rel_ent_id = r.subj.id

        if ent_id in related_entities_match_pks:
            continue

        rel_ent = RootObject.objects_inheritance.get_subclass(pk=rel_ent_id)

        if (
            hasattr(rel_ent, "alternative_names")
            and rel_ent.alternative_names
            and value in rel_ent.alternative_names
        ):
            related_entities_match_pks.append(ent_id)
            continue

        if hasattr(rel_ent, "name") and value in rel_ent.name:
            related_entities_match_pks.append(ent_id)
            continue

        if hasattr(rel_ent, "label") and value in rel_ent.label:
            related_entities_match_pks.append(ent_id)
            continue

    queryset = queryset.filter(pk__in=related_entities_match_pks)

    return queryset


class LegacyStuffMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        exclude = ABSTRACT_ENTITY_FILTERS_EXCLUDE
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.pop("search", None)  # safely remove the search filter


class TibScholRelationMixinFilterSet(RelationFilterSet):
    class Meta(RelationFilterSet.Meta):
        form = RelationSearchForm
        exclude = RelationFilterSet.Meta.exclude + ABSTRACT_ENTITY_FILTERS_EXCLUDE
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            FuzzyDateParserField: {"filter_class": YearIntervalRangeFilter},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.pop("search", None)  # safely remove the search filter


class TibScholEntityMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            FuzzyDateParserField: {"filter_class": YearIntervalRangeFilter},
        }

    comments = django_filters.CharFilter(
        label="Comments contain", lookup_expr="icontains"
    )
    external_links = django_filters.CharFilter(
        label="External links contain", lookup_expr="icontains"
    )

    # related_entity = django_filters.CharFilter(
    #     label="Related entity", method=filter_related_entity
    # )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.pop("search", None)  # safely remove the search filter


class PlaceFilterSet(TibScholEntityMixinFilterSet):
    class Meta(TibScholEntityMixinFilterSet.Meta):
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "latitude",
            "longitude",
            "name",
            "feature_code",
        ]
        form = PlaceSearchForm

    label = django_filters.CharFilter(method="custom_name_search", label="Name or ID")
    # related_property = django_filters.ChoiceFilter(
    #     choices=get_relevant_relations(Place),
    #     label="Related Property",
    #     method=filter_related_property,
    # )

    def custom_name_search(self, queryset, name, value):
        name_query = models.Q(label__unaccent__icontains=value) | models.Q(
            alternative_names__unaccent__icontains=value
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class PersonFilterSet(TibScholEntityMixinFilterSet):
    class Meta(TibScholEntityMixinFilterSet.Meta):
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "alternative_names",
        ]
        form = PersonSearchForm

    name = django_filters.CharFilter(method="custom_name_search", label="Name or ID")
    # related_property = django_filters.ChoiceFilter(
    #     choices=get_relevant_relations(Person),
    #     label="Related Property",
    #     method=filter_related_property,
    # )

    def custom_name_search(self, queryset, name, value):
        name_query = models.Q(name__unaccent__icontains=value) | models.Q(
            alternative_names__unaccent__icontains=value
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class WorkFilterSet(TibScholEntityMixinFilterSet):
    class Meta(TibScholRelationMixinFilterSet.Meta):
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "alternative_names",
        ]

        form = WorkSearchForm

    name = django_filters.CharFilter(method="custom_name_search", label="Name or ID")
    # related_property = django_filters.ChoiceFilter(
    #     choices=get_relevant_relations(Work),
    #     label="Related Property",
    #     method=filter_related_property,
    # )

    def custom_name_search(self, queryset, name, value):
        name_query = models.Q(name__unaccent__icontains=value) | models.Q(
            alternative_names__unaccent__icontains=value
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class InstanceFilterSet(TibScholEntityMixinFilterSet):
    class Meta(TibScholEntityMixinFilterSet.Meta):
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "alternative_names",
        ]

        form = InstanceSearchForm

    name = django_filters.CharFilter(
        method="custom_name_search", label="Name or Tibschol reference or ID"
    )
    # related_property = django_filters.ChoiceFilter(
    #     choices=get_relevant_relations(Instance),
    #     label="Related Property",
    #     method=filter_related_property,
    # )

    def custom_name_search(self, queryset, name, value):
        name_query = (
            models.Q(name__unaccent__icontains=value)
            | models.Q(alternative_names__unaccent__icontains=value)
            | models.Q(tibschol_ref__icontains=value)
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class OtherModelsFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
            FuzzyDateParserField: {"filter_class": YearIntervalRangeFilter},
        }


class ExcerptsFilterSet(OtherModelsFilterSet):
    pass


class ZoteroEntryFilterSet(OtherModelsFilterSet):
    pass


class TopicFilterSet(OtherModelsFilterSet):
    pass
