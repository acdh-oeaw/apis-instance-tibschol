from django.apps import apps
import django_filters
from apis_core.apis_entities.filtersets import (
    ABSTRACT_ENTITY_FILTERS_EXCLUDE,
    AbstractEntityFilterSet,
)
from django.db import models

from apis_ontology.forms import PersonSearchForm, PlaceSearchForm, WorkSearchForm
from apis_ontology.models import Place
from apis_ontology.utils import get_relavent_relations

ABSTRACT_ENTITY_FILTERS_EXCLUDE = [
    f for f in ABSTRACT_ENTITY_FILTERS_EXCLUDE if f != "notes"
]


def filter_related_property(queryset, name, value):
    # Implement your filtering logic here based on the selected value
    rel_class = apps.get_model("apis_ontology", value)
    referenced_place_ids = rel_class.objects.values_list("subj", flat=True).union(
        rel_class.objects.values_list("obj", flat=True)
    )

    # Filter places based on the referenced primary keys
    queryset = queryset.filter(pk__in=referenced_place_ids)
    return queryset  # Return the original queryset if no filtering is required


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


class TibScholEntityMixinFilterSet(AbstractEntityFilterSet):
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

    comments = django_filters.CharFilter(
        label="Comments contain", lookup_expr="icontains"
    )
    external_links = django_filters.CharFilter(
        label="External links contain", lookup_expr="icontains"
    )

    related_entity = None


class PlaceFilterSet(TibScholEntityMixinFilterSet):
    class Meta:
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "latitude",
            "longitude",
            "notes",
            "name",
        ]
        form = PlaceSearchForm
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

    label = django_filters.CharFilter(method="custom_name_search")
    related_property = django_filters.ChoiceFilter(
        choices=get_relavent_relations(Place),
        label="Related Property",
        method=filter_related_property,
    )

    def custom_name_search(self, queryset, name, value):
        name_query = models.Q(label__icontains=value) | models.Q(
            alternative_names__icontains=value
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class PersonFilterSet(TibScholEntityMixinFilterSet):
    class Meta:
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "notes",
            "alternative_names",
        ]
        form = PersonSearchForm
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

    name = django_filters.CharFilter(method="custom_name_search")

    def custom_name_search(self, queryset, name, value):
        name_query = models.Q(name__icontains=value) | models.Q(
            alternative_names__icontains=value
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class WorkFilterSet(TibScholEntityMixinFilterSet):
    class Meta:
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "notes",
            "alternative_names",
        ]

        form = WorkSearchForm
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

    name = django_filters.CharFilter(method="custom_name_search", label="Name or ID")

    def custom_name_search(self, queryset, name, value):
        name_query = models.Q(name__icontains=value) | models.Q(
            alternative_names__icontains=value
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)


class InstanceFilterSet(TibScholEntityMixinFilterSet):
    class Meta:
        exclude = [
            *ABSTRACT_ENTITY_FILTERS_EXCLUDE,
            "notes",
            "alternative_names",
        ]

        form = WorkSearchForm
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

    name = django_filters.CharFilter(
        method="custom_name_search", label="Name or Tibschol reference or ID"
    )

    def custom_name_search(self, queryset, name, value):
        name_query = (
            models.Q(name__icontains=value)
            | models.Q(alternative_names__icontains=value)
            | models.Q(tibschol_ref__icontains=value)
        )
        if value.isdigit():
            name_query = name_query | models.Q(pk=int(value))

        return queryset.filter(name_query)
