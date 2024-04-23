from apis_core.apis_entities.filtersets import (
    AbstractEntityFilterSet,
    ABSTRACT_ENTITY_FILTERS_EXCLUDE,
)
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
        filter_overrides = {
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }


class InstanceMixinFilterSet(AbstractEntityFilterSet):
    class Meta(AbstractEntityFilterSet.Meta):
        filter_overrides = {
            models.TextField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }
