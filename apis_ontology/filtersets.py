from apis_core.apis_entities.filtersets import (
    AbstractEntityFilterSet,
    ABSTRACT_ENTITY_FILTERS_EXCLUDE,
)
from apis_ontology.forms import PersonSearchForm, PlaceSearchForm
from django.db import models
import django_filters

ABSTRACT_ENTITY_FILTERS_EXCLUDE = [
    f for f in ABSTRACT_ENTITY_FILTERS_EXCLUDE if f != "notes"
]


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
    alternative_names = django_filters.CharFilter(
        label="Alternative names contain", lookup_expr="icontains"
    )


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

    def custom_name_search(self, queryset, name, value):
        return queryset.filter(
            models.Q(label__icontains=value)
            | models.Q(alternative_names__icontains=value)
        )


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
        return queryset.filter(
            models.Q(name__icontains=value)
            | models.Q(alternative_names__icontains=value)
        )
